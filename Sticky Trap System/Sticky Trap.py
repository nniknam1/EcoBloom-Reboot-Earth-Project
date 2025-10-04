import cv2
import numpy as np
from PIL import Image
import os

def load_image(image_path):
    """
    Load image regardless of format (jpg, png, webp, etc.)
    """
    # Get file extension
    ext = os.path.splitext(image_path)[1].lower()
   
    # For webp, use PIL then convert to OpenCV format
    if ext == '.webp':
        pil_image = Image.open(image_path)
        # Convert PIL image to numpy array (OpenCV format)
        img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    else:
        # For jpg, png, etc., use OpenCV directly
        img = cv2.imread(image_path)
   
    if img is None:
        raise ValueError(f"❌ Could not load image: {image_path}")
   
    return img

def save_image(image, output_path):
    """
    Save image with proper format handling
    """
    ext = os.path.splitext(output_path)[1].lower()
   
    if ext == '.webp':
        # Convert OpenCV image to PIL and save as webp
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(img_rgb)
        pil_image.save(output_path, 'WEBP', quality=90)
    else:
        # Use OpenCV for jpg, png
        cv2.imwrite(output_path, image)

def detect_pests_simple(image_path):
    """
    Simple color-based pest detection for sticky traps
    Works great for yellow sticky traps with dark insects
    Now supports: jpg, png, webp, bmp, tiff
    """
    print(f"📸 Loading image: {image_path}")
   
    # Read image (supports all formats including webp)
    img = load_image(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
   
    # Define range for dark objects (insects on yellow traps)
    # Adjust these values based on your trap color
    lower_dark = np.array([0, 0, 0])
    upper_dark = np.array([180, 255, 100])
   
    # Create mask for dark objects
    mask = cv2.inRange(hsv, lower_dark, upper_dark)
   
    # Remove noise
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
   
    # Find contours (each contour = potential insect)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   
    # Filter by size (remove very small/large objects)
    min_area = 20  # Adjust based on image resolution
    max_area = 5000
    valid_pests = []
   
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_area < area < max_area:
            valid_pests.append(contour)
            # Draw circle around pest
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            cv2.circle(img, center, radius, (0, 255, 0), 2)
            cv2.putText(img, 'Pest', (center[0]-20, center[1]-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
   
    pest_count = len(valid_pests)
   
    # Calculate risk level
    if pest_count <= 2:
        risk = "LOW"
        color = (0, 255, 0)
    elif pest_count <= 5:
        risk = "MEDIUM"
        color = (0, 165, 255)
    else:
        risk = "HIGH"
        color = (0, 0, 255)
   
    # Add summary text
    cv2.putText(img, f"Detected: {pest_count} insects | Risk: {risk}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
   
    # Generate output path (keep same format as input)
    base_name = os.path.splitext(image_path)[0]
    ext = os.path.splitext(image_path)[1]
    output_path = f"{base_name}_detected{ext}"
   
    # Save result (handles all formats)
    save_image(img, output_path)
   
    print(f"✅ Detected {pest_count} insects")
    print(f"🚨 Risk Level: {risk}")
    print(f"📸 Saved result to: {output_path}")
   
    return {
        "pest_count": pest_count,
        "risk_level": risk,
        "output_image": output_path,
        "details": f"Found {pest_count} dark objects on sticky trap",
        "input_format": ext
    }

def detect_pests_roboflow(image_path, api_key="YOUR_ROBOFLOW_API_KEY"):
    """
    BEST OPTION: Use Roboflow's pre-trained insect detection models
    Sign up at: https://universe.roboflow.com/
    Search for "insect detection" or "pest detection" models
    Now supports webp files!
    """
    from roboflow import Roboflow
   
    # Roboflow API requires jpg/png, so convert webp if needed
    ext = os.path.splitext(image_path)[1].lower()
    temp_path = image_path
   
    if ext == '.webp':
        print("🔄 Converting webp to jpg for Roboflow API...")
        img = load_image(image_path)
        temp_path = image_path.replace('.webp', '_temp.jpg')
        cv2.imwrite(temp_path, img)
   
    # Initialize Roboflow (free tier available)
    rf = Roboflow(api_key=api_key)
   
    # Use a pre-trained pest detection model
    # Example: "pest-detection-zue0y" or search for others on Roboflow Universe
    project = rf.workspace().project("pest-detection")
    model = project.version(1).model
   
    # Run prediction
    prediction = model.predict(temp_path, confidence=40).json()
   
    pest_count = len(prediction['predictions'])
   
    # Calculate risk
    if pest_count <= 2:
        risk = "LOW"
    elif pest_count <= 5:
        risk = "MEDIUM"
    else:
        risk = "HIGH"
   
    # Generate output path
    base_name = os.path.splitext(image_path)[0]
    original_ext = os.path.splitext(image_path)[1]
    output_path = f"{base_name}_detected{original_ext}"
   
    # Visualize and save
    model.predict(temp_path, confidence=40).save(output_path)
   
    # Clean up temp file if created
    if temp_path != image_path:
        os.remove(temp_path)
   
    print(f"✅ Detected {pest_count} insects")
    print(f"🚨 Risk Level: {risk}")
   
    return {
        "pest_count": pest_count,
        "risk_level": risk,
        "output_image": output_path,
        "predictions": prediction['predictions'],
        "input_format": original_ext
    }

# QUICKEST FOR HACKATHON: Use simple color detection
if __name__ == "__main__":
    # Test with different file formats
    # Works with: .jpg, .jpeg, .png, .webp, .bmp, .tiff
   
    print("🌱 PEST DETECTION SYSTEM - Multi-Format Support")
    print("Supported formats: JPG, PNG, WEBP, BMP, TIFF\n")
   
    # Method 1: Simple color-based (NO API needed, works immediately)
    print("🔍 Method 1: Color-based detection")
   
    # Try to find any image in current directory
    test_images = ["sticky_trap.jpg", "sticky_trap.png", "sticky_trap.webp"]
   
    for test_img in test_images:
        if os.path.exists(test_img):
            print(f"\n📸 Found image: {test_img}")
            try:
                result = detect_pests_simple(test_img)
                print(result)
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    else:
        print("⚠️ No test image found. Please provide: sticky_trap.jpg, sticky_trap.png, or sticky_trap.webp")
   
    # Method 2: Roboflow (better accuracy, needs free API key)
    # Uncomment below after getting Roboflow API key:
    # print("\n🔍 Method 2: Roboflow AI detection")
    # result = detect_pests_roboflow("sticky_trap.webp", "YOUR_API_KEY")
    # print(result)