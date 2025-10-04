# 🌱 EcoBloom - Smart Agriculture Platform

**Comprehensive IoT System for Sustainable Farming in Qatar**
*Built for Reboot Earth Hackathon 2025*

---

## 🎯 Overview

EcoBloom is an integrated agricultural monitoring platform that combines multiple smart farming technologies to help farmers in Qatar optimize crop production, detect pests early, prevent heat stress, and share critical information across farms.

### The Challenge
Farmers face multiple threats to crop health:
- **Pest infestations** detected too late, causing crop damage
- **Heat stress** from extreme temperatures affecting plant health
- **Information isolation** - no way to share pest alerts between farms
- **Manual monitoring** - time-consuming and ineffective

### Our Solution
An affordable, open-source platform with **4 integrated systems**:

1. **🐛 Pest Detection System** - Automated sticky trap monitoring
2. **🌡️ Heat Stress Detection** - Plant health monitoring via computer vision
3. **🔗 P2P Alert Network** - Farm-to-farm communication system
4. **📊 Unified Dashboard** - Centralized monitoring interface

---

## 🚀 Quick Start

### Installation

**Prerequisites:**
- Python 3.8 or higher
- pip (Python package manager)

**Install all dependencies:**
```bash
# Clone the repository
git clone https://github.com/nniknam1/EcoBloom-Reboot-Earth-Project.git
cd EcoBloom-Reboot-Earth-Project

# Install dependencies for all 4 systems
pip install -r requirements.txt
```

**What gets installed:**
- ✅ **Sticky Trap System**: OpenCV, schedule, Flask
- ✅ **Heat Stress Detection**: scikit-learn, pandas, matplotlib, seaborn
- ✅ **P2P Network**: No extra packages (uses Python standard library)
- ✅ **Dashboard**: Flask-Cors

**Optional (for ML training only):**
```bash
# Only needed if you want to train custom YOLOv8 models
pip install -r "Sticky Trap System/model-training/requirements-training.txt"
```

**Raspberry Pi Camera Setup (if deploying on hardware):**
```bash
# For Pi Camera Module 3 (newer):
sudo apt install -y python3-picamera2

# For older Pi Camera modules:
sudo apt install -y python3-picamera
```

### Run Individual Systems

**Pest Detection System:**
```bash

cd "Sticky Trap System"
python run_demo.py sticky-trap-sample.jpg
# Or run dashboard:
python dashboard_simple.py
```

**Heat Stress Detection:**
```bash
cd Heat-Risk
python heat_stress_app.py
```

**P2P Alert Network:**
```bash
cd P2P-System
python demo_launcher.py
```

**Unified Dashboard:**
```bash
cd Dashboard
python app.py
```

---

## 📁 Project Structure

```
EcoBloom-Reboot-Earth-Project/
│
├── Sticky Trap System/          # Automated Pest Detection
│   ├── modules/                 # Core detection modules
│   │   ├── camera_capture.py    # Raspberry Pi camera integration
│   │   ├── pest_detector.py     # OpenCV pest detection
│   │   ├── data_logger.py       # SQLite database management
│   │   ├── alert_system.py      # Email/SMS/MQTT alerts
│   │   └── scheduler.py         # Automated monitoring
│   ├── model-training/          # YOLOv8 training pipeline
│   │   ├── train_yolov8.py      # Auto-training script
│   │   ├── TRAINING-GUIDE.md    # Step-by-step training
│   │   └── README.md            # ML methodology
│   ├── dashboard.py             # Full web dashboard
│   ├── dashboard_simple.py      # Simplified dashboard
│   ├── run_demo.py              # Quick demo script
│   ├── config.json              # System configuration
│   ├── data/                    # Database and images
│   └── templates/               # Web UI templates
│
├── Heat-Risk/                   # Plant Heat Stress Detection
│   ├── heat_risk.py             # ML model for heat stress
│   ├── heat_stress_app.py       # Flask web interface
│   ├── heat_stress_model.pkl    # Trained model
│   └── dataset_crops/           # Training data
│
├── P2P-System/                  # Farm-to-Farm Communication
│   ├── peer.py                  # P2P node implementation
│   ├── message.py               # Message protocol
│   ├── router.py                # Network routing
│   ├── pest_alert_handler.py    # Pest alert integration
│   ├── demo_launcher.py         # Multi-farm demo
│   ├── dashboard.html           # P2P network dashboard
│   └── database/                # Message storage
│
├── Dashboard/                   # Unified Monitoring Dashboard
│   ├── app.py                   # Main dashboard server
│   ├── dashboard.html           # Combined interface
│   └── service_logs/            # System logs
│
├── Pest-detection/              # Alternative pest detection UI
│   ├── pest_detection.py        # Detection engine
│   └── pest_detection.html      # Web interface
│
├── README.md                    # This file
├── SETUP.md                     # Detailed setup guide
├── requirements.txt             # Python dependencies
└── DEMO-GUIDE.md               # Hackathon demo instructions
```

