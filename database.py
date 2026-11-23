"""
Rockfall Early Warning and Response Coordination System
Database Management Module (SQLite)

This module manages all database operations for:
- Monitored zones
- Historical sensor readings
- Supervised machine learning predictions
- Independent rule-based extreme alerts
- Administrator-verified safety protocols
- Configurable sensor thresholds
"""

import sqlite3
import os
import shutil
from datetime import datetime, timedelta
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORIGINAL_DB_PATH = os.path.join(BASE_DIR, 'rockfall.db')

# On Vercel / serverless platforms, root directory is read-only.
# We use /tmp for SQLite to allow reading & writing without errors.
if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    DB_PATH = '/tmp/rockfall.db'
else:
    DB_PATH = ORIGINAL_DB_PATH


def get_db_connection():
    """Returns a SQLite connection with row factory enabled for dictionary-like access."""
    if (os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME')) and not os.path.exists(DB_PATH):
        try:
            if os.path.exists(ORIGINAL_DB_PATH):
                shutil.copy2(ORIGINAL_DB_PATH, DB_PATH)
            else:
                init_db()
        except Exception as e:
            print(f"[DB Warning] Error copying SQLite db to /tmp: {e}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes database tables and seeds baseline demonstration data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Monitored Zones table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            rock_type TEXT NOT NULL,
            slope_angle_deg REAL NOT NULL,
            current_risk TEXT DEFAULT 'Low Risk',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Sensor Readings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id INTEGER NOT NULL,
            rainfall_mm REAL NOT NULL,
            slope_angle_deg REAL NOT NULL,
            vibration_intensity REAL NOT NULL,
            soil_moisture_pct REAL NOT NULL,
            displacement_rate_mm_day REAL NOT NULL,
            rock_movement_mm REAL NOT NULL,
            geological_condition TEXT NOT NULL,
            predicted_risk TEXT,
            confidence_score REAL,
            is_extreme_alert INTEGER DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE
        )
    ''')

    # 3. Extreme Alerts table (Rule-Based Backstop)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extreme_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reading_id INTEGER,
            zone_id INTEGER NOT NULL,
            rule_name TEXT NOT NULL,
            sensor_name TEXT NOT NULL,
            reading_value REAL NOT NULL,
            threshold_value REAL NOT NULL,
            risk_level TEXT NOT NULL,
            danger_explanation TEXT NOT NULL,
            recommended_action TEXT NOT NULL,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE
        )
    ''')

    # 4. Verified Safety Protocols table (Ground Truth Emergency Responses)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS safety_protocols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id INTEGER UNIQUE NOT NULL,
            protocol_code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            authority_source TEXT NOT NULL,
            evacuation_route TEXT NOT NULL,
            safe_assembly_point TEXT NOT NULL,
            emergency_commander TEXT NOT NULL,
            contact_phone TEXT NOT NULL,
            is_verified INTEGER DEFAULT 1,
            verified_date TEXT,
            document_filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE
        )
    ''')

    # 5. Configurable Sensor Thresholds table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS threshold_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_key TEXT UNIQUE NOT NULL,
            sensor_label TEXT NOT NULL,
            unit TEXT NOT NULL,
            warning_threshold REAL NOT NULL,
            critical_threshold REAL NOT NULL,
            danger_reason TEXT NOT NULL,
            recommended_action TEXT NOT NULL
        )
    ''')

    # 6. Prediction History table (Manual Inputs & Batch Predictions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_source TEXT DEFAULT 'Manual Input',
            zone_name TEXT,
            rainfall_mm REAL NOT NULL,
            slope_angle_deg REAL NOT NULL,
            vibration_intensity REAL NOT NULL,
            soil_moisture_pct REAL NOT NULL,
            displacement_rate_mm_day REAL NOT NULL,
            rock_movement_mm REAL NOT NULL,
            geological_condition TEXT NOT NULL,
            predicted_risk TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            rule_alert_triggered INTEGER DEFAULT 0,
            rule_alert_details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()

    # Seed baseline data if zones table is empty
    cursor.execute('SELECT COUNT(*) as count FROM zones')
    if cursor.fetchone()['count'] == 0:
        seed_baseline_data(conn)

    conn.close()


