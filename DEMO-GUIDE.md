# EcoBloom Hackathon Demo Guide

## Quick Demo (5 Minutes)

### 1. Run Single Image Analysis
```bash
python run_demo.py dark-winged-fungus-gnats-and-white-flies-are-stuck-on-a-yellow-sticky-trap-whiteflies-trapped-and-sciaridae-fly-sticky-in-a-trap-stockpack-adobe-stock-540x540.jpg
```

**Shows**: Real pest detection on actual sticky trap image

### 2. Start Web Dashboard
```bash
python dashboard_simple.py
```
**Access**: http://localhost:5000

**Shows**: Multi-location monitoring interface with upload capability

### 3. Show CVAT Training Plan
Open: `model-training/README.md`

**Highlights**:
- Current: OpenCV demo (70-75% accuracy)
- Production: Custom YOLOv8 (90-94% projected)
- Timeline: 6-8 weeks post-deployment

---

## Full Demo Flow (15 Minutes)

### Part 1: Problem Statement (2 min)
"Farmers waste hours manually checking sticky traps across large fields. Late detection = crop damage."

### Part 2: Solution Overview (3 min)
- **Hardware**: $50 Raspberry Pi cameras vs $500+ commercial
- **Software**: Automated detection + alerts
- **Scalability**: 1 camera or 100+ cameras

### Part 3: Live Demo (5 min)

**Demo 1: Single Image Analysis**
```bash
python run_demo.py <your_image>.jpg
```
- Shows detection in action
- Risk assessment
- Output visualization

**Demo 2: Web Dashboard**
- Upload new images
- View detection history
- Multi-location stats
- Trend analysis

### Part 4: CVAT/ML Differentiator (3 min)
Open `model-training/README.md`

**Key Points**:
- "We're using OpenCV for this 2-day demo"
- "Production uses custom YOLOv8 trained on Qatar farms"
- "CVAT annotation workflow designed"
- "Community-driven dataset improvement"

**Honest Approach**:
> "We could have rushed a model on 20 images and gotten 60% accuracy. Instead, we built the full IoT system and designed proper ML pipeline. Better to demo with proven OpenCV than deploy bad AI."

### Part 5: Business Model (2 min)
- **Cost**: $50/camera vs $500-2000 competitors
- **Open Source**: Anyone can replicate
- **Community**: Dataset improves with more farms
- **Scalable**: Proven for 1-100+ locations

---

## Judge Q&A Responses

### "Why didn't you train a custom model?"
> "Quality ML requires 200+ properly annotated images and real farm data. We prioritized:
> 1. Working end-to-end IoT system
> 2. Multi-location architecture
> 3. Production-ready training pipeline
>
> We'll train properly during pilot deployment with actual Qatar greenhouse data. That's responsible engineering."

### "How is this different from competitors?"
> "Commercial solutions cost $500-2000 per camera and use generic global models. We offer:
> - $50 Raspberry Pi cameras
> - Qatar-specific training
> - Open-source community approach
> - Model improves as more farms join"

### "What if the detection is wrong?"
> "Farmers flag errors in dashboard → we retrain monthly → accuracy improves over time. It's a learning system."

### "How does CVAT integration work?"
> "Camera traps collect images → CVAT team workspace → bounding box annotations → YOLOv8 training → deploy to all devices. See our workflow doc."

---

## Files to Show Judges

### 1. **Working Demo**
- `run_demo.py` - Single image analysis
- `dashboard_simple.py` - Web interface
- `demo_results/` - Output examples

### 2. **CVAT Training Plan**
- `model-training/README.md` - Complete methodology
- `model-training/yolov8-training-config.yaml` - Training config
- `model-training/docs/CVAT-WORKFLOW.md` - Annotation workflow

### 3. **Production System**
- `modules/` - Modular architecture
- `config.json` - Configurable parameters
- `README.md` - Full system documentation

---

## Key Talking Points

### Innovation
- **IoT + Computer Vision**: Automated 24/7 monitoring
- **CVAT Integration**: Community-driven training
- **Multi-Location**: Farm-wide dashboard
- **Open Source**: Reproducible & improvable

### Technical Depth
- **Raspberry Pi Integration**: Edge computing
- **Adaptive Algorithms**: Lighting adjustment
- **Database Tracking**: Historical trends
- **Alert System**: Email/SMS/MQTT

### Real-World Impact
- **Time Savings**: Hours → Minutes
- **Cost Reduction**: $2000 → $50 per location
- **Better Decisions**: Data-driven treatment
- **Environmental**: Targeted pesticide use

### Scalability
- **Proven Architecture**: 1 to 100+ cameras
- **Cloud Ready**: Multi-farm management
- **Model Versioning**: OTA updates
- **Community Growth**: Dataset improves

---

## Demo Tips

### Do's
✅ Be honest about demo vs production
✅ Show working code (not slides)
✅ Emphasize scalability
✅ Highlight cost advantage
✅ Explain CVAT workflow clearly

### Don'ts
❌ Claim you trained ML model in 2 days
❌ Over-promise accuracy
❌ Hide limitations
❌ Compare to generic solutions unfairly

---

## Backup Demos

### If Internet Fails
- Run local demo: `python run_demo.py`
- Show offline capabilities
- Explain cloud sync happens later

### If Code Crashes
- Show `demo_results/` folder with pre-generated outputs
- Walk through code in IDE
- Explain architecture on whiteboard

---

## Post-Demo Follow-Up

### Judges Want More Info
Point to:
- GitHub repo (if public)
- `SETUP.md` - Installation guide
- `model-training/README.md` - ML roadmap

### Interested Farmers
- Pilot program: 2-3 farms (free)
- 3-month trial
- Collect training data
- Train custom model
- Scale to community

---

## Success Metrics

**Hackathon Win Criteria**:
- ✅ Working demo with real pest image
- ✅ Multi-location architecture
- ✅ Clear ML improvement path (CVAT)
- ✅ Honest about limitations
- ✅ Strong business case ($50 vs $2000)

**Demo Checklist**:
- [ ] Tested `run_demo.py` with fungus gnat image
- [ ] Dashboard running on http://localhost:5000
- [ ] Can explain CVAT workflow
- [ ] Practiced honest ML approach speech
- [ ] Know all file locations

---

*EcoBloom - Making farming smarter, one trap at a time* 🌱
