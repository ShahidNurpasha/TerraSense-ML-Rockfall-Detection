"""
Rockfall Early Warning and Response Coordination System
Prediction Engine (Machine Learning Inference & XAI)

This module handles:
1. Loading the pre-trained Joblib model bundle and preprocessors
2. Real-time inference on manual sensor inputs
3. Probability and confidence calculation
4. Explainable AI (XAI) feature contribution analysis for decision support
5. Batch prediction on uploaded CSV datasets
"""

import os
import joblib
import numpy as np
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'rockfall_model.pkl')

# Cache the loaded bundle in memory for fast response times
_model_bundle = None


def get_model_bundle():
    """Loads and caches the model bundle from disk."""
    global _model_bundle
    if _model_bundle is None:
        if not os.path.exists(MODEL_PATH):
            from model import train_and_evaluate_models
            train_and_evaluate_models()
        _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle


def reload_model_bundle():
    """Forces reloading the model bundle from disk after retraining."""
    global _model_bundle
    _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle


def predict_risk(sensor_data):
    """
    Performs inference for a single sensor reading dictionary.

    Input sensor_data dict should have:
    - rainfall_mm: float
    - slope_angle_deg: float
    - vibration_intensity: float
    - soil_moisture_pct: float
    - displacement_rate_mm_day: float
    - rock_movement_mm: float
    - geological_condition: str

    Returns:
    - predicted_risk: 'Low Risk', 'Medium Risk', or 'High Risk'
    - confidence: float (0.0 to 1.0)
    - probabilities: dict of {class_name: float}
    - feature_contributions: list of dicts with feature explanation (XAI)
    - comparison_prediction: prediction from Decision Tree
    """
    bundle = get_model_bundle()
    rf_model = bundle['rf_model']
    dt_model = bundle['dt_model']
    scaler = bundle['scaler']
    num_features = bundle['numerical_features']
    geo_map = bundle['geo_mapping']
    classes = list(rf_model.classes_)

    # Extract & validate values
    try:
        rainfall = float(sensor_data.get('rainfall_mm', 0.0))
        slope = float(sensor_data.get('slope_angle_deg', 45.0))
        vibration = float(sensor_data.get('vibration_intensity', 0.0))
        moisture = float(sensor_data.get('soil_moisture_pct', 20.0))
        disp_rate = float(sensor_data.get('displacement_rate_mm_day', 0.0))
        rock_mov = float(sensor_data.get('rock_movement_mm', 0.0))
        geo_cond = str(sensor_data.get('geological_condition', 'Stable Bedrock'))
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid sensor input data: {str(e)}")

    geo_vuln = float(geo_map.get(geo_cond, 3))

    # Construct DataFrame with proper feature names to avoid sklearn feature name warnings
    num_df = pd.DataFrame([[rainfall, slope, vibration, moisture, disp_rate, rock_mov]], columns=num_features)
    num_scaled = scaler.transform(num_df)

    feature_df = pd.DataFrame(
        np.hstack([num_scaled, [[geo_vuln]]]),
        columns=bundle['all_features']
    )

    # Inference with primary model (Random Forest)
    pred_class = rf_model.predict(feature_df)[0]
    probabilities_raw = rf_model.predict_proba(feature_df)[0]
    probabilities = {cls: round(float(prob), 4) for cls, prob in zip(classes, probabilities_raw)}
    confidence = round(float(np.max(probabilities_raw)), 4)

    # Comparison model inference (Decision Tree)
    dt_pred = dt_model.predict(feature_df)[0]

    # Explainable AI (XAI): Calculate relative contribution of each feature to the risk score
    # We combine global feature importances with normalized feature severity
    importances = bundle['metrics']['feature_importance']
    
    # Feature baseline / reference thresholds for explanation
    benchmarks = {
        'displacement_rate_mm_day': (disp_rate, 15.0, 'Displacement Rate', 'mm/day'),
        'rainfall_mm': (rainfall, 100.0, 'Rainfall Intensity', 'mm/24h'),
        'rock_movement_mm': (rock_mov, 20.0, 'Rock Movement', 'mm'),
        'soil_moisture_pct': (moisture, 75.0, 'Soil Moisture', '%'),
        'slope_angle_deg': (slope, 65.0, 'Slope Angle', '°'),
        'vibration_intensity': (vibration, 7.0, 'Vibration (PPV)', 'mm/s'),
        'geo_vulnerability': (geo_vuln, 4.0, 'Geological Vulnerability', f'({geo_cond})')
    }

    contributions = []
    for key, (val, bench, label, unit) in benchmarks.items():
        imp = importances.get(key, 0.1)
        ratio = val / max(bench, 1.0)
        # Severity weighted by model feature importance
        severity_score = imp * ratio
        impact_level = 'High' if ratio >= 1.0 else ('Moderate' if ratio >= 0.6 else 'Low')
        
        contributions.append({
            'key': key,
            'label': label,
            'value': val,
            'unit': unit,
            'importance_pct': round(imp * 100, 1),
            'impact_level': impact_level,
            'ratio_to_benchmark': round(ratio, 2),
            'severity_score': round(severity_score, 3)
        })

    # Sort descending by severity score for Explainable AI output
    contributions.sort(key=lambda x: x['severity_score'], reverse=True)

    return {
        'predicted_risk': pred_class,
        'confidence': confidence,
        'confidence_pct': round(confidence * 100, 1),
        'probabilities': probabilities,
        'comparison_prediction': dt_pred,
        'feature_contributions': contributions,
        'raw_inputs': {
            'rainfall_mm': rainfall,
            'slope_angle_deg': slope,
            'vibration_intensity': vibration,
            'soil_moisture_pct': moisture,
            'displacement_rate_mm_day': disp_rate,
            'rock_movement_mm': rock_mov,
            'geological_condition': geo_cond
        }
    }


def predict_batch(df):
    """
    Performs inference on a pandas DataFrame containing sensor readings.
    Returns the DataFrame augmented with predicted_risk and confidence.
    """
    bundle = get_model_bundle()
    rf_model = bundle['rf_model']
    scaler = bundle['scaler']
    num_features = bundle['numerical_features']
    geo_map = bundle['geo_mapping']

    df_clean = df.copy()
    for col in num_features:
        if col not in df_clean.columns:
            df_clean[col] = 0.0

    if 'geological_condition' not in df_clean.columns:
        df_clean['geological_condition'] = 'Stable Bedrock'

    df_clean['geo_vulnerability'] = df_clean['geological_condition'].map(geo_map).fillna(3)

    num_vals = df_clean[num_features]
    num_scaled = scaler.transform(num_vals)
    feature_matrix = pd.DataFrame(
        np.hstack([num_scaled, df_clean[['geo_vulnerability']].values]),
        columns=bundle['all_features']
    )

    preds = rf_model.predict(feature_matrix)
    probs = rf_model.predict_proba(feature_matrix)
    confs = np.max(probs, axis=1)

    df_clean['predicted_risk'] = preds
    df_clean['confidence'] = np.round(confs, 4)
    df_clean['confidence_pct'] = np.round(confs * 100, 1)

    return df_clean
