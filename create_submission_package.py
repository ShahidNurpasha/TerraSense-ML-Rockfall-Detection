"""
Script to create the exact UMS Submission ZIP matching the university template:
Folder Structure:
CSE276_P09_12513245_12501181_.zip/
├── AI CODE FULL FOLDER/
│   ├── app.py
│   ├── model.py
│   ├── prediction.py
│   ├── alert_system.py
│   ├── emergency_response.py
│   ├── database.py
│   ├── rockfall.db
│   ├── Procfile
│   ├── requirements.txt
│   ├── run_app.bat
│   ├── test_system.py
│   ├── README.md
│   ├── templates/
│   │   ├── chatbot.html
│   │   ├── dashboard.html
│   │   ├── prediction.html
│   │   ├── protocols.html
│   │   ├── monitoring.html
│   │   ├── sensor_data.html
│   │   ├── alerts.html
│   │   ├── admin.html
│   │   ├── about.html
│   │   ├── index.html
│   │   └── base.html
│   ├── static/
│   │   ├── css/style.css
│   │   ├── js/script.js
│   │   └── img/
│   ├── data/
│   │   └── sample_dataset.csv
│   ├── models/
│   │   ├── model_metrics.json
│   │   └── rockfall_model.pkl
│   └── uploads/
├── CODE BASE REQUERIMENTS/
│   ├── app.py
│   ├── Database Details & Verified Dataset.txt
│   ├── GITHUB REPO LINK AND LIVE DEPLOYMENT LINK.txt
│   ├── README.md
│   └── requirements.txt
├── TERRASENSE ML ROCKFALL EARLY WARNING.pptx
├── ROCKFALL_EARLY_WARNING_PRESENTATION.pptx
├── CSE 276 TERRASENSE ML REPORT.pdf
└── PROJECT_REPORT.docx
"""

import os
import shutil
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Prepare GITHUB REPO LINK AND LIVE DEPLOYMENT LINK.txt
links_content = """GITHUB REPO LINK:

https://github.com/ShahidNurpasha/TerraSense-ML-Rockfall-Detection.git



LIVE DEPLOYMENT LINK:

https://terra-sense-ml-rockfall-detection.vercel.app/



INTERACTIVE RAG AI ASSISTANT CHATBOT:

https://terra-sense-ml-rockfall-detection.vercel.app/chatbot



GROUNDED SAFETY PROTOCOLS & RESPONSE COPILOT:

https://terra-sense-ml-rockfall-detection.vercel.app/protocols



LOCAL APPLICATION SERVER (OFFLINE EXECUTION):

http://127.0.0.1:5000/
http://127.0.0.1:5000/protocols
http://127.0.0.1:5000/chatbot



STUDENT INVESTIGATORS:

1. Nurpasha Shahid (Registration No. 12513245, Roll No. 05, Section K3P25IL)
2. Banala Yaswanth (Registration No. 12501181, Roll No. 27, Section K3P25IL)

Course: CSE276 (Artificial Intelligence Foundations) / Course Record ID: SDE25071
Project Group: Group #9 (P09)
University: Lovely Professional University (LPU)
"""

req_dir = os.path.join(BASE_DIR, 'CODE_BASE_REQUIREMENTS_TMP')
os.makedirs(req_dir, exist_ok=True)

with open(os.path.join(req_dir, 'GITHUB REPO LINK AND LIVE DEPLOYMENT LINK.txt'), 'w', encoding='utf-8') as f:
    f.write(links_content)

