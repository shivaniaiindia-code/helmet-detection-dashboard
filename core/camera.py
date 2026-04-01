import cv2
import threading
import time

class CameraStream:
    def __init__(self, source):
        self.source = source
        if isinstance(self.source, str) and self.source.isdigit():
            self.source = int(self.source)
            
        self.video = cv2.VideoCapture(self.source)
        self.frame = None
        self.is_running = True
        self.lock = threading.Lock()
        
        # Start a thread to read frames continuously (avoids buffer lag and handles reconnects)
        self.thread = threading.Thread(target=self._update_frames, daemon=True)
        self.thread.start()

    def _update_frames(self):
        while self.is_running:
            success, frame = self.video.read()
            if not success:
                # Reconnect logic
                self.video.release()
                time.sleep(1) # wait before reconnecting
                self.video = cv2.VideoCapture(self.source)
                continue
                
            with self.lock:
                self.frame = frame

    def get_frame(self):
        with self.lock:
            if self.frame is None:
                return None
            return self.frame.copy()
            
    def stop(self):
        self.is_running = False
        self.thread.join(timeout=2)
        if hasattr(self, 'video') and self.video.isOpened():
            self.video.release()
