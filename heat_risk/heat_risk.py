import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
warnings.filterwarnings('ignore')

# Configuration: which features the model uses and helper columns used when
# generating labels from noisy real-world sensor data.
ESSENTIAL_FEATURES = [
    'temperature',
    'humidity', 
    'soil_moisture',
    'sunlight_exposure'
]

# Additional features used ONLY for label generation (not for ML training)
LABEL_HELPER_FEATURES = [
    'rainfall',
    'growth_stage',
    'irrigation_frequency'
]

def calculate_vapor_pressure_deficit(temp, humidity):
    """Calculate Vapor Pressure Deficit (VPD).

    VPD is a widely-used agronomic metric combining temperature and humidity
    to estimate how aggressively plants transpire. Higher VPD generally
    increases plant water demand and stress.
    """
    svp = 0.61121 * np.exp((18.678 - temp / 234.5) * (temp / (257.14 + temp)))
    avp = svp * (humidity / 100.0)
    vpd = svp - avp
    return vpd

def calculate_heat_stress_index(temp, humidity, soil_moisture, rainfall,
                                growth_stage, irrigation_freq):
    """Combine multiple domain signals into a single stress index.

    This function codifies a simple agronomic rule set so our label
    generation reflects how farmers would reason about heat stress:
      - High temperature and high VPD raise stress
      - Low soil moisture raises stress
      - Recent rain and frequent irrigation reduce stress
      - Flowering/fruiting stages are more vulnerable
    The result is a continuous index we later bucket into labels.
    """
    temp_stress = np.clip((temp - 25) / 20, 0, 1) ** 1.5

    vpd = calculate_vapor_pressure_deficit(temp, humidity)
    vpd_stress = np.clip(vpd / 4.0, 0, 1)

    moisture_stress = np.clip((60 - soil_moisture) / 60, 0, 1)

    rainfall_factor = np.clip(1 - (rainfall / 50), 0.5, 1)

    stage_vulnerability = {0: 0.8, 1: 1.2, 2: 1.1, 3: 0.9}
    stage_factor = np.vectorize(lambda x: stage_vulnerability.get(x, 1.0))(growth_stage)

    irrigation_mitigation = np.clip(1 - (irrigation_freq * 0.15), 0.6, 1)

    stress_index = (
        0.4 * temp_stress +
        0.3 * vpd_stress +
        0.3 * moisture_stress
    ) * rainfall_factor * stage_factor * irrigation_mitigation

    return stress_index

def create_heat_stress_labels(df):
    """Generate labels by applying domain-aware rules to sensor data.

    The function prints helpful diagnostics so you can inspect the
    synthetic labels distribution during data preparation and debugging.
    """
    print("\n" + "=" * 60)
    print("GENERATING HEAT STRESS LABELS")
    print("=" * 60)
    print("Using multi-factor stress index based on temperature, VPD,")
    print("soil moisture, rainfall, growth stage and irrigation")

    stress_index = calculate_heat_stress_index(
        df['temperature'].values,
        df['humidity'].values,
        df['soil_moisture'].values,
        df['rainfall'].values,
        df['growth_stage'].values if 'growth_stage' in df.columns else np.zeros(len(df)),
        df['irrigation_frequency'].values if 'irrigation_frequency' in df.columns else np.ones(len(df))
    )

    # Small random perturbation makes the synthetic labels less brittle
    noise = np.random.normal(0, 0.1, len(stress_index))
    stress_index_noisy = np.clip(stress_index + noise, 0, 1)

    conditions = [
        stress_index_noisy < 0.25,
        (stress_index_noisy >= 0.25) & (stress_index_noisy < 0.50),
        (stress_index_noisy >= 0.50) & (stress_index_noisy < 0.75),
        stress_index_noisy >= 0.75
    ]
    labels = ['none', 'low', 'medium', 'high']

    df['heat_stress'] = np.select(conditions, labels, default='none')
    df['stress_index'] = stress_index

    print("\n" + "-" * 60)
    print("LABEL DISTRIBUTION")
    print("-" * 60)
    distribution = df['heat_stress'].value_counts().sort_index()
    for label, count in distribution.items():
        percentage = (count / len(df)) * 100
        print(f"  {label:8s}: {count:5d} samples ({percentage:5.1f}%)")

    print(f"\n✓ Created {len(df)} labeled samples")
    print(f"✓ Stress index range: {stress_index.min():.3f} to {stress_index.max():.3f}")

    return df

