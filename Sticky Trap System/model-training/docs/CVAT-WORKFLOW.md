# CVAT Annotation Workflow for EcoBloom

## Quick Start Guide

### Step 1: Access CVAT
- **Cloud Version**: https://cvat.ai (recommended for demo)
- **Self-Hosted**: https://github.com/opencv/cvat (for production)

Create free account on cvat.ai

### Step 2: Create Project
1. Click "Projects" → "Create new project"
2. Name: `EcoBloom Qatar Pests`
3. Labels:
   - whitefly
   - fungus_gnat
   - thrips
   - aphid
   - leaf_miner

### Step 3: Create Task
1. Inside project, click "Create new task"
2. Name: `Sticky Trap Batch 1`
3. Upload 10-50 images
4. Start annotation

### Step 4: Annotate Images
1. Select "Rectangle" tool
2. Draw bounding box around each pest
3. Label the pest type
4. Save (Ctrl+S)
5. Next image (F key)

### Step 5: Export Dataset
1. Go to project page
2. Click "Export dataset"
3. Format: **YOLO 1.1**
4. Download ZIP file

---

## Annotation Guidelines

### What to Annotate
- **Include**: All visible insects, even partial ones
- **Exclude**: Debris, dirt spots, glue artifacts

### Bounding Box Rules
- Box should tightly fit the insect
- Include wings if extended
- Separate overlapping insects if possible
- Label uncertain ones as "unknown" (review later)

### Quality Standards
- Minimum 200 annotations per class
- At least 3 different lighting conditions
- Various pest densities
- Mix of clear and challenging images

---

## Dataset Structure After Export

```
qatar-pests-yolo/
├── images/
│   ├── train/
│   │   ├── trap_001.jpg
│   │   ├── trap_002.jpg
│   │   └── ...
│   └── val/
│       ├── trap_101.jpg
│       └── ...
├── labels/
│   ├── train/
│   │   ├── trap_001.txt  # YOLO format
│   │   ├── trap_002.txt
│   │   └── ...
│   └── val/
│       └── ...
├── data.yaml
└── README.dataset.txt
```

### YOLO Label Format
Each .txt file contains:
```
<class_id> <x_center> <y_center> <width> <height>
```

Example (trap_001.txt):
```
1 0.5123 0.3456 0.0234 0.0456  # fungus_gnat at center (51.23%, 34.56%)
0 0.7890 0.2345 0.0123 0.0234  # whitefly
```

---

## Training Integration

After exporting from CVAT:

```bash
# 1. Extract ZIP
unzip qatar-pests-yolo.zip -d ./dataset

# 2. Train YOLOv8
python train.py --config yolov8-training-config.yaml

# 3. Validate
python val.py --model runs/train/qatar-pests-v1/weights/best.pt

# 4. Export for Raspberry Pi
python export.py --model best.pt --format torchscript --imgsz 640
```

---

## Team Collaboration

### Roles
- **Annotator 1**: Label dark insects (fungus gnats, thrips)
- **Annotator 2**: Label light insects (whiteflies, aphids)
- **Validator**: Review all annotations for accuracy
- **Expert**: Validate species identification

### Workflow
1. Upload batch of 50 images
2. Annotators work in parallel
3. Validator reviews each image
4. Expert spot-checks 10% random sample
5. Export when batch complete

---

## Performance Tracking

### Annotation Speed
- Beginner: 5-10 images/hour
- Experienced: 15-25 images/hour
- Target: 200 images in 10-15 hours

### Quality Metrics
- Inter-annotator agreement: >90%
- Expert validation pass rate: >95%
- Box accuracy (IoU): >0.7

---

## Tools & Resources

- **CVAT**: https://cvat.ai
- **Tutorial**: https://opencv.github.io/cvat/docs/
- **YOLOv8 Docs**: https://docs.ultralytics.com
- **Sample Datasets**: https://universe.roboflow.com

---

*For EcoBloom Hackathon Demo - October 2025*
