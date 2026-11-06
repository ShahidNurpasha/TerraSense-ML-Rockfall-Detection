from config import DEFAULT_THRESHOLDS

EXPLANATIONS = {
    "rainfall_mm_hr": "Rainfall intensity is above the configured trigger; infiltration can increase pore-water pressure.",
    "slope_angle_deg": "Slope angle is above the configured screening limit; inspect the site's geotechnical assessment.",
    "vibration_rms": "Ground vibration exceeds the configured monitoring threshold.",
    "soil_moisture_pct": "Soil moisture is above the configured trigger and may indicate elevated saturation.",
    "displacement_mm": "Measured displacement exceeds the configured movement threshold.",
    "rock_movement_mm_hr": "Rock movement rate exceeds the configured movement threshold."
}

def evaluate_thresholds(readings, thresholds):
    """Independent detector: does not consume or depend on the ML class."""
    events = []
    for key, limit in thresholds.items():
        value = float(readings[key])
        if value >= float(limit):
            events.append({
                "sensor": key, "value": value, "threshold": float(limit),
                "explanation": EXPLANATIONS[key], "severity": "CRITICAL" if value >= 1.25*float(limit) else "WARNING"
            })
    return events
