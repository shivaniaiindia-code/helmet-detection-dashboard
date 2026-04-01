from flask import Blueprint, render_template, request, make_response
from flask_login import login_required
from core.models import DetectionLog
import pandas as pd
from datetime import datetime

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/logs')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    class_filter = request.args.get('class_filter', 'All')
    
    query = DetectionLog.query
    if class_filter != 'All':
        query = query.filter_by(class_name=class_filter)
        
    logs = query.order_by(DetectionLog.timestamp.desc()).paginate(page=page, per_page=10)
    
    return render_template('logs.html', logs=logs, current_filter=class_filter)

@logs_bp.route('/logs/export')
@login_required
def export_csv():
    logs = DetectionLog.query.order_by(DetectionLog.timestamp.desc()).all()
    
    data = []
    for log in logs:
        data.append({
            'ID': log.id,
            'Timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Class': log.class_name,
            'Snapshot': log.snapshot_path or 'N/A'
        })
        
    df = pd.DataFrame(data)
    csv_data = df.to_csv(index=False)
    
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = f"attachment; filename=detection_logs_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response
