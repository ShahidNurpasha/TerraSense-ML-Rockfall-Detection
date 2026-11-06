# TerraSense ML — Rockfall Early Warning & Response Coordination

A redesigned, white-mode machine-learning decision-support web application built with Flask.

## Visual direction
This version uses a clean research-dashboard aesthetic: white surfaces, muted blue technical accents, data tables, inference pipeline, model diagnostics, feature importance and confusion matrix. It is intentionally more like a student ML engineering project than a basic CRUD website.

## Features
- Random Forest classification: LOW / MODERATE / HIGH.
- Six sensor/geological input features.
- Stratified train/test split and 5-fold cross-validation.
- Classification report, confusion matrix and permutation feature importance.
- Independent threshold-based sensor event detector.
- Zone registration and sensor observation history.
- Alert workflow: OPEN / INVESTIGATING / RESOLVED.
- Configurable threshold settings.
- Verified safety protocol repository and retrieval.
- SQLite persistence and Joblib model serialization.

## Windows setup
```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Data and safety limitations
The initial 1,200-row dataset is synthetic and generated to exercise the application pipeline. Model metrics are illustrative and are not evidence of real-world rockfall prediction accuracy. Thresholds are demonstration values, not engineering standards. Do not use this application for real evacuation or safety decisions.

The emergency response module never fabricates routes or assembly points. It displays only protocol records marked verified; without one it instructs users to follow official site/emergency guidance.

## Main modules
- `ml_pipeline.py`: dataset generation, preprocessing pipeline, model training, evaluation and prediction.
- `risk_engine.py`: independent deterministic threshold checks.
- `response_engine.py`: verified protocol retrieval.
- `database.py`: SQLite schema and initial demo zones.
- `app.py`: Flask routes and integration.
- `config.py`: feature schema and demo threshold defaults.

## Suggested viva explanation
The system has three connected but independent layers. The Random Forest estimates a risk class from a six-dimensional feature vector. The rule engine checks each raw sensor feature against its own configured threshold, so it can raise an event even when the ML model predicts LOW. The response engine checks the database for a verified site protocol and never invents an evacuation instruction.

## Testing checklist
1. Open Overview and inspect model metrics.
2. Run inference with default readings.
3. Run inference with rainfall >= configured threshold to trigger the independent rule engine.
4. Confirm a sensor event appears in Alert Center.
5. Update alert status.
6. Add a zone.
7. Add a protocol but leave it unverified; it should not be retrieved.
8. Add an approved protocol and mark verified; test the response lookup again.
9. Change a threshold in Threshold Settings and test again.
10. Inspect the model diagnostics page.

## Production gaps
This is a university prototype, not a production safety system. It needs authentication, authorization, audit logs, CSRF protection, secure deployment, calibrated sensors, site-specific data validation, geotechnical expert review and emergency authority approval before operational use.
