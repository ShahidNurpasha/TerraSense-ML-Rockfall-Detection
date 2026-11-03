"""
Rockfall Early Warning and Response Coordination System
Extreme Reading Detection (Independent Rule-Based Backstop)

This module operates independently from the Machine Learning model.
It evaluates sensor readings against deterministic geotechnical safety thresholds.
Even if the ML classifier predicts 'Low Risk', if any critical physical threshold is exceeded,
this rule-based backstop triggers an immediate emergency alert.
"""

from database import get_db_connection


DEFAULT_THRESHOLDS = {
    'rainfall_mm': {
        'label': 'Rainfall Intensity',
        'unit': 'mm/24h',
        'warning': 65.0,
        'critical': 120.0,
        'danger_reason': 'High cumulative rainfall elevates pore water pressure along rock discontinuities, diminishing shear resistance and inducing sudden wedge/planar detachment.',
        'recommended_action': 'Suspend ground operations, activate drainage diversion, and initiate continuous laser distance monitoring.'
    },
    'displacement_rate_mm_day': {
        'label': 'Slope Displacement Rate',
        'unit': 'mm/day',
        'warning': 8.0,
        'critical': 15.0,
        'danger_reason': 'Displacement rate acceleration indicates progressive tertiary creep failure of the slope mass. Catastrophic rockfall is physically imminent.',
        'recommended_action': 'Sound immediate audible evacuation sirens for all downhill sectors and clear personnel to designated assembly points.'
    },
    'vibration_intensity': {
        'label': 'Ground Vibration (PPV)',
        'unit': 'mm/s',
        'warning': 5.0,
        'critical': 9.0,
        'danger_reason': 'Peak particle velocity from blasting or seismic shock exceeds tensile strength of fractured rock joints, dislodging hanging blocks.',
        'recommended_action': 'Halt all heavy machinery and blasting within a 1.5 km radius. Dispatch geotechnical drone for crest crack survey.'
    },
    'rock_movement_mm': {
        'label': 'Cumulative Rock Movement',
        'unit': 'mm',
        'warning': 12.0,
        'critical': 25.0,
        'danger_reason': 'Cumulative joint aperture widening has exceeded elastic tolerance limits. The rock wedge has detached from supporting bedrock.',
        'recommended_action': 'Establish physical exclusion barricades around the toe of the slope and prepare mobile catch-nets.'
    },
    'soil_moisture_pct': {
        'label': 'Soil Moisture Content',
        'unit': '%',
        'warning': 60.0,
        'critical': 80.0,
        'danger_reason': 'Near-saturation moisture eliminates soil suction, liquefying overburden colluvium and initiating rapid debris/rock avalanches.',
        'recommended_action': 'Engage sump dewatering pumps and inspect surface catch-water ditches for blockages.'
    }
}


