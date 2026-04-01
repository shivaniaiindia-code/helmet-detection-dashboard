from flask import Blueprint, render_template, request, flash, redirect, url_for, Response
from flask_login import login_required
from core.models import CameraSetting
from core import db
import json
from core.routes.stream import get_engine

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def config():
    setting = CameraSetting.query.first()
    if not setting:
        setting = CameraSetting(rtsp_url='0')
        db.session.add(setting)
        db.session.commit()
        
    if request.method == 'POST':
        rtsp_url = request.form.get('rtsp_url')
        roi_data = request.form.get('roi_data')
        
        if rtsp_url:
            setting.rtsp_url = rtsp_url
            
        if roi_data:
            try:
                parsed = json.loads(roi_data)
                if isinstance(parsed, list):
                    setting.roi_coordinates = roi_data
                else:
                    setting.roi_coordinates = "[]"
            except:
                pass
        elif 'reset_roi' in request.form:
            setting.roi_coordinates = "[]"
            
        db.session.commit()
        
        engine = get_engine()
        engine.load_config()
        
        flash('Settings updated successfully', 'success')
        return redirect(url_for('settings.config'))
        
    roi_json = setting.roi_coordinates if setting.roi_coordinates else "[]"
    return render_template('settings.html', setting=setting, roi_json=roi_json)

@settings_bp.route('/api/reference_frame')
@login_required
def reference_frame():
    engine = get_engine()
    frame_bytes = engine.get_raw_frame_for_roi()
    if frame_bytes:
        return Response(frame_bytes, mimetype='image/jpeg')
    return Response("No frame available", status=404)