# 2. Prepare Database Details & Verified Dataset.txt
db_details_content = """Database Details & Verified Geotechnical Dataset
Part 1: Relational SQLite Database Architecture (rockfall.db)

The application runs an embedded, zero-configuration relational SQLite 3 database (rockfall.db) with dictionary row access.

Core Database Tables:
------------------------------------------------------------------------------------------------------------------------
Table Name          Primary Key     Key Columns & Types                                 Description
------------------------------------------------------------------------------------------------------------------------
zones               id (INTEGER)    zone_code (TEXT), name (TEXT), location (TEXT),     Registry of monitored slope sectors,
                                    rock_type (TEXT), slope_angle_deg (REAL),           geological rock formations, and 
                                    current_risk (TEXT), last_updated (TIMESTAMP)       active safety status.

sensor_readings     id (INTEGER)    zone_id (INTEGER), rainfall_mm (REAL),              Continuous telemetry logs of 6 core
                                    slope_angle_deg (REAL), vibration_intensity (REAL), physical parameters + rock type, ML
                                    soil_moisture_pct (REAL), displacement_rate (REAL), predicted risk tier, and confidence.
                                    rock_movement_mm (REAL), predicted_risk (TEXT)

extreme_alerts      id (INTEGER)    reading_id (INTEGER), zone_id (INTEGER),            Independent rule-based backstop events
                                    rule_name (TEXT), sensor_name (TEXT),               triggering deterministic safety alerts
                                    reading_value (REAL), threshold_value (REAL),       when physical thresholds are breached.
                                    risk_level (TEXT), status (TEXT)

safety_protocols    id (INTEGER)    zone_id (INTEGER), protocol_code (TEXT),            Administrator-verified SOP documents
                                    title (TEXT), authority_source (TEXT),              providing legal grounding for RAG
                                    evacuation_route (TEXT), assembly_point (TEXT),     evacuation directives (DGMS / SDMA).
                                    emergency_commander (TEXT), contact_phone (TEXT),
                                    is_verified (INTEGER)

threshold_configs   id (INTEGER)    sensor_key (TEXT), sensor_label (TEXT),             Configurable physical limits for
                                    unit (TEXT), warning_threshold (REAL),              rainfall, vibration, pore moisture,
                                    critical_threshold (REAL), danger_reason (TEXT),    and displacement velocity.
                                    recommended_action (TEXT)

prediction_history  id (INTEGER)    input_source (TEXT), zone_name (TEXT),              Full audit log of manual inferences
                                    rainfall_mm, slope_angle_deg, vibration, moisture,  and dual-engine evaluations.
                                    predicted_risk, confidence_score, rule_triggered


Part 2: Verified Synthetic Geotechnical Demonstration Dataset (data/sample_dataset.csv)
- Total Samples: 1,200 calibrated multivariate records
- Physical Features:
  1. Rainfall Intensity (mm/hr)
  2. Slope Incline Angle (degrees)
  3. Ground Vibration PPV (mm/s RMS)
  4. Soil / Joint Moisture Saturation (%)
  5. Slope Displacement Rate (mm/day)
  6. Rock Movement Aperture (mm)
  7. Geological Strata: Fractured Limestone, Weathered Sandstone, Jointed Basalt, Metamorphic Schist, Loose Shale
- Target Classes: Balanced 3-class target (Low Risk: 35%, Medium Risk: 35%, High Risk: 30%)
- Preprocessing: StandardScaler fitted strictly on 80% training split with 0% data leakage into the 20% holdout test partition.


Part 3: Retrieval-Augmented Generation (RAG) Knowledge Base
- 8 indexed geotechnical and procedural knowledge chunks
- Verified SOP clauses from Directorate General of Mine Safety (DGMS) and State Disaster Management Authority (SDMA)
- Zero Hallucination Guardrail: Unverified sectors (Zone E) trigger explicit emergency contingency fallbacks.
"""

with open(os.path.join(req_dir, 'Database Details & Verified Dataset.txt'), 'w', encoding='utf-8') as f:
    f.write(db_details_content)


