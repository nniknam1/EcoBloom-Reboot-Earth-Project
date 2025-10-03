#!/usr/bin/env python3
"""
Train YOLOv8 on Yellow Sticky Traps Dataset
Dataset: https://github.com/md-121/yellow-sticky-traps-dataset

This script:
1. Downloads the dataset
2. Converts PASCAL VOC to YOLO format
3. Trains YOLOv8 model
4. Exports for Raspberry Pi deployment
"""

import os
import sys
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
import requests
import zipfile

def download_dataset(output_dir="dataset"):
    """
    Download yellow sticky traps dataset from GitHub
    """
    print("="*70)
    print("  Step 1: Downloading Yellow Sticky Traps Dataset")
    print("="*70)

    # GitHub repo
    repo_url = "https://github.com/md-121/yellow-sticky-traps-dataset/archive/refs/heads/main.zip"

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    zip_path = output_dir / "dataset.zip"

    print(f"\n[*] Downloading from GitHub...")
    print(f"    URL: {repo_url}")

    # Download
    response = requests.get(repo_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(zip_path, 'wb') as f:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total_size > 0:
                percent = (downloaded / total_size) * 100
                print(f"\r    Progress: {percent:.1f}%", end="")

    print("\n[+] Download complete!")

    # Extract
    print("\n[*] Extracting dataset...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

    # Find extracted folder
    extracted_folder = output_dir / "yellow-sticky-traps-dataset-main"

    print(f"[+] Dataset extracted to: {extracted_folder}")

    return extracted_folder

def convert_voc_to_yolo(voc_xml_path, image_width, image_height, class_names):
    """
    Convert PASCAL VOC XML annotation to YOLO format

    YOLO format: <class_id> <x_center> <y_center> <width> <height>
    All values normalized to 0-1
    """
    tree = ET.parse(voc_xml_path)
    root = tree.getroot()

    yolo_annotations = []

    for obj in root.findall('object'):
        class_name = obj.find('name').text

        if class_name not in class_names:
            continue

        class_id = class_names.index(class_name)

        bbox = obj.find('bndbox')
        xmin = float(bbox.find('xmin').text)
        ymin = float(bbox.find('ymin').text)
        xmax = float(bbox.find('xmax').text)
        ymax = float(bbox.find('ymax').text)

        # Convert to YOLO format (normalized)
        x_center = ((xmin + xmax) / 2) / image_width
        y_center = ((ymin + ymax) / 2) / image_height
        width = (xmax - xmin) / image_width
        height = (ymax - ymin) / image_height

        yolo_annotations.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

    return yolo_annotations

def prepare_yolo_dataset(dataset_path, output_dir="yolo_dataset"):
    """
    Convert VOC format dataset to YOLO format
    """
    print("\n" + "="*70)
    print("  Step 2: Converting to YOLO Format")
    print("="*70)

    dataset_path = Path(dataset_path)
    output_dir = Path(output_dir)

    # Class names from dataset
    class_names = [
        'Macrolophus_pygmaeus',
        'Nesidiocoris_tenuis',
        'Trialeurodes_vaporariorum'  # Whitefly
    ]

    print(f"\n[*] Classes: {class_names}")

    # Create YOLO directory structure
    (output_dir / "images" / "train").mkdir(parents=True, exist_ok=True)
    (output_dir / "images" / "val").mkdir(parents=True, exist_ok=True)
    (output_dir / "labels" / "train").mkdir(parents=True, exist_ok=True)
    (output_dir / "labels" / "val").mkdir(parents=True, exist_ok=True)

    # Get all XML files
    annotations_dir = dataset_path / "Annotations"
    images_dir = dataset_path / "JPEGImages"

    if not annotations_dir.exists():
        print(f"[!] Annotations directory not found: {annotations_dir}")
        return None

    xml_files = list(annotations_dir.glob("*.xml"))
    print(f"\n[*] Found {len(xml_files)} annotation files")

    # Split train/val (80/20)
    split_idx = int(len(xml_files) * 0.8)
    train_files = xml_files[:split_idx]
    val_files = xml_files[split_idx:]

    print(f"[*] Train: {len(train_files)}, Val: {len(val_files)}")

    # Process train set
    print("\n[*] Converting train set...")
    for i, xml_file in enumerate(train_files):
        image_name = xml_file.stem + ".jpg"
        image_path = images_dir / image_name

        if not image_path.exists():
            continue

        # Convert annotation
        yolo_labels = convert_voc_to_yolo(
            xml_file,
            5184,  # Image width from dataset
            3456,  # Image height from dataset
            class_names
        )

        # Copy image
        shutil.copy(image_path, output_dir / "images" / "train" / image_name)

        # Save YOLO labels
        label_path = output_dir / "labels" / "train" / (xml_file.stem + ".txt")
        with open(label_path, 'w') as f:
            f.write('\n'.join(yolo_labels))

        if (i + 1) % 50 == 0:
            print(f"    Processed {i + 1}/{len(train_files)}")

    # Process val set
    print("\n[*] Converting val set...")
    for i, xml_file in enumerate(val_files):
        image_name = xml_file.stem + ".jpg"
        image_path = images_dir / image_name

        if not image_path.exists():
            continue

        yolo_labels = convert_voc_to_yolo(xml_file, 5184, 3456, class_names)

        shutil.copy(image_path, output_dir / "images" / "val" / image_name)

        label_path = output_dir / "labels" / "val" / (xml_file.stem + ".txt")
        with open(label_path, 'w') as f:
            f.write('\n'.join(yolo_labels))

    print(f"\n[+] Conversion complete!")

    # Create data.yaml
    data_yaml = f"""# Yellow Sticky Traps Dataset - YOLO Format
# 3 insect classes from greenhouse monitoring

path: {output_dir.absolute()}
train: images/train
val: images/val

# Classes
nc: 3
names:
  0: Macrolophus_pygmaeus
  1: Nesidiocoris_tenuis
  2: Trialeurodes_vaporariorum

# Dataset info
# Total images: 284
# Total annotations: 8,114
# Image size: 5184 x 3456
# Source: https://github.com/md-121/yellow-sticky-traps-dataset
"""

    yaml_path = output_dir / "data.yaml"
    with open(yaml_path, 'w') as f:
        f.write(data_yaml)

    print(f"[+] Created: {yaml_path}")

    return output_dir

def train_model(dataset_dir):
    """
    Train YOLOv8 model on the prepared dataset
    """
    print("\n" + "="*70)
    print("  Step 3: Training YOLOv8 Model")
    print("="*70)

    try:
        from ultralytics import YOLO
    except ImportError:
        print("\n[!] Ultralytics not installed!")
        print("[*] Install with: pip install ultralytics")
        return None

    dataset_dir = Path(dataset_dir)
    data_yaml = dataset_dir / "data.yaml"

    print(f"\n[*] Dataset: {data_yaml}")
    print(f"[*] Model: YOLOv8n (nano - Raspberry Pi optimized)")

    # Initialize model
    model = YOLO('yolov8n.pt')  # Nano version for Pi

    print("\n[*] Starting training...")
    print("    This will take 4-6 hours on GPU (Google Colab)")
    print("    Or 1-2 days on CPU")
    print()

    # Train
    results = model.train(
        data=str(data_yaml),
        epochs=100,
        imgsz=640,
        batch=16,
        device=0,  # GPU (use 'cpu' if no GPU)
        project='runs/train',
        name='sticky-traps-v1',
        exist_ok=True,
        patience=20,  # Early stopping
        save=True,
        plots=True
    )

    print("\n[+] Training complete!")

    # Validate
    print("\n[*] Validating model...")
    metrics = model.val()

    print(f"\n[+] Validation Results:")
    print(f"    mAP@0.5: {metrics.box.map50:.3f}")
    print(f"    mAP@0.5:0.95: {metrics.box.map:.3f}")

    return model

def export_for_pi(model):
    """
    Export model for Raspberry Pi deployment
    """
    print("\n" + "="*70)
    print("  Step 4: Exporting for Raspberry Pi")
    print("="*70)

    print("\n[*] Exporting to TorchScript format...")
    model.export(format='torchscript', imgsz=640)

    print("[+] Model exported!")
    print("[*] Deploy to Raspberry Pi:")
    print("    1. Copy .torchscript file to Pi")
    print("    2. Use in detection pipeline")

    return True

def main():
    """
    Main training pipeline
    """
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     EcoBloom YOLOv8 Training Pipeline                       ║
║     Yellow Sticky Traps Dataset (284 images, 8114 labels)   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Step 1: Download dataset
    print("\nWARNING: This will download ~2GB of data")
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    dataset_path = download_dataset()

    # Step 2: Convert to YOLO format
    yolo_dataset = prepare_yolo_dataset(dataset_path)

    if yolo_dataset is None:
        print("\n[!] Failed to prepare dataset")
        return

    # Step 3: Train
    print("\nWARNING: Training takes 4-6 hours on GPU")
    response = input("Start training? (y/n): ")
    if response.lower() != 'y':
        print("\n[*] Dataset prepared. You can train later with:")
        print(f"    python -c 'from ultralytics import YOLO; YOLO(\"yolov8n.pt\").train(data=\"{yolo_dataset}/data.yaml\", epochs=100)'")
        return

    model = train_model(yolo_dataset)

    if model is None:
        return

    # Step 4: Export
    export_for_pi(model)

    print("\n" + "="*70)
    print("  TRAINING COMPLETE!")
    print("="*70)
    print()
    print("Next steps:")
    print("  1. Check runs/train/sticky-traps-v1/ for results")
    print("  2. Deploy .torchscript model to Raspberry Pi")
    print("  3. Update EcoBloom detection module")
    print()

if __name__ == "__main__":
    main()
