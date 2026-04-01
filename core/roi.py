import cv2
import numpy as np

def mask_frame(frame, polygon_data):
    """
    Masks the area outside the ROI (blacks it out).
    polygon_data: List of dicts [{'x': float, 'y': float}, ...] where x,y are 0-1 normalized
    """
    if frame is None or not polygon_data or len(polygon_data) < 3:
        return frame

    h, w = frame.shape[:2]
    
    # Convert normalized coordinates to pixel coordinates
    points = []
    for p in polygon_data:
        points.append([int(p['x'] * w), int(p['y'] * h)])
    
    pts = np.array(points, np.int32)
    pts = pts.reshape((-1, 1, 2))

    # Create a black mask
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    
    # Draw a filled white polygon on the mask mapping the allowed ROI
    cv2.fillPoly(mask, [pts], 255)
    
    # Bitwise AND to keep only the ROI
    masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
    return masked_frame

def draw_roi_overlay(frame, polygon_data, color=(0, 255, 255), thickness=2):
    """Draws the ROI path directly on a frame."""
    if frame is None or not polygon_data or len(polygon_data) < 3:
        return frame
        
    h, w = frame.shape[:2]
    points = []
    for p in polygon_data:
        points.append([int(p['x'] * w), int(p['y'] * h)])
        
    pts = np.array(points, np.int32)
    pts = pts.reshape((-1, 1, 2))
    
    # Draw polygon overlay
    cv2.polylines(frame, [pts], isClosed=True, color=color, thickness=thickness)
    return frame

def crop_violation(frame, bbox):
    """
    Extracts the bounding box from the frame correctly, with some padding.
    bbox: [x1, y1, x2, y2]
    """
    h, w = frame.shape[:2]
    x1, y1, x2, y2 = bbox
    
    p = 30 # padding
    x1 = max(0, x1 - p)
    y1 = max(0, y1 - p)
    x2 = min(w, x2 + p)
    y2 = min(h, y2 + p)
    
    return frame[y1:y2, x1:x2]