---

## 🐛 System 1: Sticky Trap Pest Detection

### Features
- **Automated Image Capture**: Raspberry Pi cameras photograph sticky traps every hour
- **Smart Detection**: OpenCV-based pest counting with adaptive thresholds
- **Multi-Location Support**: Monitor multiple farm zones simultaneously
- **Risk Assessment**: LOW/MEDIUM/HIGH classification based on pest count
- **Alert System**: Email, SMS, and MQTT notifications
- **Historical Tracking**: SQLite database with trend analysis
- **Web Dashboard**: Real-time monitoring interface

### Hardware
- Raspberry Pi 4 (or 3B+)
- Pi Camera Module (v2, v3, or HQ)
- Yellow sticky traps
- Optional: weatherproof enclosure for outdoor deployment

### Usage
```bash
cd "Sticky Trap System"

# Quick demo
python run_demo.py sticky-trap-sample.jpg

# Run web dashboard
python dashboard_simple.py
# Access at: http://localhost:5000

# Start automated monitoring
python modules/scheduler.py
```

### Machine Learning Pipeline
We include a **YOLOv8 training system** for production deployment:
- Pre-configured training script (`model-training/train_yolov8.py`)
- Ready-to-use dataset with 284 annotated images
- Google Colab integration for free GPU training
- Export models for Raspberry Pi deployment
- See `model-training/README.md` for details

### Configuration
Edit `config.json` to set:
- Camera location and GPS coordinates
- Capture intervals
- Detection thresholds
- Alert settings (email, SMS, MQTT)

---

## 🌡️ System 2: Heat Stress Detection

### Features
- **Computer Vision Analysis**: Detects heat stress symptoms in plants
- **Machine Learning Model**: Trained on crop stress indicators
- **Real-Time Monitoring**: Continuous plant health assessment
- **Preventive Alerts**: Early warning system before visible damage
- **Data Logging**: Historical stress patterns

### Technology
- Scikit-learn Random Forest classifier
- Image preprocessing with OpenCV
- Flask web interface
- Feature extraction for leaf analysis

### Usage
```bash
cd Heat-Risk
python heat_stress_app.py
# Access at: http://localhost:5001
```

### How It Works
1. Camera captures plant images
2. ML model analyzes visual stress indicators:
   - Leaf color changes
   - Wilting patterns
   - Growth anomalies
3. Risk score generated (0-100%)
4. Alerts sent if threshold exceeded

---

## 🔗 System 3: P2P Alert Network

### Features
- **Decentralized Communication**: Farm-to-farm messaging without central server
- **Pest Alert Sharing**: Broadcast warnings across farming community
- **Resilient Network**: Works even if internet connection drops
- **Privacy-Focused**: Direct peer communication
- **Message Persistence**: Local database for offline capability
- **Multi-Farm Dashboard**: Visualize network and alerts

### Architecture
```
Farm A (Peer) ←→ Farm B (Peer)
     ↕               ↕
Farm C (Peer) ←→ Farm D (Peer)
```

### Usage
```bash
cd P2P-System

# Launch demo with 3 virtual farms
python demo_launcher.py

# Run single peer node
python main.py --port 5555 --name "Farm A"
```

### Features in Detail
- **Message Routing**: Intelligent path finding between farms
- **Pest Alert Handler**: Integration with pest detection system
- **WebSocket Bridge**: Real-time dashboard updates
- **Message Store**: Persistent storage for reliability

---

## 📊 System 4: Unified Dashboard

### Features
- **Single Interface**: Monitor all systems in one place
- **Real-Time Updates**: Live data from all sensors
- **Historical Data**: Trends and analytics
- **Multi-Location View**: See status across all farms
- **Alert Management**: Centralized notification center

### Usage
```bash
cd Dashboard
python app.py
# Access at: http://localhost:5002
```

### Dashboard Components
- Pest detection statistics
- Heat stress indicators
- P2P network status
- Alert history
- System health monitoring

---

## 🛠️ Technology Stack

### Hardware
- **Raspberry Pi 4** - Edge computing
- **Pi Camera Module** - Image capture
- **Yellow Sticky Traps** - Pest monitoring
- Optional: Environmental sensors (temperature, humidity)

### Software
- **Computer Vision**: OpenCV, NumPy
- **Machine Learning**: YOLOv8 (Ultralytics), Scikit-learn
- **Backend**: Python, Flask
- **Database**: SQLite
- **Networking**: WebSockets, P2P messaging
- **Alerts**: SMTP (email), Twilio (SMS), MQTT
- **Scheduling**: Python `schedule` library

