"""
Flask Dashboard for Multi-Location Pest Monitoring
Web interface to view all cameras, detections, and statistics
"""
from flask import Flask, render_template, jsonify, request, send_from_directory
from pathlib import Path
import json
from datetime import datetime, timedelta

# Import modules
from modules.data_logger import DataLogger
from modules.pest_detector import PestDetector
from modules.alert_system import AlertSystem
from modules.scheduler import PestMonitorScheduler

app = Flask(__name__)

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

# Initialize components
data_logger = DataLogger('config.json')
detector = PestDetector('config.json')
scheduler = None  # Will be initialized if needed

# Routes

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/cameras')
def get_cameras():
    """Get all registered cameras"""
    cameras = data_logger.get_all_cameras()
    return jsonify(cameras)

@app.route('/api/detections/recent')
def get_recent_detections():
    """Get recent detections"""
    camera_id = request.args.get('camera_id')
    hours = int(request.args.get('hours', 24))
    limit = int(request.args.get('limit', 50))

    detections = data_logger.get_recent_detections(
        camera_id=camera_id,
        hours=hours,
        limit=limit
    )

    return jsonify(detections)

@app.route('/api/statistics')
def get_statistics():
    """Get summary statistics"""
    camera_id = request.args.get('camera_id')
    days = int(request.args.get('days', 7))

    stats = data_logger.get_statistics(camera_id=camera_id, days=days)
    return jsonify(stats)

@app.route('/api/trends')
def get_trends():
    """Get trend analysis data"""
    camera_id = request.args.get('camera_id')
    days = int(request.args.get('days', 7))

    trends = data_logger.get_trend_analysis(camera_id=camera_id, days=days)
    return jsonify(trends)

@app.route('/api/alerts/pending')
def get_pending_alerts():
    """Get pending alerts"""
    alerts = data_logger.get_pending_alerts()
    return jsonify(alerts)

@app.route('/api/heatmap')
def get_heatmap_data():
    """Get data for pest activity heatmap"""
    cameras = data_logger.get_all_cameras()
    heatmap_data = []

    for camera in cameras:
        stats = data_logger.get_statistics(camera_id=camera['camera_id'], days=1)

        if stats and stats['total_pests']:
            heatmap_data.append({
                'camera_id': camera['camera_id'],
                'location_name': camera['location_name'],
                'latitude': camera['latitude'],
                'longitude': camera['longitude'],
                'pest_count': stats['total_pests'],
                'intensity': min(stats['total_pests'] / 10, 1.0)  # Normalized 0-1
            })

    return jsonify(heatmap_data)

@app.route('/api/manual-capture', methods=['POST'])
def trigger_manual_capture():
    """Trigger manual capture and analysis"""
    global scheduler

    try:
        if scheduler is None:
            scheduler = PestMonitorScheduler('config.json')

        result = scheduler.run_manual_cycle()

        if result:
            return jsonify({
                'success': True,
                'result': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Capture/analysis failed'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """Upload and analyze an image manually"""
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'}), 400

    file = request.files['image']
    camera_id = request.form.get('camera_id', 'MANUAL_UPLOAD')

    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    try:
        # Save uploaded file
        upload_path = Path('data/images') / f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        file.save(str(upload_path))

        # Detect pests
        metadata = {
            'camera_id': camera_id,
            'location': {'name': 'Manual Upload'},
            'timestamp': datetime.now().isoformat()
        }

        result = detector.detect_pests(str(upload_path), metadata)

        # Log result
        data_logger.log_detection(result)

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve detection images"""
    return send_from_directory('data/images', filename)

@app.route('/api/status')
def get_status():
    """Get system status"""
    if scheduler:
        status = scheduler.get_status()
    else:
        status = {
            'running': False,
            'message': 'Scheduler not started'
        }

    return jsonify(status)

# Error handlers

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Main execution

if __name__ == '__main__':
    print("""
===========================================================

       EcoBloom Pest Detection Dashboard

  Multi-Location Farm Monitoring System
  Powered by Computer Vision & IoT

===========================================================
    """)

    host = config['dashboard']['host']
    port = config['dashboard']['port']

    print(f"\n🚀 Starting dashboard server...")
    print(f"📍 Access at: http://{host}:{port}")
    print(f"🌐 Network access enabled (connect from any device on your network)")
    print(f"\n🛑 Press Ctrl+C to stop\n")

    app.run(
        host=host,
        port=port,
        debug=True
    )
