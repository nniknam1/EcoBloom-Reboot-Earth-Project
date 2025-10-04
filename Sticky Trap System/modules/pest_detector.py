"""
Enhanced Pest Detection Engine
Features: adaptive thresholds, location tagging, multiple detection methods
"""
import cv2
import numpy as np
import json
from PIL import Image
from datetime import datetime
from pathlib import Path
import os

class PestDetector:
    def __init__(self, config_path="config.json"):
        """Initialize detector with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.min_area = self.config['detection']['min_pest_area']
        self.max_area = self.config['detection']['max_pest_area']
        self.risk_thresholds = self.config['detection']['risk_thresholds']
        self.adaptive = self.config['detection']['adaptive_threshold']

    def load_image(self, image_path):
        """Load image regardless of format (jpg, png, webp, etc.)"""
        ext = os.path.splitext(image_path)[1].lower()

        if ext == '.webp':
            pil_image = Image.open(image_path)
            img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        else:
            img = cv2.imread(image_path)

        if img is None:
            raise ValueError(f"❌ Could not load image: {image_path}")

        return img

    def save_image(self, image, output_path):
        """Save image with proper format handling"""
        ext = os.path.splitext(output_path)[1].lower()

        if ext == '.webp':
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(img_rgb)
            pil_image.save(output_path, 'WEBP', quality=90)
        else:
            cv2.imwrite(output_path, image)

    def _calculate_adaptive_threshold(self, hsv_image):
        """
        Calculate adaptive threshold based on image brightness
        Helps with varying lighting conditions in the field
        """
        # Get average brightness (V channel in HSV)
        avg_brightness = np.mean(hsv_image[:, :, 2])

        # Adjust threshold based on brightness
        if avg_brightness < 80:  # Dark image
            upper_value = 120
        elif avg_brightness > 180:  # Bright image
            upper_value = 80
        else:  # Normal lighting
            upper_value = 100

        return upper_value

    def detect_pests(self, image_path, camera_metadata=None):
        """
        Main detection function with location tagging
        Returns detailed results with pest count, risk level, and metadata
        """
        print(f"🔍 Analyzing: {image_path}")

        # Load image
        img = self.load_image(image_path)
        original = img.copy()
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Adaptive threshold calculation
        if self.adaptive:
            upper_value = self._calculate_adaptive_threshold(hsv)
        else:
            upper_value = 100

        # Define range for dark objects (insects on sticky traps)
        lower_dark = np.array([0, 0, 0])
        upper_dark = np.array([180, 255, upper_value])

        # Create mask
        mask = cv2.inRange(hsv, lower_dark, upper_dark)

        # Noise removal
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Analyze each pest
        valid_pests = []
        pest_details = []

        for idx, contour in enumerate(contours):
            area = cv2.contourArea(contour)

            if self.min_area < area < self.max_area:
                # Get pest location and size
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                radius = int(radius)

                # Store pest details
                pest_info = {
                    "id": idx + 1,
                    "center": center,
                    "radius": radius,
                    "area": float(area),
                    "size_category": self._categorize_size(area)
                }
                pest_details.append(pest_info)
                valid_pests.append(contour)

                # Draw on image
                cv2.circle(img, center, radius, (0, 255, 0), 2)
                cv2.putText(img, f'#{idx+1}', (center[0]-15, center[1]-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        pest_count = len(valid_pests)

        # Calculate risk level
        risk_level, color = self._calculate_risk(pest_count)

        # Add summary overlay
        cv2.putText(img, f"Detected: {pest_count} insects | Risk: {risk_level}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Add location and timestamp if available
        if camera_metadata:
            location_text = camera_metadata.get('location', {}).get('name', 'Unknown')
            cv2.putText(img, f"Location: {location_text}",
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Generate output path
        base_name = os.path.splitext(image_path)[0]
        ext = os.path.splitext(image_path)[1]
        output_path = f"{base_name}_detected{ext}"

        # Save annotated image
        self.save_image(img, output_path)

        # Prepare results
        results = {
            "timestamp": datetime.now().isoformat(),
            "image_path": image_path,
            "output_path": output_path,
            "pest_count": pest_count,
            "risk_level": risk_level,
            "pest_details": pest_details,
            "detection_params": {
                "adaptive_threshold": self.adaptive,
                "threshold_value": int(upper_value),
                "min_area": self.min_area,
                "max_area": self.max_area
            }
        }

        # Add camera metadata if available
        if camera_metadata:
            results["camera_id"] = camera_metadata.get("camera_id")
            results["location"] = camera_metadata.get("location")

        print(f"✅ Detected {pest_count} insects | Risk: {risk_level}")

        return results

    def _categorize_size(self, area):
        """Categorize pest by size (useful for species identification)"""
        if area < 100:
            return "small"
        elif area < 500:
            return "medium"
        else:
            return "large"

    def _calculate_risk(self, pest_count):
        """Calculate risk level based on pest count"""
        if pest_count <= self.risk_thresholds['low']:
            return "LOW", (0, 255, 0)
        elif pest_count <= self.risk_thresholds['medium']:
            return "MEDIUM", (0, 165, 255)
        else:
            return "HIGH", (0, 0, 255)

    def batch_detect(self, image_folder, camera_metadata=None):
        """
        Process multiple images from a folder
        Useful for analyzing multiple traps or time-series data
        """
        print(f"📁 Batch processing folder: {image_folder}")

        image_folder = Path(image_folder)
        supported_formats = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']

        results_list = []

        for img_file in image_folder.iterdir():
            if img_file.suffix.lower() in supported_formats:
                try:
                    result = self.detect_pests(str(img_file), camera_metadata)
                    results_list.append(result)
                except Exception as e:
                    print(f"❌ Error processing {img_file}: {e}")

        print(f"✅ Batch complete: {len(results_list)} images processed")

        # Summary statistics
        total_pests = sum(r['pest_count'] for r in results_list)
        avg_pests = total_pests / len(results_list) if results_list else 0

        summary = {
            "total_images": len(results_list),
            "total_pests_detected": total_pests,
            "average_pests_per_image": round(avg_pests, 2),
            "results": results_list
        }

        return summary

# Test function
if __name__ == "__main__":
    print("🌱 Testing Pest Detection Engine")

    detector = PestDetector("../config.json")

    # Test with sample metadata
    test_metadata = {
        "camera_id": "CAM001",
        "location": {
            "name": "North Field - Zone A",
            "latitude": 40.7128,
            "longitude": -74.0060
        }
    }

    # Test detection (adjust path as needed)
    test_images = ["../sticky_trap.jpg", "../data/images/test.jpg"]

    for test_img in test_images:
        if os.path.exists(test_img):
            result = detector.detect_pests(test_img, test_metadata)
            print(json.dumps(result, indent=2))
            break
    else:
        print("⚠️ No test image found")
