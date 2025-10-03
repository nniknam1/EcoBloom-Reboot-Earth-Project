#!/usr/bin/env python3
"""
EcoBloom Pest Detection - Clean Demo Runner
Analyzes sticky trap images using OpenCV color-based detection
"""

import cv2
import numpy as np
import os
import sys
from datetime import datetime

def analyze_sticky_trap(image_path, output_dir="demo_results"):
    """
    Analyze a sticky trap image for pests

    Args:
        image_path: Path to sticky trap image
        output_dir: Directory to save results
    """
    print("="*70)
    print("         EcoBloom Pest Detection Demo")
    print("="*70)
    print()

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load image
    print(f"[1/4] Loading image: {image_path}")
    img = cv2.imread(image_path)

    if img is None:
        print(f"ERROR: Could not load image: {image_path}")
        return None

    print(f"      Image size: {img.shape[1]}x{img.shape[0]} pixels")

    # Convert to HSV
    print("[2/4] Analyzing image...")
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Adaptive threshold based on brightness
    avg_brightness = np.mean(hsv[:, :, 2])

    if avg_brightness < 80:
        upper_value = 120
        lighting = "dark"
    elif avg_brightness > 180:
        upper_value = 80
        lighting = "bright"
    else:
        upper_value = 100
        lighting = "normal"

    print(f"      Lighting: {lighting} (brightness: {avg_brightness:.1f})")

    # Detect dark objects (insects)
    lower_dark = np.array([0, 0, 0])
    upper_dark = np.array([180, 255, upper_value])
    mask = cv2.inRange(hsv, lower_dark, upper_dark)

    # Noise removal
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter by size
    min_area = 50  # Configurable
    max_area = 5000
    detected_pests = []

    print("[3/4] Detecting pests...")

    for idx, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if min_area < area < max_area:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)

            detected_pests.append({
                'id': idx + 1,
                'center': center,
                'radius': radius,
                'area': area
            })

            # Draw detection
            cv2.circle(img, center, max(radius, 10), (0, 255, 0), 2)
            cv2.putText(img, f'#{idx+1}', (center[0]-10, center[1]-radius-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    pest_count = len(detected_pests)

    # Risk assessment
    if pest_count <= 5:
        risk = "LOW"
        color = (0, 255, 0)
    elif pest_count <= 15:
        risk = "MEDIUM"
        color = (0, 165, 255)
    else:
        risk = "HIGH"
        color = (0, 0, 255)

    # Add overlay
    cv2.putText(img, f"Detected: {pest_count} pests | Risk: {risk}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.putText(img, f"EcoBloom Demo - {datetime.now().strftime('%Y-%m-%d')}",
               (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    # Save result
    output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(image_path))[0]}_analyzed.jpg")
    cv2.imwrite(output_path, img)

    print("[4/4] Results:")
    print()
    print("="*70)
    print(f"  Pests Detected:  {pest_count}")
    print(f"  Risk Level:      {risk}")
    print(f"  Output Image:    {output_path}")
    print("="*70)
    print()

    if detected_pests:
        print(f"Top 10 detected pests by size:")
        print("-"*70)
        sorted_pests = sorted(detected_pests, key=lambda x: x['area'], reverse=True)
        for pest in sorted_pests[:10]:
            print(f"  Pest #{pest['id']}: Area={pest['area']:.0f}px at ({pest['center'][0]}, {pest['center'][1]})")
        print("-"*70)

    print()
    print(f"[+] Analysis complete! Open: {output_path}")
    print()
    print("NOTE: This demo uses OpenCV color-based detection.")
    print("      Production version will use custom YOLOv8 model.")
    print("      See model-training/README.md for details.")
    print("="*70)

    return {
        'pest_count': pest_count,
        'risk_level': risk,
        'output_path': output_path,
        'detected_pests': detected_pests
    }

if __name__ == "__main__":
    # Check for command line argument
    if len(sys.argv) < 2:
        print("Usage: python run_demo.py <image_path>")
        print()
        print("Example:")
        print("  python run_demo.py sticky_trap.jpg")
        print()

        # Try to find the fungus gnat image
        test_image = "dark-winged-fungus-gnats-and-white-flies-are-stuck-on-a-yellow-sticky-trap-whiteflies-trapped-and-sciaridae-fly-sticky-in-a-trap-stockpack-adobe-stock-540x540.jpg"
        if os.path.exists(test_image):
            print(f"Found test image: {test_image}")
            print("Running demo on this image...")
            print()
            analyze_sticky_trap(test_image)
        else:
            print("No test image found. Please provide an image path.")
        sys.exit(0)

    image_path = sys.argv[1]

    if not os.path.exists(image_path):
        print(f"ERROR: Image not found: {image_path}")
        sys.exit(1)

    analyze_sticky_trap(image_path)