def build_final_zip(zip_filename, inner_folder_name="CSE276_P09_12513245_12501181_.zip"):
    zip_path = os.path.join(BASE_DIR, zip_filename)
    print(f"Creating {zip_filename}...")

    # Files to include in AI CODE FULL FOLDER
    code_files = [
        "app.py",
        "model.py",
        "prediction.py",
        "alert_system.py",
        "emergency_response.py",
        "ai_chatbot_engine.py",
        "database.py",
        "rockfall.db",
        "Procfile",
        "vercel.json",
        "requirements.txt",
        "run_app.bat",
        "test_system.py",
        "README.md"
    ]

    code_dirs = [
        "api",
        "templates",
        "static",
        "data",
        "models",
        "uploads"
    ]

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        # 1. Root Presentations & Reports
        # Presentation 1 (16-Slide High Contrast)
        if os.path.exists(os.path.join(BASE_DIR, "ROCKFALL_EARLY_WARNING_PRESENTATION.pptx")):
            z.write(
                os.path.join(BASE_DIR, "ROCKFALL_EARLY_WARNING_PRESENTATION.pptx"),
                f"{inner_folder_name}/TERRASENSE ML ROCKFALL EARLY WARNING.pptx"
            )
            z.write(
                os.path.join(BASE_DIR, "ROCKFALL_EARLY_WARNING_PRESENTATION.pptx"),
                f"{inner_folder_name}/ROCKFALL_EARLY_WARNING_PRESENTATION.pptx"
            )

        # Presentation 2 (Mobile Friendly 8-Slide)
        if os.path.exists(os.path.join(BASE_DIR, "TerraSense_ML_Mobile_Friendly.pptx")):
            z.write(
                os.path.join(BASE_DIR, "TerraSense_ML_Mobile_Friendly.pptx"),
                f"{inner_folder_name}/TerraSense_ML_Mobile_Friendly.pptx"
            )

        # Report 1 (15-Page LPU Official PDF)
        if os.path.exists(os.path.join(BASE_DIR, "TerraSense_ML_CSE276_Project_Report.pdf")):
            z.write(
                os.path.join(BASE_DIR, "TerraSense_ML_CSE276_Project_Report.pdf"),
                f"{inner_folder_name}/CSE 276 TERRASENSE ML REPORT.pdf"
            )

        # Report 2 (10-Chapter Formal Word Report DOCX)
        if os.path.exists(os.path.join(BASE_DIR, "PROJECT_REPORT.docx")):
            z.write(
                os.path.join(BASE_DIR, "PROJECT_REPORT.docx"),
                f"{inner_folder_name}/PROJECT_REPORT.docx"
            )

        # 2. CODE BASE REQUERIMENTS
        z.write(
            os.path.join(BASE_DIR, "app.py"),
            f"{inner_folder_name}/CODE BASE REQUERIMENTS/app.py"
        )
        z.write(
            os.path.join(req_dir, "GITHUB REPO LINK AND LIVE DEPLOYMENT LINK.txt"),
            f"{inner_folder_name}/CODE BASE REQUERIMENTS/GITHUB REPO LINK AND LIVE DEPLOYMENT LINK.txt"
        )
        z.write(
            os.path.join(req_dir, "Database Details & Verified Dataset.txt"),
            f"{inner_folder_name}/CODE BASE REQUERIMENTS/Database Details & Verified Dataset.txt"
        )
        z.write(
            os.path.join(BASE_DIR, "README.md"),
            f"{inner_folder_name}/CODE BASE REQUERIMENTS/README.md"
        )
        z.write(
            os.path.join(BASE_DIR, "requirements.txt"),
            f"{inner_folder_name}/CODE BASE REQUERIMENTS/requirements.txt"
        )

        # 3. AI CODE FULL FOLDER
        for f in code_files:
            fp = os.path.join(BASE_DIR, f)
            if os.path.exists(fp):
                z.write(fp, f"{inner_folder_name}/AI CODE FULL FOLDER/{f}")

        for d in code_dirs:
            dp = os.path.join(BASE_DIR, d)
            if os.path.exists(dp):
                for root, _, files in os.walk(dp):
                    for file in files:
                        if "__pycache__" in root or file.endswith(".pyc") or file.endswith(".tmp"):
                            continue
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, BASE_DIR)
                        z.write(full_path, f"{inner_folder_name}/AI CODE FULL FOLDER/{rel_path}")

    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"Successfully generated: {zip_filename} ({size_mb:.2f} MB)")


if __name__ == '__main__':
    # Generate main target zip with exact university naming convention
    build_final_zip("CSE276_P09_12513245_12501181_.zip", "CSE276_P09_12513245_12501181_.zip")
    # Also generate without trailing underscore
    build_final_zip("CSE276_P09_12513245_12501181.zip", "CSE276_P09_12513245_12501181")
    # Also generate clean name
    build_final_zip("CSE276 12513245.zip", "CSE276_12513245_12501181")
    # Cleanup temp directory
    shutil.rmtree(req_dir, ignore_errors=True)
    print("Done!")
