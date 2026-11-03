"""
Rockfall Early Warning and Response Coordination System
Machine Learning Training and Evaluation Pipeline

This module implements:
1. Generation / Loading of synthetic geological sensor data (clearly labeled for academic demonstration)
2. Data preprocessing & feature encoding preventing data leakage
3. Train/Test split & 5-Fold Stratified Cross Validation
4. Primary Model: Random Forest Classifier
5. Comparison Model: Decision Tree Classifier
6. Model evaluation: Accuracy, Precision, Recall, F1-Score, Confusion Matrix
7. Matplotlib visualizations: Confusion Matrix and Feature Importance plots
8. Model serialization with Joblib
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')  # Headless backend for web/server environments
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
IMG_DIR = os.path.join(BASE_DIR, 'static', 'img')

DATA_PATH = os.path.join(DATA_DIR, 'sample_dataset.csv')
MODEL_PATH = os.path.join(MODELS_DIR, 'rockfall_model.pkl')
METRICS_PATH = os.path.join(MODELS_DIR, 'model_metrics.json')

# Standard geological condition ratings (vulnerability weight)
GEO_CONDITION_MAP = {
    'Stable Bedrock': 1,
    'Jointed Basalt': 2,
    'Fractured Limestone': 3,
    'Weathered Sandstone': 4,
    'Loose Shale & Siltstone': 5,
    'Active Fault Zone': 6
}

NUMERICAL_FEATURES = [
    'rainfall_mm',
    'slope_angle_deg',
    'vibration_intensity',
    'soil_moisture_pct',
    'displacement_rate_mm_day',
    'rock_movement_mm'
]

ALL_FEATURES = NUMERICAL_FEATURES + ['geo_vulnerability']
TARGET_CLASSES = ['Low Risk', 'Medium Risk', 'High Risk']


def generate_synthetic_dataset(n_samples=1000, random_state=42):
    """
    Generates a geotechnically realistic synthetic dataset for rockfall hazard classification.
    Clearly labeled for academic demonstration purposes.
    """
    np.random.seed(random_state)
    os.makedirs(DATA_DIR, exist_ok=True)

    conditions = list(GEO_CONDITION_MAP.keys())
    geo_conditions = np.random.choice(conditions, size=n_samples, p=[0.18, 0.20, 0.22, 0.18, 0.14, 0.08])

    rainfall = np.random.gamma(shape=2.5, scale=22.0, size=n_samples)  # 0 to 200+ mm
    rainfall = np.clip(rainfall, 0.0, 240.0)

    slope_angle = np.random.normal(loc=55.0, scale=12.0, size=n_samples)  # 25 to 85 deg
    slope_angle = np.clip(slope_angle, 25.0, 85.0)

    vibration = np.random.exponential(scale=2.2, size=n_samples)  # 0 to 12 mm/s
    vibration = np.clip(vibration, 0.0, 14.0)

    soil_moisture = 15.0 + (rainfall * 0.28) + np.random.normal(0, 7.0, size=n_samples)
    soil_moisture = np.clip(soil_moisture, 10.0, 95.0)

    # Displacement rate correlates with slope, rainfall, and moisture
    displacement_rate = (
        (slope_angle / 85.0) * 4.0 +
        (rainfall / 200.0) * 8.0 +
        (soil_moisture / 95.0) * 5.0 +
        (vibration / 14.0) * 4.0 +
        np.random.normal(0, 1.5, size=n_samples)
    )
    displacement_rate = np.clip(displacement_rate, 0.1, 35.0)

    rock_movement = displacement_rate * np.random.uniform(1.2, 2.5, size=n_samples) + np.random.normal(0, 1.0, size=n_samples)
    rock_movement = np.clip(rock_movement, 0.2, 50.0)

    # Geotechnical Hazard Score calculation (Driving / Resisting intuition)
    vulnerability = np.array([GEO_CONDITION_MAP[g] for g in geo_conditions])

    hazard_score = (
        (rainfall / 150.0) * 30.0 +
        (slope_angle / 75.0) * 25.0 +
        (vibration / 10.0) * 15.0 +
        (soil_moisture / 85.0) * 20.0 +
        (displacement_rate / 15.0) * 35.0 +
        (rock_movement / 25.0) * 30.0 +
        (vulnerability / 6.0) * 25.0 +
        np.random.normal(0, 3.5, size=n_samples)  # calibrated geotechnical variance
    )

    # Classify into 3 distinct categories: Low Risk, Medium Risk, High Risk
    risk_labels = []
    p33 = np.percentile(hazard_score, 35)
    p66 = np.percentile(hazard_score, 70)

    for score in hazard_score:
        if score < p33:
            risk_labels.append('Low Risk')
        elif score < p66:
            risk_labels.append('Medium Risk')
        else:
            risk_labels.append('High Risk')

    df = pd.DataFrame({
        'rainfall_mm': np.round(rainfall, 1),
        'slope_angle_deg': np.round(slope_angle, 1),
        'vibration_intensity': np.round(vibration, 2),
        'soil_moisture_pct': np.round(soil_moisture, 1),
        'displacement_rate_mm_day': np.round(displacement_rate, 2),
        'rock_movement_mm': np.round(rock_movement, 2),
        'geological_condition': geo_conditions,
        'risk_level': risk_labels,
        'data_source_label': 'Curated Academic Demonstration Dataset (Synthetic Geotechnical Model)'
    })

    df.to_csv(DATA_PATH, index=False)
    print(f"[Dataset] Generated {n_samples} samples and saved to: {DATA_PATH}")
    return df


def load_and_preprocess_data(force_regenerate=False):
    """Loads dataset and preprocesses features safely without data leakage."""
    if force_regenerate or not os.path.exists(DATA_PATH):
        df = generate_synthetic_dataset()
    else:
        df = pd.read_csv(DATA_PATH)

    # Check for missing values and clean
    df = df.dropna(subset=NUMERICAL_FEATURES + ['geological_condition', 'risk_level'])

    # Map geological condition to ordinal vulnerability
    df['geo_vulnerability'] = df['geological_condition'].map(GEO_CONDITION_MAP).fillna(3)

    X = df[ALL_FEATURES].copy()
    y = df['risk_level'].copy()

    return X, y, df


def train_and_evaluate_models():
    """
    Trains Random Forest and Decision Tree models with 5-Fold Stratified Cross Validation.
    Computes performance metrics and saves artifacts.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)

    X, y, df = load_and_preprocess_data()

    # 80-20 Train-Test split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Standardize numerical features using pipeline scaler fitted ONLY on training set
    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()

    X_train_scaled[NUMERICAL_FEATURES] = scaler.fit_transform(X_train[NUMERICAL_FEATURES])
    X_test_scaled[NUMERICAL_FEATURES] = scaler.transform(X_test[NUMERICAL_FEATURES])

    # 1. Primary Model: Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=120,
        max_depth=10,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )

    # 2. Comparison Model: Decision Tree Classifier
    dt_model = DecisionTreeClassifier(
        max_depth=6,
        min_samples_split=5,
        min_samples_leaf=3,
        random_state=42,
        class_weight='balanced'
    )

    # 5-Fold Stratified Cross-Validation on training data
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    rf_cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=cv, scoring='accuracy')
    dt_cv_scores = cross_val_score(dt_model, X_train_scaled, y_train, cv=cv, scoring='accuracy')

    # Fit final models on entire training split
    rf_model.fit(X_train_scaled, y_train)
    dt_model.fit(X_train_scaled, y_train)

    # Predictions on holdout test set
    rf_pred = rf_model.predict(X_test_scaled)
    dt_pred = dt_model.predict(X_test_scaled)

    # Evaluate metrics
    rf_acc = accuracy_score(y_test, rf_pred)
    rf_prec = precision_score(y_test, rf_pred, average='weighted')
    rf_rec = recall_score(y_test, rf_pred, average='weighted')
    rf_f1 = f1_score(y_test, rf_pred, average='weighted')
    rf_cm = confusion_matrix(y_test, rf_pred, labels=TARGET_CLASSES)

    dt_acc = accuracy_score(y_test, dt_pred)
    dt_prec = precision_score(y_test, dt_pred, average='weighted')
    dt_rec = recall_score(y_test, dt_pred, average='weighted')
    dt_f1 = f1_score(y_test, dt_pred, average='weighted')
    dt_cm = confusion_matrix(y_test, dt_pred, labels=TARGET_CLASSES)

    # Feature Importance for Random Forest
    importances = rf_model.feature_importances_
    feature_imp_dict = {feat: float(imp) for feat, imp in zip(ALL_FEATURES, importances)}
    # Sort descending
    sorted_features = sorted(feature_imp_dict.items(), key=lambda x: x[1], reverse=True)

    # Save Confusion Matrix Plot
    plot_confusion_matrix(rf_cm, TARGET_CLASSES, os.path.join(IMG_DIR, 'confusion_matrix.png'))
    plot_feature_importance(sorted_features, os.path.join(IMG_DIR, 'feature_importance.png'))

    # Prepare metadata dictionary
    metrics = {
        'primary_model': 'Random Forest Classifier',
        'comparison_model': 'Decision Tree Classifier',
        'sample_count': len(df),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'target_classes': TARGET_CLASSES,
        'features': ALL_FEATURES,
        'random_forest': {
            'accuracy': round(float(rf_acc), 4),
            'precision': round(float(rf_prec), 4),
            'recall': round(float(rf_rec), 4),
            'f1_score': round(float(rf_f1), 4),
            'cv_mean_accuracy': round(float(np.mean(rf_cv_scores)), 4),
            'cv_std': round(float(np.std(rf_cv_scores)), 4),
            'cv_scores': [round(float(s), 4) for s in rf_cv_scores],
            'confusion_matrix': rf_cm.tolist()
        },
        'decision_tree': {
            'accuracy': round(float(dt_acc), 4),
            'precision': round(float(dt_prec), 4),
            'recall': round(float(dt_rec), 4),
            'f1_score': round(float(dt_f1), 4),
            'cv_mean_accuracy': round(float(np.mean(dt_cv_scores)), 4),
            'cv_std': round(float(np.std(dt_cv_scores)), 4),
            'cv_scores': [round(float(s), 4) for s in dt_cv_scores],
            'confusion_matrix': dt_cm.tolist()
        },
        'feature_importance': {k: round(v, 4) for k, v in sorted_features},
        'disclaimer': 'Demonstration Model: Trained on curated synthetic geotechnical sensor distributions adhering to rock slope stability physics. Not calibrated for operational life-safety deployment without verified site-specific sensor telemetry.'
    }

    # Save metrics JSON
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=4)

    # Save Model Bundle with Joblib
    model_bundle = {
        'rf_model': rf_model,
        'dt_model': dt_model,
        'scaler': scaler,
        'numerical_features': NUMERICAL_FEATURES,
        'all_features': ALL_FEATURES,
        'geo_mapping': GEO_CONDITION_MAP,
        'target_classes': TARGET_CLASSES,
        'metrics': metrics
    }
    joblib.dump(model_bundle, MODEL_PATH)

    print("\n" + "="*60)
    print("MODEL TRAINING AND EVALUATION REPORT")
    print("="*60)
    print(f"Dataset Size: {len(df)} samples (80% Train: {len(X_train)}, 20% Test: {len(X_test)})")
    print("\n1. Random Forest (Primary Model):")
    print(f"   Accuracy:  {rf_acc * 100:.2f}%")
    print(f"   Precision: {rf_prec * 100:.2f}%")
    print(f"   Recall:    {rf_rec * 100:.2f}%")
    print(f"   F1-Score:  {rf_f1 * 100:.2f}%")
    print(f"   5-Fold CV: {np.mean(rf_cv_scores)*100:.2f}% (+/- {np.std(rf_cv_scores)*100:.2f}%)")
    print("\n2. Decision Tree (Comparison Model):")
    print(f"   Accuracy:  {dt_acc * 100:.2f}%")
    print(f"   F1-Score:  {dt_f1 * 100:.2f}%")
    print(f"   5-Fold CV: {np.mean(dt_cv_scores)*100:.2f}%")
    print(f"\nArtifacts successfully saved to:")
    print(f" - Model file:   {MODEL_PATH}")
    print(f" - Metrics file: {METRICS_PATH}")
    print(f" - Visuals:      {IMG_DIR}")
    print("="*60 + "\n")

    return metrics


