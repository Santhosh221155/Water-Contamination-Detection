"""
Water Quality ML Model Training Script
Trains a Random Forest classifier on Tamil Nadu water quality parameters
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent

# Tamil Nadu water quality parameter ranges
PARAM_RANGES = {
    'pH': {'min': 5.5, 'max': 8.8, 'safe_min': 6.5, 'safe_max': 8.5},
    'Sulphate': {'min': 69, 'max': 496, 'safe_min': 100, 'safe_max': 400},
    'Hardness': {'min': 66, 'max': 281, 'safe_min': 80, 'safe_max': 250},
    'Conductivity': {'min': 152, 'max': 895, 'safe_min': 200, 'safe_max': 800},
    'TDS': {'min': 137, 'max': 1178, 'safe_min': 200, 'safe_max': 1000},
    'Turbidity': {'min': 1.3, 'max': 9.4, 'safe_min': 1.5, 'safe_max': 5.0}
}

def generate_synthetic_data(n_samples=5000):
    """
    Generate balanced synthetic water quality dataset (50% Safe, 50% Unsafe)
    """
    data = []
    n_safe = n_samples // 2
    n_unsafe = n_samples - n_safe
    
    print(f"   Generating {n_safe} Safe and {n_unsafe} Unsafe samples...")

    # 1. Generate Safe Samples (All parameters within safe ranges)
    for _ in range(n_safe):
        sample = {}
        for param, ranges in PARAM_RANGES.items():
            sample[param] = np.random.uniform(ranges['safe_min'], ranges['safe_max'])
        sample['is_safe'] = 1
        data.append(sample)

    # 2. Generate Unsafe Samples (At least one parameter out of range)
    for _ in range(n_unsafe):
        sample = {}
        # First, generate random values for all parameters
        for param, ranges in PARAM_RANGES.items():
            sample[param] = np.random.uniform(ranges['min'], ranges['max'])
        
        # Force at least one parameter to be unsafe
        unsafe_param = np.random.choice(list(PARAM_RANGES.keys()))
        ranges = PARAM_RANGES[unsafe_param]
        
        # Decide whether to go below min or above max
        if np.random.random() < 0.5:
            # Go low (but stay within physical min)
            if ranges['min'] < ranges['safe_min']:
                sample[unsafe_param] = np.random.uniform(ranges['min'], ranges['safe_min'] - 0.01)
        else:
            # Go high (but stay within physical max)
            if ranges['max'] > ranges['safe_max']:
                sample[unsafe_param] = np.random.uniform(ranges['safe_max'] + 0.01, ranges['max'])
                
        sample['is_safe'] = 0
        data.append(sample)
    
    # Shuffle the dataset
    df = pd.DataFrame(data)
    return df.sample(frac=1).reset_index(drop=True)

def train_model():
    """
    Train Random Forest classifier on water quality data
    """
    print("🔬 Generating synthetic water quality dataset...")
    df = generate_synthetic_data(n_samples=5000)
    
    # Save dataset
    dataset_path = SCRIPT_DIR / 'water_quality_dataset.csv'
    df.to_csv(dataset_path, index=False)
    print(f"✅ Dataset saved: {len(df)} samples")
    print(f"   Safe samples: {df['is_safe'].sum()}")
    print(f"   Unsafe samples: {len(df) - df['is_safe'].sum()}")
    
    # Prepare features and labels
    X = df[['pH', 'Sulphate', 'Hardness', 'Conductivity', 'TDS', 'Turbidity']]
    y = df['is_safe']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("\n🤖 Training Random Forest classifier...")
    # Train model
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✅ Model Training Complete!")
    print(f"   Accuracy: {accuracy * 100:.2f}%")
    print("\n📊 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Unsafe', 'Safe']))
    
    print("\n🔢 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"   True Negatives:  {cm[0][0]}")
    print(f"   False Positives: {cm[0][1]}")
    print(f"   False Negatives: {cm[1][0]}")
    print(f"   True Positives:  {cm[1][1]}")
    
    # Feature importance
    print("\n🎯 Feature Importance:")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    for _, row in feature_importance.iterrows():
        print(f"   {row['feature']:15s}: {row['importance']:.4f}")
    
    # Save model
    model_path = SCRIPT_DIR / 'tamilnadu_water_model.joblib'
    joblib.dump(model, model_path)
    print(f"\n💾 Model saved as '{model_path}'")
    
    return model

if __name__ == "__main__":
    print("=" * 60)
    print("Tamil Nadu Water Quality Model Training")
    print("=" * 60)
    model = train_model()
    print("\n" + "=" * 60)
    print("✨ Training Complete! Ready for deployment.")
    print("=" * 60)