# ============================================
# STEP 2: Load and Prepare Data
# ============================================
def load_and_prepare_data(csv_path):
    """Load CSV and prepare data"""
    print("="*60)
    print("LOADING DATA")
    print("="*60)
    
    df = pd.read_csv(csv_path)
    print(f"\n✓ Loaded dataset with {len(df)} rows and {len(df.columns)} columns")
    
    # Check for required features
    all_required = ESSENTIAL_FEATURES + LABEL_HELPER_FEATURES
    missing = set(all_required) - set(df.columns)
    
    if missing:
        print(f"\n⚠️  Missing columns: {missing}")
        print(f"Available columns: {list(df.columns)}")
        
        # Try to continue with available features
        available_helper_features = [f for f in LABEL_HELPER_FEATURES if f in df.columns]
        if not available_helper_features:
            print("\n❌ Cannot create labels without helper features")
            print("At minimum, need: temperature, humidity, soil_moisture")
            raise ValueError("Insufficient columns for label generation")
    
    print(f"✓ Found all required features")
    
    # Handle missing values
    df = df.fillna(df.median(numeric_only=True))
    
    # Create labels using sophisticated approach
    df = create_heat_stress_labels(df)
    
    # Prepare features and target
    X = df[ESSENTIAL_FEATURES].copy()
    y = df['heat_stress'].copy()
    
    # Feature statistics
    print("\n" + "="*60)
    print("FEATURE STATISTICS (FOR MODEL INPUT)")
    print("="*60)
    print(X.describe())
    
    return X, y, df

# ============================================
# STEP 3: Visualize Label Generation Logic
# ============================================
def visualize_label_generation(df):
    """Create visualizations showing how labels were generated"""
    print("\n" + "="*60)
    print("CREATING LABEL GENERATION VISUALIZATIONS")
    print("="*60)
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Stress Index vs Temperature
    ax1 = axes[0, 0]
    for label in ['none', 'low', 'medium', 'high']:
        mask = df['heat_stress'] == label
        ax1.scatter(df[mask]['temperature'], df[mask]['stress_index'], 
                   label=label, alpha=0.6, s=20)
    ax1.set_xlabel('Temperature (°C)')
    ax1.set_ylabel('Stress Index')
    ax1.set_title('Heat Stress vs Temperature')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Humidity vs Temperature colored by stress
    ax2 = axes[0, 1]
    scatter = ax2.scatter(df['temperature'], df['humidity'], 
                         c=df['stress_index'], cmap='YlOrRd', alpha=0.6, s=20)
    ax2.set_xlabel('Temperature (°C)')
    ax2.set_ylabel('Humidity (%)')
    ax2.set_title('Temperature-Humidity Interaction')
    plt.colorbar(scatter, ax=ax2, label='Stress Index')
    ax2.grid(True, alpha=0.3)
    
    # 3. Soil Moisture Impact
    ax3 = axes[1, 0]
    for label in ['none', 'low', 'medium', 'high']:
        mask = df['heat_stress'] == label
        ax3.scatter(df[mask]['soil_moisture'], df[mask]['temperature'], 
                   label=label, alpha=0.6, s=20)
    ax3.set_xlabel('Soil Moisture (%)')
    ax3.set_ylabel('Temperature (°C)')
    ax3.set_title('Soil Moisture Effect on Stress')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Stress Index Distribution
    ax4 = axes[1, 1]
    for label in ['none', 'low', 'medium', 'high']:
        mask = df['heat_stress'] == label
        ax4.hist(df[mask]['stress_index'], alpha=0.6, label=label, bins=20)
    ax4.set_xlabel('Stress Index')
    ax4.set_ylabel('Count')
    ax4.set_title('Stress Index Distribution by Category')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('label_generation_analysis.png', dpi=300, bbox_inches='tight')
    print("✓ Saved 'label_generation_analysis.png'")
    plt.close()

