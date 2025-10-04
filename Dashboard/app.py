from flask import Flask, send_from_directory, render_template_string, jsonify
import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
P2P_DIR = BASE_DIR / 'P2P-System'
PEST_DIR = BASE_DIR / 'Pest-detection'
HEAT_DIR = BASE_DIR / 'heat_risk'

app = Flask(__name__, static_folder=str(Path(__file__).resolve().parent))

# Serve the main dashboard (the Dashboard/dashboard.html)
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'dashboard.html')

# Serve P2P dashboard
@app.route('/p2p')
def p2p():
    return send_from_directory(str(P2P_DIR), 'dashboard.html')

# Serve pest detection page
@app.route('/pest')
def pest():
    return send_from_directory(str(PEST_DIR), 'pest_detection.html')

# Serve heat stress page
@app.route('/heat')
def heat():
    return send_from_directory(str(HEAT_DIR), 'heat_stress_detection.html')

# Static file passthrough for each folder (js/css/images inside folders)
@app.route('/p2p/<path:filename>')
def p2p_static(filename):
    return send_from_directory(str(P2P_DIR), filename)

@app.route('/pest/<path:filename>')
def pest_static(filename):
    return send_from_directory(str(PEST_DIR), filename)

@app.route('/heat/<path:filename>')
def heat_static(filename):
    return send_from_directory(str(HEAT_DIR), filename)

# Simple summary endpoint aggregating some local info
@app.route('/api/summary')
def summary():
    # Count peer id files
    ids_dir = P2P_DIR / 'ids'
    connected = 0
    if ids_dir.exists():
        connected = len(list(ids_dir.glob('*.id')))

    # Count alert logs (farm_*.log)
    logs = list(P2P_DIR.glob('*.log'))
    alerts = 0
    for log in logs:
        try:
            with open(log, 'r', encoding='utf-8') as f:
                data = f.read()
                alerts += data.count('ALERT')
        except Exception:
            pass

    # Read pest detection sample if exists
    pests = {}
    pest_file = PEST_DIR / 'pest_detection.html'
    if pest_file.exists():
        pests['sample_page'] = str(pest_file.name)

    return jsonify({
        'connected_peers': connected,
        'alert_mentions': alerts,
        'pest_page': pests
    })

if __name__ == '__main__':
    app.run(debug=True, port=8080)
