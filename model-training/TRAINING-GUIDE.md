# YOLOv8 Training Guide - Yellow Sticky Traps Dataset

## Overview

**Dataset**: 284 images, 8,114 annotations
**Classes**: 3 insect types (Macrolophus pygmaeus, Nesidiocoris tenuis, Whitefly)
**Source**: https://github.com/md-121/yellow-sticky-traps-dataset
**Format**: PASCAL VOC → YOLO conversion

---

## Quick Start (5 Minutes Setup)

### Option 1: Google Colab (FREE GPU - RECOMMENDED)

1. **Open Google Colab**: https://colab.research.google.com
2. **Create new notebook**
3. **Run training cells**:

```python
# Install dependencies
!pip install ultralytics requests

# Download training script
!wget https://raw.githubusercontent.com/YOUR_REPO/model-training/train_yolov8.py

# Run training
!python train_yolov8.py
```

**Training time**: 4-6 hours (free GPU)

### Option 2: Local Machine

```bash
# Install dependencies
pip install -r requirements-training.txt

# Run training script
python train_yolov8.py
```

**Training time**: 1-2 days (CPU) or 4-6 hours (GPU)

---

## Training Pipeline Details

### Step 1: Download Dataset (~2GB)
```python
python train_yolov8.py
# Auto-downloads from GitHub
# Extracts 284 JPEG images + XML annotations
```

### Step 2: Convert to YOLO Format
- Reads PASCAL VOC XML files
- Converts to YOLO txt format
- Splits train/val (80/20)
- Creates data.yaml

**Output**:
```
yolo_dataset/
├── images/
│   ├── train/ (227 images)
│   └── val/ (57 images)
├── labels/
│   ├── train/ (227 .txt files)
│   └── val/ (57 .txt files)
└── data.yaml
```

### Step 3: Train YOLOv8n
- Model: YOLOv8n (nano - 6MB, Pi-optimized)
- Epochs: 100
- Batch: 16
- Image size: 640x640
- Device: GPU (or CPU fallback)

### Step 4: Export for Deployment
- Format: TorchScript (.torchscript)
- Optimized for Raspberry Pi inference
- Ready to deploy

---

## Training Configuration

**Hyperparameters** (in `train_yolov8.py`):
```python
epochs=100           # Full training cycles
batch=16            # Images per batch (reduce if OOM)
imgsz=640           # Input image size
device=0            # GPU device (or 'cpu')
patience=20         # Early stopping patience
```

**Augmentation** (automatic):
- Random rotation
- Horizontal/vertical flips
- HSV color jittering
- Mosaic augmentation
- Scale/translate

---

## Expected Results

### Performance Metrics
Based on similar greenhouse pest datasets:

| Metric | Expected |
|--------|----------|
| mAP@0.5 | 85-92% |
| mAP@0.5:0.95 | 65-75% |
| Inference time (Pi 4) | 100-150ms |
| Model size | ~6MB |

### Per-Class Performance
- **Whitefly** (5,807 labels): 90-95% mAP
- **Macrolophus** (1,619 labels): 80-85% mAP
- **Nesidiocoris** (688 labels): 75-82% mAP

---

## Google Colab Training (Step-by-Step)

### 1. Setup Colab Notebook

```python
# Cell 1: Check GPU
!nvidia-smi
```

```python
# Cell 2: Install dependencies
!pip install ultralytics requests tqdm
```

### 2. Download & Prepare Dataset

```python
# Cell 3: Clone training script
!git clone https://github.com/YOUR_REPO/EcoBloom.git
%cd EcoBloom/model-training
```

```python
# Cell 4: Run training pipeline
!python train_yolov8.py
```

### 3. Monitor Training

```python
# Cell 5: View training plots
from IPython.display import Image
Image('runs/train/sticky-traps-v1/results.png')
```

### 4. Download Trained Model

```python
# Cell 6: Download model to local machine
from google.colab import files
files.download('runs/train/sticky-traps-v1/weights/best.pt')
files.download('runs/train/sticky-traps-v1/weights/best.torchscript')
```

---

## Validation & Testing

### Validate Model
```bash
python -c "from ultralytics import YOLO; \
    YOLO('runs/train/sticky-traps-v1/weights/best.pt').val()"
```

### Test on New Image
```bash
python -c "from ultralytics import YOLO; \
    YOLO('runs/train/sticky-traps-v1/weights/best.pt').predict(
        'test_trap.jpg',
        save=True,
        conf=0.25
    )"
```

---

## Deployment to EcoBloom

### 1. Copy Model to Project
```bash
cp runs/train/sticky-traps-v1/weights/best.torchscript \
   ../../modules/models/yolov8_sticky_traps.torchscript
```

### 2. Update Detection Module

**Edit `modules/pest_detector.py`**:
```python
import torch

class PestDetectorYOLO:
    def __init__(self):
        self.model = torch.jit.load('modules/models/yolov8_sticky_traps.torchscript')

    def detect(self, image_path):
        # Run inference
        results = self.model(image_path)
        return results
```

### 3. Test Integration
```bash
python -c "from modules.pest_detector import PestDetectorYOLO; \
    detector = PestDetectorYOLO(); \
    print(detector.detect('test_trap.jpg'))"
```

---

## Troubleshooting

### Out of Memory (OOM)
**Solution**: Reduce batch size
```python
# In train_yolov8.py, line ~200
batch=8  # Instead of 16
```

### Slow Training on CPU
**Solution**: Use Google Colab free GPU
- 100 epochs: 1-2 days (CPU) vs 4-6 hours (GPU)

### Low Accuracy
**Solutions**:
1. Train longer (150-200 epochs)
2. Collect more data (CVAT annotation)
3. Adjust augmentation parameters

### Dataset Download Fails
**Solution**: Manual download
```bash
wget https://github.com/md-121/yellow-sticky-traps-dataset/archive/refs/heads/main.zip
unzip main.zip
```

---

## Next Steps After Training

### 1. Integrate with EcoBloom
- Copy model to `modules/models/`
- Update `pest_detector.py`
- Test on Raspberry Pi

### 2. Continuous Improvement
- Collect Qatar farm images
- Annotate in CVAT
- Retrain with combined dataset
- Achieve 95%+ accuracy

### 3. Deploy to Production
- Push model to all Raspberry Pi devices
- Monitor performance
- Collect farmer feedback
- Monthly retraining

---

## Cost Analysis

### Training Costs
| Resource | Cost |
|----------|------|
| Google Colab (free GPU) | $0 |
| Dataset (open-source) | $0 |
| Ultralytics YOLOv8 | $0 (open-source) |
| **Total** | **$0** |

### Time Investment
- Dataset preparation: 30 minutes
- Training: 4-6 hours (automated)
- Validation: 30 minutes
- Deployment: 1 hour
- **Total**: ~7 hours

---

## References

- **Dataset**: https://github.com/md-121/yellow-sticky-traps-dataset
- **YOLOv8 Docs**: https://docs.ultralytics.com
- **Google Colab**: https://colab.research.google.com
- **Training Tutorial**: https://docs.ultralytics.com/modes/train/

---

*For EcoBloom Hackathon - October 2025*
*284 images → Production-ready model in 6 hours*