def get_all_thresholds():
    """
    Fetches threshold configurations from SQLite database.
    Falls back to default geotechnical thresholds if table is not yet populated.
    """
    thresholds = {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM threshold_configs')
        rows = cursor.fetchall()
        conn.close()

        if rows:
            for row in rows:
                thresholds[row['sensor_key']] = {
                    'label': row['sensor_label'],
                    'unit': row['unit'],
                    'warning': float(row['warning_threshold']),
                    'critical': float(row['critical_threshold']),
                    'danger_reason': row['danger_reason'],
                    'recommended_action': row['recommended_action']
                }
            return thresholds
    except Exception as e:
        print(f"[AlertSystem] Warning reading thresholds from DB: {e}")

    return DEFAULT_THRESHOLDS


def update_threshold_config(sensor_key, warning_val, critical_val, danger_reason=None, action=None):
    """Updates a configurable sensor threshold in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if danger_reason and action:
        cursor.execute('''
            UPDATE threshold_configs
            SET warning_threshold = ?, critical_threshold = ?, danger_reason = ?, recommended_action = ?
            WHERE sensor_key = ?
        ''', (warning_val, critical_val, danger_reason, action, sensor_key))
    else:
        cursor.execute('''
            UPDATE threshold_configs
            SET warning_threshold = ?, critical_threshold = ?
            WHERE sensor_key = ?
        ''', (warning_val, critical_val, sensor_key))
    conn.commit()
    conn.close()
    return True


def evaluate_sensor_readings(sensor_data):
    """
    Independent Rule-Based Detection Engine.
    Evaluates individual sensor values and compound conditions against thresholds.

    Returns:
    - has_alerts: bool
    - max_severity: 'Normal', 'Warning', or 'Critical'
    - alerts: list of triggered alert dictionaries
    - trigger_count: int
    """
    thresholds = get_all_thresholds()
    alerts = []
    max_severity = 'Normal'

    # 1. Parameter-by-parameter evaluation
    for key, config in thresholds.items():
        if key in sensor_data:
            try:
                val = float(sensor_data[key])
            except (ValueError, TypeError):
                continue

            # Critical Breach
            if val >= config['critical']:
                alerts.append({
                    'sensor_key': key,
                    'sensor_label': config['label'],
                    'unit': config['unit'],
                    'reading_value': val,
                    'threshold_value': config['critical'],
                    'threshold_type': 'Critical Threshold',
                    'severity': 'Critical',
                    'risk_level': 'High Risk',
                    'danger_reason': config['danger_reason'],
                    'recommended_action': config['recommended_action']
                })
                max_severity = 'Critical'
            # Warning Breach
            elif val >= config['warning']:
                alerts.append({
                    'sensor_key': key,
                    'sensor_label': config['label'],
                    'unit': config['unit'],
                    'reading_value': val,
                    'threshold_value': config['warning'],
                    'threshold_type': 'Warning Threshold',
                    'severity': 'Warning',
                    'risk_level': 'Medium Risk',
                    'danger_reason': f"Elevated reading ({val} {config['unit']}) approaches geotechnical safety margin. {config['danger_reason']}",
                    'recommended_action': config['recommended_action']
                })
                if max_severity != 'Critical':
                    max_severity = 'Warning'

    # 2. Compound Geotechnical Rule: Steep Slope + High Moisture Saturation
    slope = float(sensor_data.get('slope_angle_deg', 0.0))
    moisture = float(sensor_data.get('soil_moisture_pct', 0.0))

    if slope >= 68.0 and moisture >= 75.0:
        # Check if already caught
        already_flagged = any(a['sensor_key'] == 'slope_angle_deg' and a['severity'] == 'Critical' for a in alerts)
        if not already_flagged:
            alerts.append({
                'sensor_key': 'compound_slope_moisture',
                'sensor_label': 'Overburden Saturation on Steep Incline',
                'unit': 'Angle & %',
                'reading_value': f"{slope}° / {moisture}%",
                'threshold_value': '68° / 75%',
                'threshold_type': 'Compound Limit',
                'severity': 'Critical',
                'risk_level': 'High Risk',
                'danger_reason': f"Dangerous compound hazard: Extreme slope steepness ({slope}°) combined with heavy soil saturation ({moisture}%) exceeds the limit equilibrium safety factor (FS < 1.0).",
                'recommended_action': 'Declare immediate slope exclusion zone and deploy safety barriers.'
            })
            max_severity = 'Critical'

    return {
        'has_alerts': len(alerts) > 0,
        'max_severity': max_severity,
        'alerts': alerts,
        'trigger_count': len(alerts)
    }


def record_alert_in_db(zone_id, reading_id, alert_info):
    """Records an extreme alert into the SQLite database for administrative management."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO extreme_alerts (
            reading_id, zone_id, rule_name, sensor_name, reading_value,
            threshold_value, risk_level, danger_explanation, recommended_action, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active')
    ''', (
        reading_id,
        zone_id,
        f"{alert_info['sensor_label']} {alert_info['threshold_type']}",
        alert_info['sensor_label'],
        float(str(alert_info['reading_value']).split()[0]) if isinstance(alert_info['reading_value'], str) else alert_info['reading_value'],
        float(str(alert_info['threshold_value']).split()[0]) if isinstance(alert_info['threshold_value'], str) else alert_info['threshold_value'],
        alert_info['risk_level'],
        alert_info['danger_reason'],
        alert_info['recommended_action']
    ))
    alert_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return alert_id