def plot_confusion_matrix(cm, classes, output_path):
    """Generates and saves a clean, dark-blue themed confusion matrix chart."""
    plt.figure(figsize=(6, 5), dpi=150)
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Random Forest - Confusion Matrix', fontsize=12, fontweight='bold', pad=12, color='#0f2b48')
    plt.colorbar()

    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, fontsize=9, color='#1e293b')
    plt.yticks(tick_marks, classes, fontsize=9, color='#1e293b')

    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            color = "white" if val > thresh else "#0f2b48"
            plt.text(j, i, format(val, 'd'),
                     ha="center", va="center",
                     fontsize=11, fontweight='bold',
                     color=color)

    plt.ylabel('Actual True Risk', fontsize=10, fontweight='bold', color='#0f2b48')
    plt.xlabel('Predicted Risk', fontsize=10, fontweight='bold', color='#0f2b48')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def plot_feature_importance(sorted_features, output_path):
    """Generates and saves a bar chart showing relative feature importance."""
    features = [f[0].replace('_', ' ').title() for f in sorted_features]
    scores = [f[1] * 100 for f in sorted_features]

    plt.figure(figsize=(7, 4.5), dpi=150)
    y_pos = np.arange(len(features))
    
    # Modern dark blue / cyan bar style
    bars = plt.barh(y_pos, scores, align='center', color='#1a365d', edgecolor='#0f2b48')
    plt.yticks(y_pos, features, fontsize=9, color='#1e293b')
    plt.gca().invert_yaxis()  # top feature on top
    plt.xlabel('Relative Feature Importance (%)', fontsize=10, fontweight='bold', color='#0f2b48')
    plt.title('Supervised Model - Feature Importance (XAI)', fontsize=12, fontweight='bold', pad=12, color='#0f2b48')

    # Add data labels
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.8, bar.get_y() + bar.get_height()/2.0,
                 f"{width:.1f}%",
                 ha='left', va='center', fontsize=9, fontweight='bold', color='#1a365d')

    plt.xlim(0, max(scores) + 8)
    plt.grid(axis='x', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


if __name__ == '__main__':
    print("Training Rockfall Hazard Classification Pipeline...")
    train_and_evaluate_models()
