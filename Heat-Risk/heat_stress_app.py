from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)
CORS(app)

# Load model at startup
MODEL_PATH = 'heat_stress_model.pkl'
METADATA_PATH = 'model_metadata.pkl'

try:
    pipeline = joblib.load(MODEL_PATH)
    metadata = joblib.load(METADATA_PATH)
    print("✓ Heat stress model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    pipeline = None
    metadata = None

def predict_heat_stress(temperature, humidity, soil_moisture, sunlight_exposure):
    """Make prediction using loaded model"""
    if pipeline is None:
        raise ValueError("Model not loaded")
    
    input_df = pd.DataFrame([{
        'temperature': temperature,
        'humidity': humidity,
        'soil_moisture': soil_moisture,
        'sunlight_exposure': sunlight_exposure
    }])
    
    prediction = pipeline.predict(input_df)[0]
    probabilities = pipeline.predict_proba(input_df)[0]
    confidence = max(probabilities) * 100
    
    class_probs = dict(zip(pipeline.classes_, probabilities))
    
    return prediction, confidence, class_probs

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Extract sensor values
        temperature = float(data['temperature'])
        humidity = float(data['humidity'])
        soil_moisture = float(data['soil_moisture'])
        sunlight_exposure = float(data['sunlight_exposure'])
        
        # Validate ranges
        if not (0 <= temperature <= 60):
            return jsonify({'error': 'Temperature must be between 0-60°C'}), 400
        if not (0 <= humidity <= 100):
            return jsonify({'error': 'Humidity must be between 0-100%'}), 400
        if not (0 <= soil_moisture <= 100):
            return jsonify({'error': 'Soil moisture must be between 0-100%'}), 400
        if not (0 <= sunlight_exposure <= 24):
            return jsonify({'error': 'Sunlight exposure must be between 0-24 hours'}), 400
        
        # Make prediction
        risk_level, confidence, class_probs = predict_heat_stress(
            temperature, humidity, soil_moisture, sunlight_exposure
        )
        
        # Generate recommendations
        recommendations = {
            'none': [
                'Conditions are optimal for plant growth',
                'Continue current irrigation schedule',
                'Regular monitoring is sufficient'
            ],
            'low': [
                'Monitor plants for early stress signs',
                'Consider light irrigation if soil moisture drops',
                'Check plants twice weekly'
            ],
            'medium': [
                'Increase irrigation frequency',
                'Provide shade during peak sunlight hours',
                'Monitor plants closely daily',
                'Consider misting in extreme heat'
            ],
            'high': [
                'IMMEDIATE ACTION REQUIRED!',
                'Increase irrigation immediately',
                'Provide shade or misting',
                'Consider early harvest if crops are mature',
                'Inspect for heat damage'
            ]
        }
        
        return jsonify({
            'risk_level': risk_level,
            'confidence': confidence,
            'probabilities': class_probs,
            'recommendations': recommendations[risk_level],
            'sensor_readings': {
                'temperature': temperature,
                'humidity': humidity,
                'soil_moisture': soil_moisture,
                'sunlight_exposure': sunlight_exposure
            },
            'details': f'Detected {risk_level.upper()} heat stress risk based on sensor analysis using {metadata["model_type"] if metadata else "ML model"}'
        })
        
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    model_status = 'loaded' if pipeline is not None else 'not loaded'
    return jsonify({
        'status': 'ok',
        'message': 'Heat stress prediction API is running',
        'model_status': model_status,
        'model_type': metadata['model_type'] if metadata else None
    })

if __name__ == '__main__':
    print("="*60)
    print("🌱 ECO BLOOM - HEAT STRESS PREDICTION API")
    print("="*60)
    print("\nServer running at http://localhost:5001")
    print("Make sure heat_stress_model.pkl exists in the same directory!")
    print("\nEndpoints:")
    print("  POST /predict - Make heat stress predictions")
    print("  GET  /health  - Check API status")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5001)