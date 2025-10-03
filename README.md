# 🌱 EcoBloom - Smart Pest Detection for Farmers

**Multi-Location IoT Pest Monitoring System**
*Built for Reboot Earth Hackathon 2025*

---

## 🎯 Problem
Farmers waste time manually checking sticky traps across large fields, leading to delayed pest control and crop damage.

## 💡 Solution
Automated camera trap system using Raspberry Pi that:
- 📸 Captures images of sticky traps automatically
- 🤖 Detects and counts pests using computer vision
- 📊 Tracks pest trends across multiple farm locations
- 🚨 Sends instant alerts when pest levels spike
- 🗺️ Provides web dashboard for farm-wide monitoring

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Your Camera
Edit `config.json` with your camera location and settings.

### 3. Run the Dashboard
```bash
python main.py --dashboard
```
Access at: **http://localhost:5000**

### 4. Start Automated Monitoring
```bash
python main.py --scheduler
```

---

## 🎥 Demo Features

### For Hackathon Judges:
1. **Web Dashboard** - Visual interface showing all locations
2. **Manual Upload** - Upload sticky trap photos instantly
3. **Multi-Location Support** - Track pests across entire farm
4. **Real-time Alerts** - Email/SMS when pests spike
5. **Trend Analysis** - Historical pest data visualization
6. **Batch Processing** - Analyze multiple traps at once

---

## 🏗️ System Architecture

```
Raspberry Pi Camera Traps (Field Deployment)
    ↓
Automated Image Capture (Hourly/Daily)
    ↓
Computer Vision Detection (OpenCV)
    ↓
SQLite Database (Local Storage)
    ↓
Alert System (Email/SMS/MQTT)
    ↓
Web Dashboard (Flask) - Multi-Farm View
```

---

## 📁 Project Structure

```
EcoBloom-Reboot-Earth-Project/
├── main.py                 # Main CLI interface
├── dashboard.py            # Web dashboard server
├── config.json             # Configuration file
├── modules/
│   ├── camera_capture.py   # Pi Camera integration
│   ├── pest_detector.py    # Computer vision detection
│   ├── data_logger.py      # Database management
│   ├── alert_system.py     # Email/SMS/MQTT alerts
│   └── scheduler.py        # Automated scheduling
├── templates/
│   └── dashboard.html      # Web interface
├── data/                   # Database & images
└── Sticky Trap.py          # Original detection code
```

---

## 🚀 Features

### ✅ Multi-Location Management
- GPS/location tagging for each camera
- Farm zone mapping (North Field, Greenhouse A, etc.)
- Batch processing across multiple traps
- Historical tracking per location

### ✅ Smart Detection
- Adaptive thresholds for varying lighting
- Pest size classification
- Confidence scoring
- Risk level assessment (LOW/MEDIUM/HIGH)

### ✅ Automated Alerts
- Email notifications for high pest activity
- SMS alerts via Twilio (optional)
- MQTT integration for IoT platforms
- Daily summary reports

### ✅ Farmer-Friendly Interface
- Web dashboard accessible from any device
- Manual image upload option
- Statistics and trend charts
- Export data to CSV

### ✅ Scalable Architecture
- Support for unlimited cameras
- Offline-capable with sync
- Works with Pi Camera or USB webcam
- Weatherproof deployment ready

---

## 📊 Use Cases

1. **Small Farms** - Deploy 2-3 cameras in key zones
2. **Large Operations** - Monitor 10+ locations across property
3. **Greenhouses** - Indoor pest monitoring with controlled lighting
4. **Research** - Collect data on pest populations over time
5. **Cooperative Farms** - Multi-farm dashboard view

---

## 🛠️ Technology Stack

- **Computer Vision**: OpenCV, NumPy
- **Hardware**: Raspberry Pi 4, Pi Camera Module
- **Backend**: Python, Flask, SQLite
- **Alerts**: SMTP (email), Twilio (SMS), MQTT
- **Frontend**: HTML/CSS/JavaScript
- **Scheduling**: Python `schedule` library

---

## 📱 Demo Instructions

### For Live Demo:
```bash
# Option 1: Upload test images via web
python main.py --dashboard

# Option 2: Analyze existing images
python main.py --analyze your_sticky_trap.jpg

# Option 3: Batch process folder
python main.py --batch ./test_images/

# Show statistics
python main.py --stats --days 7
```

---

## 🌟 Advanced Features (Production Ready)

- **Auto-start on Pi boot** using systemd
- **Solar-powered deployment** for remote fields
- **Weather correlation** (future: link pest data to weather API)
- **ML model training** on collected data
- **Multi-farm management** for agricultural cooperatives
- **API endpoints** for third-party integration

---

## 📈 Impact for Farmers

### Before EcoBloom:
- ❌ Manual trap checking (hours per week)
- ❌ Delayed pest detection
- ❌ Guesswork on treatment timing
- ❌ No historical data

### After EcoBloom:
- ✅ Automated 24/7 monitoring
- ✅ Instant alerts for pest spikes
- ✅ Data-driven treatment decisions
- ✅ Track effectiveness over time
- ✅ Reduce pesticide use (targeted application)

---

## 🎓 Setup Guide

See **[SETUP.md](SETUP.md)** for detailed installation instructions.

---

## 🏆 Hackathon Highlights

**Innovation**: Combines IoT + Computer Vision for agriculture
**Scalability**: Works for 1 camera or 100+ cameras
**Accessibility**: Affordable Raspberry Pi hardware
**Real-World Impact**: Solves genuine farmer pain point
**Demo-Ready**: Web dashboard + instant image analysis

---

## 🤝 Team

Built for **Reboot Earth Hackathon**
Focused on sustainable farming through technology

---

## 📝 License

Open source for educational and agricultural use.

---

## 🔮 Future Enhancements

- [ ] Pest species classification (ML model)
- [ ] Mobile app for farmers
- [ ] Cloud storage integration (AWS/GCP)
- [ ] Treatment recommendation engine
- [ ] Weather API integration
- [ ] Marketplace for pest data insights

---

**🌱 Making farming smarter, one trap at a time.**