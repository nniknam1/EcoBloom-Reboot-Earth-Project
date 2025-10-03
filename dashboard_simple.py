"""
Simple Flask Dashboard - No Emoji Issues
"""
from flask import Flask, render_template, jsonify, request, send_from_directory
from pathlib import Path
import json
import sqlite3
from datetime import datetime, timedelta
import cv2
import numpy as np
from PIL import Image
import os

app = Flask(__name__)

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

DB_PATH = Path(config['storage']['local_db_path'])
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Initialize database if needed
def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            camera_id TEXT NOT NULL,
            location_name TEXT,
            latitude REAL,
            longitude REAL,
            pest_count INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            image_path TEXT,
            output_path TEXT,
            detection_params TEXT,
            pest_details TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS camera_status (
            camera_id TEXT PRIMARY KEY,
            location_name TEXT,
            latitude REAL,
            longitude REAL,
            last_capture TEXT,
            total_captures INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active'
        )
    ''')

    conn.commit()
    conn.close()

init_db()

def detect_pests_simple(image_path):
    """Simple detection without module dependencies"""
    ext = os.path.splitext(image_path)[1].lower()

    if ext == '.webp':
        pil_image = Image.open(image_path)
        img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    else:
        img = cv2.imread(image_path)

    if img is None:
        return None

    original = img.copy()
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Detect dark objects
    lower_dark = np.array([0, 0, 0])
    upper_dark = np.array([180, 255, 100])
    mask = cv2.inRange(hsv, lower_dark, upper_dark)

    # Remove noise
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter by size
    min_area, max_area = 20, 5000
    valid_pests = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if min_area < area < max_area:
            valid_pests.append(contour)
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            cv2.circle(img, center, radius, (0, 255, 0), 2)

    pest_count = len(valid_pests)

    # Risk level
    if pest_count <= 2:
        risk = "LOW"
        color = (0, 255, 0)
    elif pest_count <= 5:
        risk = "MEDIUM"
        color = (0, 165, 255)
    else:
        risk = "HIGH"
        color = (0, 0, 255)

    cv2.putText(img, f"Detected: {pest_count} insects | Risk: {risk}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    # Save result
    base_name = os.path.splitext(image_path)[0]
    ext = os.path.splitext(image_path)[1]
    output_path = f"{base_name}_detected{ext}"
    cv2.imwrite(output_path, img)

    return {
        'timestamp': datetime.now().isoformat(),
        'pest_count': pest_count,
        'risk_level': risk,
        'image_path': image_path,
        'output_path': output_path
    }

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/cameras')
def get_cameras():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM camera_status')

    cameras = []
    for row in cursor.fetchall():
        cameras.append({
            'camera_id': row[0],
            'location_name': row[1],
            'latitude': row[2],
            'longitude': row[3],
            'last_capture': row[4],
            'total_captures': row[5],
            'status': row[6]
        })

    conn.close()
    return jsonify(cameras)

@app.route('/api/detections/recent')
def get_recent_detections():
    hours = int(request.args.get('hours', 24))
    limit = int(request.args.get('limit', 50))

    cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM detections
        WHERE timestamp > ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (cutoff, limit))

    detections = []
    for row in cursor.fetchall():
        detections.append({
            'id': row[0],
            'timestamp': row[1],
            'camera_id': row[2],
            'location_name': row[3],
            'pest_count': row[6],
            'risk_level': row[7],
            'image_path': row[8],
            'output_path': row[9]
        })

    conn.close()
    return jsonify(detections)

@app.route('/api/statistics')
def get_statistics():
    days = int(request.args.get('days', 7))
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            COUNT(*) as total_captures,
            SUM(pest_count) as total_pests,
            AVG(pest_count) as avg_pests,
            MAX(pest_count) as max_pests,
            MIN(pest_count) as min_pests
        FROM detections
        WHERE timestamp > ?
    ''', (cutoff,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({
            'total_captures': row[0] or 0,
            'total_pests': row[1] or 0,
            'avg_pests': row[2] or 0,
            'max_pests': row[3] or 0,
            'min_pests': row[4] or 0
        })

    return jsonify({
        'total_captures': 0,
        'total_pests': 0,
        'avg_pests': 0,
        'max_pests': 0,
        'min_pests': 0
    })

@app.route('/api/trends')
def get_trends():
    days = int(request.args.get('days', 7))
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            DATE(timestamp) as date,
            COUNT(*) as captures,
            SUM(pest_count) as total_pests,
            AVG(pest_count) as avg_pests
        FROM detections
        WHERE timestamp > ?
        GROUP BY DATE(timestamp)
        ORDER BY date
    ''', (cutoff,))

    trends = []
    for row in cursor.fetchall():
        trends.append({
            'date': row[0],
            'captures': row[1],
            'total_pests': row[2] or 0,
            'avg_pests': row[3] or 0
        })

    conn.close()
    return jsonify(trends)

@app.route('/api/alerts/pending')
def get_alerts():
    return jsonify([])  # Simplified for now

@app.route('/api/heatmap')
def get_heatmap():
    return jsonify([])  # Simplified for now

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
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
        result = detect_pests_simple(str(upload_path))

        if result:
            result['camera_id'] = camera_id
            result['location_name'] = 'Manual Upload'

            # Log to database
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO detections (
                    timestamp, camera_id, location_name, latitude, longitude,
                    pest_count, risk_level, image_path, output_path,
                    detection_params, pest_details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result['timestamp'], camera_id, 'Manual Upload', 0.0, 0.0,
                result['pest_count'], result['risk_level'],
                result['image_path'], result['output_path'], '{}', '[]'
            ))
            conn.commit()
            conn.close()

            return jsonify({'success': True, 'result': result})
        else:
            return jsonify({'success': False, 'error': 'Detection failed'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('data/images', filename)

@app.route('/api/status')
def get_status():
    return jsonify({'running': True, 'message': 'Dashboard active'})

if __name__ == '__main__':
    print("="*60)
    print("    EcoBloom Pest Detection Dashboard")
    print("="*60)
    print()
    print("[*] Starting Flask server...")
    print("[*] Access at: http://localhost:5000")
    print("[*] Press Ctrl+C to stop")
    print()

    host = config['dashboard']['host']
    port = config['dashboard']['port']

    app.run(host=host, port=port, debug=False)
