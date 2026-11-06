import sqlite3
from config import DATABASE

def connect():
    con = sqlite3.connect(DATABASE)
    con.row_factory = sqlite3.Row
    return con

def initialize_database():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_code TEXT UNIQUE NOT NULL,
            zone_name TEXT NOT NULL,
            geology TEXT DEFAULT '',
            location_ref TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id INTEGER NOT NULL,
            rainfall_mm_hr REAL, slope_angle_deg REAL, vibration_rms REAL,
            soil_moisture_pct REAL, displacement_mm REAL, rock_movement_mm_hr REAL,
            predicted_class TEXT, confidence REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(zone_id) REFERENCES zones(id)
        );
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id INTEGER NOT NULL, sensor_key TEXT NOT NULL,
            sensor_value REAL NOT NULL, threshold_value REAL NOT NULL,
            explanation TEXT NOT NULL, severity TEXT NOT NULL,
            status TEXT DEFAULT 'OPEN',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(zone_id) REFERENCES zones(id)
        );
        CREATE TABLE IF NOT EXISTS protocols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id INTEGER, title TEXT NOT NULL, content TEXT NOT NULL,
            source_reference TEXT NOT NULL, verified INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(zone_id) REFERENCES zones(id)
        );
        CREATE TABLE IF NOT EXISTS threshold_config (
            sensor_key TEXT PRIMARY KEY, threshold_value REAL NOT NULL
        );
        """)
        if con.execute("SELECT COUNT(*) FROM zones").fetchone()[0] == 0:
            con.executemany(
                "INSERT INTO zones(zone_code,zone_name,geology,location_ref) VALUES(?,?,?,?)",
                [
                    ("ZN-001","North Ridge","Jointed weathered rock","Demo sector A"),
                    ("ZN-002","East Escarpment","Rock-soil interface","Demo sector B"),
                    ("ZN-003","Quarry Bench 04","Fractured basalt","Demo sector C")
                ]
            )
        if con.execute("SELECT COUNT(*) FROM threshold_config").fetchone()[0] == 0:
            from config import DEFAULT_THRESHOLDS
            con.executemany("INSERT INTO threshold_config VALUES(?,?)", list(DEFAULT_THRESHOLDS.items()))
