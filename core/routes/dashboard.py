from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from core.detection import DetectionEngine
from core.models import DetectionLog

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    recent_logs = DetectionLog.query.order_by(DetectionLog.timestamp.desc()).limit(5).all()
    return render_template('dashboard.html', recent_logs=recent_logs)

@dashboard_bp.route('/api/live_stats')
@login_required
def live_stats():
    # Return the current counts tracked globally by the VideoCamera class
    return jsonify({
        'helmet_count': DetectionEngine.current_helmet_count,
        'no_helmet_count': DetectionEngine.current_no_helmet_count
    })
