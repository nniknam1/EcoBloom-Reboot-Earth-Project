from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from PIL import Image
import io
import base64

app = Flask(__name__)
CORS(app)  # Allow requests from web page

def detect_pests_opencv(image_array):
    """
    Your original OpenCV pest detection logic
    """
    # Convert to HSV
    hsv = cv2.cvtColor(image_array, cv2.COLOR_BGR2HSV)
    
    # Define range for dark objects (insects on yellow traps)
    lower_dark = np.array([0, 0, 0])
    upper_dark = np.array([180, 255, 100])
    
    # Create mask for dark objects
    mask = cv2.inRange(hsv, lower_dark, upper_dark)
    
    # Remove noise with morphological operations
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter by size
    min_area = 20
    max_area = 5000
    valid_pests = []
    
    for idx, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if min_area < area < max_area:
            valid_pests.append(contour)
            # Draw circle around pest
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            cv2.circle(image_array, center, radius, (0, 255, 0), 3)
            
            # Add label
            label = f'Pest {len(valid_pests)}'
            # Label background
            (text_width, text_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            cv2.rectangle(
                image_array,
                (center[0] - text_width//2 - 5, center[1] - radius - 35),
                (center[0] + text_width//2 + 5, center[1] - radius - 10),
                (0, 255, 0),
                -1
            )
            # Label text
            cv2.putText(
                image_array, label,
                (center[0] - text_width//2, center[1] - radius - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
            )
    
    pest_count = len(valid_pests)
    
    # Calculate risk level
    if pest_count <= 2:
        risk = "LOW"
    elif pest_count <= 5:
        risk = "MEDIUM"
    else:
        risk = "HIGH"
    
    return image_array, pest_count, risk

@app.route('/detect', methods=['POST'])
def detect_pests():
    try:
        # Get base64 image from request
        data = request.json
        image_base64 = data['image']
        
        # Remove data URL prefix if present
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        # Decode base64 to image
        image_data = base64.b64decode(image_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Run detection
        labeled_img, pest_count, risk = detect_pests_opencv(img.copy())
        
        # Encode result image back to base64
        _, buffer = cv2.imencode('.jpg', labeled_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'pest_count': pest_count,
            'risk_level': risk,
            'labeled_image': f'data:image/jpeg;base64,{img_base64}',
            'details': f'Detected {pest_count} pest(s) using OpenCV contour detection with morphological operations'
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Pest detection API is running'})

if __name__ == '__main__':
    print("Starting Eco Bloom Pest Detection API...")
    print("Server running at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)