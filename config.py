from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "instance" / "rockfall_studio.db"
DATASET = BASE_DIR / "data" / "rockfall_training_data.csv"
MODEL_FILE = BASE_DIR / "models" / "rockfall_pipeline.joblib"

FEATURES = [
    "rainfall_mm_hr", "slope_angle_deg", "vibration_rms",
    "soil_moisture_pct", "displacement_mm", "rock_movement_mm_hr"
]
TARGET = "risk_class"

# Demo thresholds only. Replace with site-calibrated, engineer-approved limits.
DEFAULT_THRESHOLDS = {
    "rainfall_mm_hr": 55.0,
    "slope_angle_deg": 58.0,
    "vibration_rms": 0.85,
    "soil_moisture_pct": 88.0,
    "displacement_mm": 22.0,
    "rock_movement_mm_hr": 17.0
}
