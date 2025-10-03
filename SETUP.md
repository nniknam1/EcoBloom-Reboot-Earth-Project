# 🌱 EcoBloom Pest Detection - Setup Guide

## Overview
Advanced IoT pest detection system for farmers using Raspberry Pi cameras and computer vision.

## Features
- ✅ Multi-location camera trap monitoring
- ✅ Automated time-lapse capture & analysis
- ✅ Real-time pest counting with adaptive thresholds
- ✅ SQLite database for historical tracking
- ✅ Email/SMS/MQTT alerts for high pest activity
- ✅ Web dashboard for multi-farm visualization
- ✅ Trend analysis and risk assessment
- ✅ Batch image processing
- ✅ Offline-capable with cloud sync

## Hardware Requirements

### Raspberry Pi Setup
- **Raspberry Pi 4** (recommended) or Pi 3B+
- **Pi Camera Module** (v2, v3, or HQ Camera)
- **MicroSD Card** (32GB+ recommended)
- **Power Supply** (5V, 3A for Pi 4)
- **Optional**: Solar panel + battery for remote deployment

### For Demo/Testing
- Any computer with webcam
- Or use pre-captured images

## Software Installation

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Raspberry Pi Camera Setup
For **Pi Camera Module 3** (newer):
```bash
sudo apt update
sudo apt install -y python3-picamera2
```

For **older Pi Camera modules**:
```bash
sudo apt install -y python3-picamera
```

Enable camera interface:
```bash
sudo raspi-config
# Navigate to: Interface Options -> Camera -> Enable
```

### 3. Optional: Alert Services
**For SMS alerts** (Twilio):
```bash
pip install twilio
```

**For MQTT** (IoT integration):
```bash
pip install paho-mqtt
```

## Configuration

### Edit `config.json`

```json
{
  "camera": {
    "camera_id": "CAM001",          // Unique ID for this camera
    "location": {
      "name": "North Field - Zone A",  // Field location
      "latitude": 40.7128,              // GPS coordinates
      "longitude": -74.0060
    },
    "capture_interval_minutes": 60,    // How often to capture
    "auto_start": true
  },

  "detection": {
    "min_pest_area": 20,              // Min pixel area for detection
    "max_pest_area": 5000,            // Max pixel area
    "risk_thresholds": {
      "low": 2,                       // <= 2 pests = LOW
      "medium": 5,                    // <= 5 pests = MEDIUM
      "high": 10                      // > 5 pests = HIGH
    },
    "adaptive_threshold": true        // Auto-adjust for lighting
  },

  "alerts": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "sender_email": "your_email@gmail.com",
      "sender_password": "your_app_password",  // Use App Password for Gmail
      "recipient_email": "farmer@example.com"
    },
    "sms": {
      "enabled": false,               // Set to true after configuring Twilio
      "twilio_account_sid": "...",
      "twilio_auth_token": "...",
      "twilio_phone": "+1234567890",
      "recipient_phone": "+1234567890"
    }
  }
}
```

### Gmail Setup for Alerts
1. Enable 2-factor authentication on your Google account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the generated password in `config.json`

## Usage

### Quick Start
```bash
# Launch web dashboard
python main.py --dashboard

# Access at: http://localhost:5000
# From other devices: http://[PI_IP_ADDRESS]:5000
```

### Automated Monitoring (Recommended for Production)
```bash
# Start automated scheduler
python main.py --scheduler

# Captures images every X minutes (set in config.json)
# Detects pests automatically
# Sends alerts when risk is HIGH
# Logs all data to database
```

### Manual Operations
```bash
# Trigger single camera capture
python main.py --capture

# Analyze existing image
python main.py --analyze sticky_trap.jpg

# Batch analyze folder
python main.py --batch ./trap_images/

# View statistics
python main.py --stats --days 7

# Test email/SMS alerts
python main.py --test-alerts
```

## Running on Startup (Raspberry Pi)

### Auto-start scheduler on boot
```bash
# Edit crontab
crontab -e

# Add this line:
@reboot sleep 30 && cd /home/pi/EcoBloom-Reboot-Earth-Project && python3 main.py --scheduler >> /home/pi/ecobloom.log 2>&1
```

### Or use systemd service
Create `/etc/systemd/system/ecobloom.service`:
```ini
[Unit]
Description=EcoBloom Pest Detection
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/EcoBloom-Reboot-Earth-Project
ExecStart=/usr/bin/python3 main.py --scheduler
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl enable ecobloom.service
sudo systemctl start ecobloom.service
```

## Multi-Camera Setup

### Deploy multiple Raspberry Pis across farm
Each Pi should have:
1. Unique `camera_id` in `config.json`
2. Different `location.name` (e.g., "East Field", "Greenhouse B")
3. GPS coordinates set correctly

### Central Dashboard
All Pis send data to the same database (future: cloud sync)

## Weatherproof Enclosure
For outdoor deployment:
- Use IP67-rated case for Raspberry Pi
- Position camera to view sticky trap clearly
- Ensure adequate ventilation
- Optional: solar panel for power

## Demo Tips for Hackathon

### 1. Use Sample Images
Place test images in `data/images/` folder and run:
```bash
python main.py --batch data/images/
```

### 2. Show Web Dashboard
- Run `python main.py --dashboard`
- Upload images via web interface
- Show real-time detection results
- Display statistics and trends

### 3. Multi-Location Demo
- Modify `config.json` to create multiple "virtual cameras"
- Upload different images with different camera IDs
- Show farm-wide heatmap on dashboard

### 4. Alert Demo
- Configure email alerts
- Upload image with high pest count
- Show live email notification

## Troubleshooting

### Camera not detected
```bash
# Test camera
libcamera-hello

# If using USB webcam instead
# The system will automatically detect and use cv2.VideoCapture
```

### Import errors
```bash
# Ensure all dependencies installed
pip install -r requirements.txt

# Check Python version (3.8+ required)
python --version
```

### Database errors
```bash
# Database is auto-created
# If corrupted, delete and restart:
rm data/pest_data.db
python main.py --capture
```

## Scaling Up

### For Large Farms
1. Deploy multiple Raspberry Pi cameras across zones
2. Use MQTT to send data to central server
3. Run dashboard on main server
4. Set different risk thresholds per crop type
5. Enable SMS alerts for critical zones only

### Cloud Integration (Future)
- Upload images to AWS S3/Google Cloud
- Use cloud database (PostgreSQL)
- Train custom ML models on historical data

## Support
For issues, check logs:
```bash
# View recent logs
tail -f /home/pi/ecobloom.log

# Check database
python main.py --stats
```

## Credits
Built for **Reboot Earth Hackathon 2025**
Powered by OpenCV, Flask, and Raspberry Pi
