from datetime import datetime
from flask_login import UserMixin
from core import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class DetectionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    class_name = db.Column(db.String(50), nullable=False) # 'Helmet' or 'No Helmet'
    snapshot_path = db.Column(db.String(255), nullable=True) # relative path to static/snapshots/

class CameraSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rtsp_url = db.Column(db.String(255), nullable=False, default='0')
    roi_coordinates = db.Column(db.Text, nullable=True) # JSON array of {x, y}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