### Deployment
- Tested on Windows, Linux, Raspberry Pi OS
- Docker support (optional)
- Cloud-ready architecture

---

## 💡 Use Cases

### Small-Scale Farms (1-5 hectares)
- Deploy 2-3 sticky trap cameras in key zones
- Single heat stress monitoring station
- Connect to neighboring farms via P2P

### Large Operations (10+ hectares)
- Multiple camera zones across property
- Distributed heat stress monitoring
- Central dashboard for farm management
- Integration with existing farm systems

### Greenhouse Farming
- Controlled environment monitoring
- Early pest detection in enclosed spaces
- Heat stress prevention with climate control
- Data-driven ventilation decisions

### Agricultural Cooperatives
- Share pest alerts across member farms
- Community-wide trend analysis
- Collaborative pest management
- Knowledge sharing platform

---

## 📈 Impact & Benefits

### Before EcoBloom
❌ Manual trap checking (hours per week)
❌ Delayed pest detection
❌ Reactive heat stress management
❌ No communication between farms
❌ Guesswork on treatment timing

### After EcoBloom
✅ Automated 24/7 monitoring
✅ Instant pest alerts
✅ Proactive heat stress prevention
✅ Farm-to-farm information sharing
✅ Data-driven decision making
✅ Reduced pesticide use (targeted application)
✅ Improved crop yields

### Cost Comparison

| Component | EcoBloom | Commercial Solution |
|-----------|----------|-------------------|
| Pest Detection Camera | $50 | $500-2000 |
| Heat Stress Monitor | $60 | $1000+ |
| Communication System | $0 (P2P) | $500/year subscription |
| Dashboard | Free | $100/month |
| **Total (per location)** | **~$110** | **$3000+** |

---

## 🎓 Setup & Configuration

For detailed installation instructions, see **[SETUP.md](SETUP.md)**

Quick checklist:
1. ✅ Install Python 3.8+
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Configure camera (if using Raspberry Pi)
4. ✅ Edit config files for your location
5. ✅ Test individual systems
6. ✅ Start unified dashboard

---

## 🏆 Hackathon Highlights

**Why EcoBloom Stands Out:**

1. **Complete Integration**: Not just one tool, but a full farming platform
2. **Real Hardware**: Designed for actual Raspberry Pi deployment
3. **P2P Innovation**: Unique farm-to-farm communication network
4. **Production-Ready ML**: Includes full YOLOv8 training pipeline
5. **Affordable**: 95% cheaper than commercial alternatives
6. **Open Source**: Community-driven, extensible
7. **Qatar-Focused**: Designed for local climate and farming needs

---

## 🔮 Future Enhancements

### Phase 1 (Next 3 Months)
- [ ] Mobile app for farmers (iOS/Android)
- [ ] Weather API integration
- [ ] Automatic irrigation recommendations
- [ ] Enhanced P2P network with encryption

### Phase 2 (6 Months)
- [ ] Custom YOLOv8 model trained on Qatar farm data
- [ ] Pest species classification (not just counting)
- [ ] Drone integration for large-scale monitoring
- [ ] Cloud sync for multi-farm management

### Phase 3 (12 Months)
- [ ] Treatment recommendation engine
- [ ] Marketplace for pest management insights
- [ ] Community annotation platform (CVAT integration)
- [ ] Integration with farm management software

---

## 🤝 Contributing

We welcome contributions from:
- **Farmers**: Share your pest images for training data
- **Developers**: Improve detection algorithms
- **Agricultural Experts**: Enhance pest identification
- **Students**: Learn IoT and computer vision

See individual system folders for specific contribution guidelines.

---

## 📝 License

Open source for educational and agricultural use.
Commercial use requires attribution.

---

## 🙏 Acknowledgments

- **Reboot Earth Hackathon 2025** - For the opportunity
- **Qatar Agricultural Community** - For inspiration
- **Open Source Community** - OpenCV, YOLOv8, Flask
- **Yellow Sticky Trap Dataset** - 284 annotated images for training

---

## 📞 Contact & Support

**For Demo Questions**: Check `DEMO-GUIDE.md`
**For Setup Help**: Read `SETUP.md`
**For ML Training**: See `Sticky Trap System/model-training/README.md`

---

## 🎬 Quick Demo Commands

```bash
# Demo 1: Pest Detection
cd "Sticky Trap System" && python run_demo.py sticky-trap-sample.jpg

# Demo 2: Heat Stress
cd ../Heat-Risk && python heat_stress_app.py

# Demo 3: P2P Network
cd ../P2P-System && python demo_launcher.py

# Demo 4: Unified Dashboard
cd ../Dashboard && python app.py
```

---

**🌱 Making farming smarter, safer, and more connected - one farm at a time.**

---

**Built with ❤️ for sustainable agriculture in Qatar**
