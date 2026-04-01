from flask import Blueprint, Response, current_app
from flask_login import login_required
from core.detection import DetectionEngine

stream_bp = Blueprint('stream', __name__)

engine_instance = None

def get_engine():
    global engine_instance
    if engine_instance is None:
        engine_instance = DetectionEngine(app=current_app._get_current_object())
    return engine_instance

def gen(engine):
    while True:
        frame = engine.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@stream_bp.route('/video_feed')
@login_required
def video_feed():
    return Response(gen(get_engine()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