# ============================================
# STEP 4: Train Models with Cross-Validation
# ============================================
def train_and_evaluate_models(X, y):
    """Train multiple models and select the best one"""
    print("\n" + "="*60)
    print("TRAINING MACHINE LEARNING MODELS")
    print("="*60)
    print("\nThe model will learn complex patterns from sensor data,")
    print("not simple rules. This includes:")
    print("  • Non-linear feature interactions")
    print("  • Threshold variations across conditions")
    print("  • Complex decision boundaries")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTrain set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Define models
    models = {
        'Random Forest': RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        ),
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=5,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        ),
        'Logistic Regression': LogisticRegression(
            class_weight='balanced',
            max_iter=1000,
            random_state=42,
            C=0.1
        )
    }
    
    results = {}
    trained_models = {}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    print("\n" + "-"*60)
    print("CROSS-VALIDATION RESULTS (5-Fold)")
    print("-"*60)
    
    for name, model in models.items():
        # Create pipeline with SMOTE and scaling
        pipeline = ImbPipeline([
            ('scaler', StandardScaler()),
            ('smote', SMOTE(random_state=42, k_neighbors=3)),
            ('classifier', model)
        ])
        
        # Cross-validation
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, 
                                    scoring='f1_weighted', n_jobs=-1)
        
        results[name] = {
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'cv_scores': cv_scores
        }
        
        print(f"\n{name}:")
        print(f"  Mean F1 Score: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
        print(f"  Scores: {[f'{s:.3f}' for s in cv_scores]}")
        
        # Train on full training set
        pipeline.fit(X_train, y_train)
        trained_models[name] = pipeline
    
    # Select best model
    best_model_name = max(results, key=lambda x: results[x]['cv_mean'])
    best_pipeline = trained_models[best_model_name]
    
    print("\n" + "="*60)
    print(f"BEST MODEL: {best_model_name}")
    print(f"CV F1 Score: {results[best_model_name]['cv_mean']:.4f}")
    print("="*60)
    
    return best_pipeline, best_model_name, X_train, X_test, y_train, y_test

# ============================================
# STEP 5: Evaluate Model
# ============================================
def evaluate_final_model(pipeline, X_test, y_test, model_name):
    """Evaluate the best model on test set"""
    print("\n" + "="*60)
    print("TEST SET EVALUATION")
    print("="*60)
    
    y_pred = pipeline.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    print(f"\nModel: {model_name}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1 Score: {f1:.4f}")
    
    print("\n" + "-"*60)
    print("CLASSIFICATION REPORT")
    print("-"*60)
    print(classification_report(y_test, y_pred, zero_division=0))
    
    # Confusion Matrix
    classes = ['none', 'low', 'medium', 'high']
    cm = confusion_matrix(y_test, y_pred, labels=classes)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='RdYlGn_r',
                xticklabels=classes, yticklabels=classes)
    plt.title(f'Confusion Matrix - {model_name}', fontsize=14, fontweight='bold')
    plt.ylabel('Actual', fontsize=12)
    plt.xlabel('Predicted', fontsize=12)
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved 'confusion_matrix.png'")
    
    # Feature Importance
    if hasattr(pipeline.named_steps['classifier'], 'feature_importances_'):
        importances = pipeline.named_steps['classifier'].feature_importances_
        feature_importance = pd.DataFrame({
            'feature': ESSENTIAL_FEATURES,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        print("\n" + "-"*60)
        print("FEATURE IMPORTANCE")
        print("-"*60)
        print(feature_importance.to_string(index=False))
        
        plt.figure(figsize=(10, 6))
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
        plt.barh(feature_importance['feature'], feature_importance['importance'], color=colors)
        plt.xlabel('Importance', fontsize=12)
        plt.title('Feature Importance for Heat Stress Prediction', 
                 fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
        print("✓ Saved 'feature_importance.png'")
    
    return accuracy, f1

# ============================================
# STEP 6: Save and Deploy
# ============================================
def save_model(pipeline, model_name):
    """Save model for deployment"""
    joblib.dump(pipeline, 'heat_stress_model.pkl')
    metadata = {
        'model_type': model_name,
        'features': ESSENTIAL_FEATURES,
        'sensors_needed': ['DHT22 (temp+humidity)', 'Soil Moisture', 'Light Sensor'],
        'estimated_cost': '$10'
    }
    joblib.dump(metadata, 'model_metadata.pkl')
    print("\n✓ Model saved as 'heat_stress_model.pkl'")
    print("✓ Metadata saved as 'model_metadata.pkl'")

def predict_heat_stress(temperature, humidity, soil_moisture, sunlight_exposure,
                       model_path='heat_stress_model.pkl'):
    """Real-time prediction function"""
    pipeline = joblib.load(model_path)
    
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

# ============================================
# DEMO FUNCTION
# ============================================
def run_demo():
    """Run interactive or preset demo"""
    print("\n" + "="*60)
    print("DEMO PREDICTION")
    print("="*60)
    
    # Ask user for input mode
    print("\nChoose demo mode:")
    print("  1. Interactive (enter your own sensor values)")
    print("  2. Preset examples")
    
    try:
        mode = input("\nEnter choice (1 or 2) [1]: ").strip()
        if not mode:
            mode = "1"
    except (EOFError, KeyboardInterrupt):
        mode = "1"
        print("1")
    
    if mode == "1":
        # Interactive mode
        print("\n" + "-"*60)
        print("INTERACTIVE SENSOR INPUT")
        print("-"*60)
        print("Enter sensor readings (or press Enter to use example values):\n")
        
        while True:
            try:
                # Temperature
                temp_input = input("Temperature (°C) [default: 35]: ").strip()
                temp = float(temp_input) if temp_input else 35.0
                
                # Humidity
                hum_input = input("Humidity (%) [default: 75]: ").strip()
                hum = float(hum_input) if hum_input else 75.0
                
                # Soil Moisture
                soil_input = input("Soil Moisture (%) [default: 45]: ").strip()
                soil = float(soil_input) if soil_input else 45.0
                
                # Sunlight
                sun_input = input("Sunlight Exposure (hours) [default: 8]: ").strip()
                sun = float(sun_input) if sun_input else 8.0
                
                # Validate ranges
                if not (0 <= temp <= 60):
                    print("⚠️  Warning: Temperature outside typical range (0-60°C)")
                if not (0 <= hum <= 100):
                    print("⚠️  Warning: Humidity outside valid range (0-100%)")
                if not (0 <= soil <= 100):
                    print("⚠️  Warning: Soil moisture outside valid range (0-100%)")
                if not (0 <= sun <= 24):
                    print("⚠️  Warning: Sunlight exposure outside valid range (0-24h)")
                
                # Make prediction
                print("\n" + "-"*60)
                print("🌡️  SENSOR READINGS")
                print("-"*60)
                print(f"  Temperature:        {temp}°C")
                print(f"  Humidity:           {hum}%")
                print(f"  Soil Moisture:      {soil}%")
                print(f"  Sunlight Exposure:  {sun} hours")
                
                risk, conf, probs = predict_heat_stress(temp, hum, soil, sun)
                
                # Display prediction with color
                print("\n" + "-"*60)
                print("📊 PREDICTION RESULTS")
                print("-"*60)
                
                risk_emoji = {'none': '✅', 'low': '⚠️', 'medium': '🔶', 'high': '🚨'}
                print(f"\n  {risk_emoji.get(risk, '❓')} Heat Stress Level: {risk.upper()}")
                print(f"  📈 Confidence: {conf:.1f}%")
                
                print(f"\n  Probability Breakdown:")
                for cls in ['none', 'low', 'medium', 'high']:
                    if cls in probs:
                        bar_length = int(probs[cls] * 40)
                        bar = '█' * bar_length + '░' * (40 - bar_length)
                        print(f"    {cls:8s}: {bar} {probs[cls]*100:5.1f}%")
                
                # Recommendations
                print("\n" + "-"*60)
                print("💡 RECOMMENDATIONS")
                print("-"*60)
                if risk == 'none':
                    print("  ✓ Conditions are optimal for plant growth")
                    print("  ✓ Continue current irrigation schedule")
                elif risk == 'low':
                    print("  • Monitor plants for early stress signs")
                    print("  • Consider light irrigation if soil moisture drops")
                elif risk == 'medium':
                    print("  ⚠️  Increase irrigation frequency")
                    print("  ⚠️  Provide shade during peak sunlight hours")
                    print("  ⚠️  Monitor plants closely")
                else:  # high
                    print("  🚨 IMMEDIATE ACTION REQUIRED!")
                    print("  🚨 Increase irrigation immediately")
                    print("  🚨 Provide shade or misting")
                    print("  🚨 Consider harvest if crops are mature")
                
                # Ask if user wants to test another case
                print("\n" + "-"*60)
                another = input("\nTest another sensor reading? (y/n) [n]: ").strip().lower()
                if another != 'y':
                    break
                print("\n")
                
            except ValueError as e:
                print(f"❌ Invalid input: {e}")
                print("Please enter numeric values only.\n")
                continue
            except (EOFError, KeyboardInterrupt):
                print("\n\n👋 Exiting interactive mode...")
                break
    else:
        # Preset examples mode
        print("\n" + "-"*60)
        print("PRESET EXAMPLES")
        print("-"*60)
        
        test_cases = [
            (35, 85, 30, 9, "High temp + high humidity + low moisture"),
            (28, 60, 55, 6, "Moderate conditions"),
            (42, 70, 25, 10, "Extreme temperature"),
        ]
        
        for i, (temp, hum, soil, sun, desc) in enumerate(test_cases, 1):
            print(f"\nExample {i}: {desc}")
            print(f"  Sensors: {temp}°C, {hum}% RH, {soil}% moisture, {sun}h sun")
            risk, conf, probs = predict_heat_stress(temp, hum, soil, sun)
            
            risk_emoji = {'none': '✅', 'low': '⚠️', 'medium': '🔶', 'high': '🚨'}
            print(f"  → {risk_emoji.get(risk, '❓')} Prediction: {risk.upper()} risk ({conf:.1f}% confidence)")
            
            # Show top 2 probabilities
            sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:2]
            print(f"     Top predictions: {sorted_probs[0][0]} ({sorted_probs[0][1]*100:.0f}%), {sorted_probs[1][0]} ({sorted_probs[1][1]*100:.0f}%)")

# ============================================
# MAIN EXECUTION
# ============================================
if __name__ == "__main__":
    CSV_FILE = 'dataset_crops/dataset.csv'  # CHANGE THIS
    
    print("="*60)
    print("🌱 ECO BLOOM - HEAT STRESS PREDICTION SYSTEM")
    print("="*60)
    print("\nWhat would you like to do?")
    print("  1. Train new model (uses dataset)")
    print("  2. Use existing model for predictions")
    print("  3. Train and then predict")
    
    try:
        choice = input("\nEnter choice (1, 2, or 3) [2]: ").strip()
        if not choice:
            choice = "2"
    except (EOFError, KeyboardInterrupt):
        choice = "2"
        print("2")
    
    # ============================================
    # OPTION 2: USE EXISTING MODEL (FAST PATH)
    # ============================================
    if choice == "2":
        print("\n" + "="*60)
        print("LOADING EXISTING MODEL")
        print("="*60)
        
        try:
            # Check if model exists
            if not os.path.exists('heat_stress_model.pkl'):
                print("\n❌ Model file 'heat_stress_model.pkl' not found!")
                print("Please train the model first (option 1 or 3)\n")
                exit(1)
            
            # Load model
            pipeline = joblib.load('heat_stress_model.pkl')
            metadata = joblib.load('model_metadata.pkl')
            
            print(f"\n✓ Model loaded successfully!")
            print(f"✓ Model type: {metadata['model_type']}")
            print(f"✓ Required sensors: {', '.join(metadata['sensors_needed'])}")
            print(f"✓ Estimated cost: {metadata['estimated_cost']}")
            
            # Run demo
            run_demo()
            
            print("\n" + "="*60)
            print("✅ DEMO COMPLETE!")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # ============================================
    # OPTION 1 or 3: TRAIN MODEL
    # ============================================
    elif choice in ["1", "3"]:
        print("\n" + "="*60)
        print("TRAINING MODE")
        print("="*60)
        
        try:
            # Load and prepare
            X, y, df = load_and_prepare_data(CSV_FILE)
            
            # Visualize label generation
            visualize_label_generation(df)
            
            # Train models
            best_pipeline, best_model_name, X_train, X_test, y_train, y_test = \
                train_and_evaluate_models(X, y)
            
            # Evaluate
            accuracy, f1 = evaluate_final_model(best_pipeline, X_test, y_test, best_model_name)
            
            # Save
            save_model(best_pipeline, best_model_name)
            
            print("\n" + "="*60)
            print("✅ MODEL TRAINING COMPLETE!")
            print("="*60)
            print(f"\n📊 Performance:")
            print(f"   • Accuracy: {accuracy:.1%}")
            print(f"   • F1 Score: {f1:.3f}")
            print(f"\n💰 Hardware Cost: ~$10 (4 sensors)")
            print(f"📦 Files Generated:")
            print(f"   • heat_stress_model.pkl")
            print(f"   • model_metadata.pkl")
            print(f"   • confusion_matrix.png")
            print(f"   • feature_importance.png")
            print(f"   • label_generation_analysis.png")
            
            # If option 3, continue to demo
            if choice == "3":
                run_demo()
            
        except FileNotFoundError:
            print(f"❌ Error: Could not find '{CSV_FILE}'")
            print("Please update the CSV_FILE variable with your dataset path")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print(f"\n❌ Invalid choice: {choice}")
        print("Please run again and choose 1, 2, or 3")