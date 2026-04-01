from core.camera import CameraStream
from core.roi import mask_frame, draw_roi_overlay, crop_violation
from core.models import CameraSetting, DetectionLog
from core import db
from ultralytics import YOLO
from datetime import datetime
import cv2
import os
import json
import threading

class DetectionEngine:
    current_helmet_count = 0
    current_no_helmet_count = 0
    
    def __init__(self, app):
        self.app = app
        self.stream = None
        self.model = YOLO('best.pt') 
        self.last_log_time = datetime.min
        self.log_cooldown_seconds = 5.0
        
        # Load configs
        self.load_config()
        self.lock = threading.Lock()
        
    def load_config(self):
        with self.app.app_context():
            setting = CameraSetting.query.first()
            if not setting:
                setting = CameraSetting(rtsp_url='0')
                db.session.add(setting)
                db.session.commit()
            
            source = setting.rtsp_url
            if hasattr(self, 'source') and self.source == source and self.stream is not None:
                pass
            else:
                self.source = source
                if self.stream is not None:
                    self.stream.stop()
                self.stream = CameraStream(self.source)
                
            self.roi_data = []
            if setting.roi_coordinates:
                try:
                    self.roi_data = json.loads(setting.roi_coordinates)
                except:
                    self.roi_data = []

    def get_frame(self):
        raw_frame = self.stream.get_frame()
        if raw_frame is None:
            return None
            
        # Mask the frame based on ROI
        masked_frame = mask_frame(raw_frame.copy(), self.roi_data)
        
        # Inference on masked frame
        results = self.model(masked_frame, stream=True, verbose=False)
        
        helmet_count = 0
        no_helmet_count = 0
        found_no_helmet = False
        no_helmet_frame = None
        no_helmet_bbox = None
        
        display_frame = raw_frame.copy()
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = box.conf[0]
                cls = int(box.cls[0])
                class_name = self.model.names.get(cls, "Unknown")
                
                # Mock logic with Yolov8n
                if class_name == 'person':
                    class_name = 'No Helmet'
                
                label = ""
                color = (0, 255, 0)
                
                if class_name.lower() == 'helmet':
                    helmet_count += 1
                    label = f"Helmet {conf:.2f}"
                    color = (0, 255, 0)
                elif class_name.lower() == 'no helmet':
                    no_helmet_count += 1
                    label = f"No Helmet {conf:.2f}"
                    color = (0, 0, 255)
                    found_no_helmet = True
                    no_helmet_frame = raw_frame.copy() 
                    no_helmet_bbox = [x1, y1, x2, y2]
                else:
                    continue
                
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(display_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
        # Draw ROI overlay on display frame
        display_frame = draw_roi_overlay(display_frame, self.roi_data)

        # Logging Logic to DB
        now = datetime.utcnow()
        if found_no_helmet and (now - self.last_log_time).total_seconds() > self.log_cooldown_seconds:
            self.last_log_time = now
            timestamp_str = now.strftime("%Y%m%d_%H%M%S")
            snapshot_filename = f"snapshot_{timestamp_str}.jpg"
            
            # Crop just the offender
            crop_img = crop_violation(no_helmet_frame, no_helmet_bbox)
            
            # Optionally draw box on crop for better visibility
            # we need local coordinates of the crop
            if crop_img is not None and crop_img.shape[0] > 0 and crop_img.shape[1] > 0:
                c_h, c_w = crop_img.shape[:2]
                cv2.rectangle(crop_img, (0, 0), (c_w-1, c_h-1), (0, 0, 255), 2)
                cv2.putText(crop_img, "No Helmet", (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            snapshot_path = os.path.join(self.app.root_path, 'static', 'snapshots', snapshot_filename)
            if crop_img is not None and crop_img.shape[0] > 0 and crop_img.shape[1] > 0:
                cv2.imwrite(snapshot_path, crop_img)
            else:
                cv2.imwrite(snapshot_path, display_frame) # Fallback
            
            with self.app.app_context():
                new_log = DetectionLog(class_name='No Helmet', snapshot_path=snapshot_filename)
                db.session.add(new_log)
                db.session.commit()

        # Update global state for Dashboard API
        DetectionEngine.current_helmet_count = helmet_count
        DetectionEngine.current_no_helmet_count = no_helmet_count

        # Encode to MJPEG
        ret, jpeg = cv2.imencode('.jpg', display_frame)
        return jpeg.tobytes()
        
    def get_raw_frame_for_roi(self):
        """Returns a snapshot of the raw stream to draw ROI on"""
        frame = self.stream.get_frame()
        if frame is not None:
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()
        return None