def seed_baseline_data(conn):
    """Populates baseline demonstration data for zones, protocols, thresholds, and readings."""
    cursor = conn.cursor()

    # 1. Seed Threshold Configurations
    default_thresholds = [
        (
            'rainfall_mm',
            'Rainfall Intensity',
            'mm/24h',
            65.0,
            120.0,
            'Sustained high rainfall saturates shear planes, increasing pore water pressure and reducing friction between rock strata.',
            'Suspend operations in downhill sectors and initiate continuous pore pressure telemetry monitoring.'
        ),
        (
            'displacement_rate_mm_day',
            'Slope Displacement Rate',
            'mm/day',
            8.0,
            15.0,
            'Accelerating slope creep indicates continuous plastic deformation and imminent shear failure along the slip surface.',
            'Sound evacuation siren for the active slope sector and clear all machinery and personnel within 300 meters.'
        ),
        (
            'vibration_intensity',
            'Ground Vibration (PPV)',
            'mm/s',
            5.0,
            9.0,
            'Strong blasting or seismic shockwaves can trigger brittle failure and dislodge hanging boulders from steep faces.',
            'Halt blasting/excavation activities immediately and verify crest crack status before permitting inspection.'
        ),
        (
            'rock_movement_mm',
            'Cumulative Rock Movement',
            'mm',
            12.0,
            25.0,
            'Cumulative joint aperture opening has surpassed critical geotechnical safety limits.',
            'Establish an exclusion zone around the toe and engage drone photogrammetry to detect toe heaving.'
        ),
        (
            'soil_moisture_pct',
            'Soil Moisture Content',
            '%',
            60.0,
            80.0,
            'Soil saturation drastically reduces effective shear strength of weathered overburden layers.',
            'Activate drainage sump pumps and reinforce containment berms along the transport ramp.'
        )
    ]

    cursor.executemany('''
        INSERT INTO threshold_configs 
        (sensor_key, sensor_label, unit, warning_threshold, critical_threshold, danger_reason, recommended_action)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', default_thresholds)

    # 2. Seed Monitored Zones
    zones = [
        ('ZONE-A', 'North Ridge Pass', 'Sector 1 - Ridge Crest', 'Fractured Limestone', 58.5, 'Low Risk'),
        ('ZONE-B', 'East Quarry Highwall', 'Sector 2 - Bench 4', 'Weathered Sandstone', 67.0, 'Medium Risk'),
        ('ZONE-C', 'Highway 108 Rock Cutting', 'Sector 3 - KM 42+300', 'Loose Shale & Siltstone', 72.0, 'High Risk'),
        ('ZONE-D', 'Valley Settlement Slope', 'Sector 4 - South Escarpment', 'Jointed Basalt', 48.0, 'Low Risk'),
        ('ZONE-E', 'Railway Tunnel Portal North', 'Sector 5 - Portal Incline', 'Metamorphic Schist', 63.5, 'Medium Risk')
    ]

    cursor.executemany('''
        INSERT INTO zones (zone_code, name, location, rock_type, slope_angle_deg, current_risk)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', zones)

    # 3. Seed Verified Safety Protocols (Zones A, B, C, D verified; Zone E unverified to test fallback)
    protocols = [
        (
            1,
            'SOP-NR-2024-01',
            'North Ridge Pass Rockfall Emergency Protocol',
            'State Disaster Management Authority & Mines Safety Directorate (Doc ID: SDMA-MSD-102)',
            'Evacuate eastward via Service Access Track 1 towards Checkpost Alpha.',
            'Assembly Point Alpha (Open Heli-pad ground, Sector 1 Coordinates 32.148N, 76.512E)',
            'Dr. Arvind Kumar (Chief Safety Officer)',
            '+91-98765-43210',
            1,
            '2024-03-15',
            'sop_north_ridge.pdf'
        ),
        (
            2,
            'SOP-EQ-2024-02',
            'East Quarry Highwall Evacuation & Berm Clearance SOP',
            'Directorate General of Mines Safety (DGMS Circular No. 04/2023)',
            'Exit bench 4 via West Haulage Ramp to Upper Terrace Parking.',
            'Quarry Administration Field Office Ground (Clear distance 450m from face)',
            'Er. Rajesh Varma (Mines Manager)',
            '+91-98765-43211',
            1,
            '2024-05-10',
            'sop_east_quarry.pdf'
        ),
        (
            3,
            'SOP-HW108-2024-03',
            'Highway 108 Slope Failure Contingency & Traffic Diversion',
            'National Highways Authority of India (NHAI Incident Response Framework v2.1)',
            'Immediately deploy automated boom barriers at KM 41 and KM 44; redirect traffic via Bypass Link B.',
            'Highway Toll Plaza Emergency Staging Area (KM 39.5)',
            'Inspector S. Patil (Highway Traffic & Disaster Incharge)',
            '+91-98765-43212',
            1,
            '2024-01-20',
            'sop_highway_108.pdf'
        ),
        (
            4,
            'SOP-VS-2024-04',
            'Valley Settlement Civil Protection & Relocation Directive',
            'District Disaster Management Authority (DDMA Order Ref #88/DIS-MAG)',
            'Move downhill away from the toe along marked pedestrian emergency corridor Blue towards Valley School.',
            'Valley Community High School Sports Complex & Emergency Relief Camp',
            'Ms. Neha Sharma (District Relief Commissioner)',
            '+91-98765-43213',
            1,
            '2024-06-01',
            'sop_valley_settlement.pdf'
        )
        # Note: Zone E deliberately left without verified protocol to test system's safety honesty constraint
    ]

    cursor.executemany('''
        INSERT INTO safety_protocols 
        (zone_id, protocol_code, title, authority_source, evacuation_route, safe_assembly_point, emergency_commander, contact_phone, is_verified, verified_date, document_filename)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', protocols)

    # 4. Seed Historical Readings for Demonstration
    sample_readings = [
        # Zone A: Normal stable reading
        (1, 15.2, 58.5, 0.8, 25.4, 0.4, 1.2, 'Fractured Limestone', 'Low Risk', 0.94, 0),
        # Zone B: Moderate displacement & rainfall
        (2, 68.4, 67.0, 3.2, 58.2, 7.5, 9.8, 'Weathered Sandstone', 'Medium Risk', 0.86, 0),
        # Zone C: Extreme rainfall and displacement breach
        (3, 142.5, 72.0, 7.8, 84.6, 21.4, 32.1, 'Loose Shale & Siltstone', 'High Risk', 0.98, 1),
        # Zone D: Low risk baseline
        (4, 8.0, 48.0, 0.5, 22.0, 0.2, 0.8, 'Jointed Basalt', 'Low Risk', 0.97, 0),
        # Zone E: Medium risk vibration reading
        (5, 42.0, 63.5, 5.8, 48.0, 4.2, 6.5, 'Metamorphic Schist', 'Medium Risk', 0.82, 0)
    ]

    for r in sample_readings:
        cursor.execute('''
            INSERT INTO sensor_readings 
            (zone_id, rainfall_mm, slope_angle_deg, vibration_intensity, soil_moisture_pct, displacement_rate_mm_day, rock_movement_mm, geological_condition, predicted_risk, confidence_score, is_extreme_alert)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', r)
        reading_id = cursor.lastrowid

        # Insert prediction history
        zone_names = {1: 'North Ridge Pass', 2: 'East Quarry Highwall', 3: 'Highway 108 Rock Cutting', 4: 'Valley Settlement Slope', 5: 'Railway Tunnel Portal North'}
        cursor.execute('''
            INSERT INTO prediction_history
            (input_source, zone_name, rainfall_mm, slope_angle_deg, vibration_intensity, soil_moisture_pct, displacement_rate_mm_day, rock_movement_mm, geological_condition, predicted_risk, confidence_score, rule_alert_triggered, rule_alert_details)
            VALUES ('Zone Sensor', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (zone_names[r[0]], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], 'Critical threshold exceeded on rainfall & displacement' if r[10] else 'Normal parameters'))

    # 5. Seed Demonstration Extreme Alert for Zone C
    cursor.execute('''
        INSERT INTO extreme_alerts 
        (reading_id, zone_id, rule_name, sensor_name, reading_value, threshold_value, risk_level, danger_explanation, recommended_action, status)
        VALUES 
        (3, 3, 'Extreme Displacement Acceleration', 'Displacement Rate', 21.4, 15.0, 'High Risk',
         'Displacement rate of 21.4 mm/day exceeded critical threshold of 15.0 mm/day. Rapid progressive shear plane movement indicates catastrophic rockfall danger.',
         'Execute Highway 108 Emergency Protocol (SOP-HW108-2024-03). Close road section and deploy barrier crews.', 'Active'),
        (3, 3, 'Extreme Rainfall Inundation', 'Rainfall Intensity', 142.5, 120.0, 'High Risk',
         'Continuous 24-hour rainfall of 142.5 mm exceeded critical saturation barrier of 120.0 mm. High pore water pressure will induce structural rock detachment.',
         'Sound warning sirens and evacuate lower crest workers.', 'Active')
    ''')

    conn.commit()


if __name__ == '__main__':
    print("Initializing Rockfall Early Warning System Database...")
    init_db()
    print(f"Database successfully created at: {DB_PATH}")
