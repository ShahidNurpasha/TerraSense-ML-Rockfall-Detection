"""
Rockfall Early Warning and Response Coordination System
Flask Web Application Server

This application integrates:
1. Supervised Machine Learning Risk Classification (Random Forest / Decision Tree)
2. Independent Rule-Based Extreme Reading Detection System
3. Verified Documented Emergency Response Coordination System
4. Zone Monitoring & Alert Management Dashboard
"""

import os
import io
import json
import sqlite3
import pandas as pd
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    send_file,
    send_from_directory
)
from werkzeug.utils import secure_filename

from database import init_db, get_db_connection
from prediction import predict_risk, predict_batch, get_model_bundle, reload_model_bundle
from alert_system import evaluate_sensor_readings, record_alert_in_db, get_all_thresholds, update_threshold_config
from emergency_response import (
    get_zone_protocol,
    get_all_protocols_with_zones,
    generate_grounded_evacuation_notice,
    generate_rag_response,
    save_or_update_protocol
)
from model import train_and_evaluate_models
from ai_chatbot_engine import process_chat_query, get_all_indexed_topics

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    UPLOAD_PROTOCOLS_DIR = os.path.join('/tmp', 'uploads', 'protocols')
    DATA_DIR = os.path.join('/tmp', 'data')
    MODELS_DIR = os.path.join(BASE_DIR, 'models')
else:
    UPLOAD_PROTOCOLS_DIR = os.path.join(BASE_DIR, 'uploads', 'protocols')
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    MODELS_DIR = os.path.join(BASE_DIR, 'models')

try:
    os.makedirs(UPLOAD_PROTOCOLS_DIR, exist_ok=True)
except OSError:
    pass
try:
    os.makedirs(DATA_DIR, exist_ok=True)
except OSError:
    pass
try:
    os.makedirs(MODELS_DIR, exist_ok=True)
except OSError:
    pass

app = Flask(__name__)
app.secret_key = 'rockfall-decision-support-secret-key-2025'
app.config['UPLOAD_FOLDER'] = UPLOAD_PROTOCOLS_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

# Initialize Database on application startup
init_db()


# -------------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------------
def get_dashboard_summary():
    """Calculates summary statistics across zones, readings, and alerts."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Zone counts by risk
    cursor.execute('SELECT COUNT(*) as total FROM zones')
    total_zones = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as count FROM zones WHERE current_risk = 'Low Risk'")
    low_risk_zones = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM zones WHERE current_risk = 'Medium Risk'")
    med_risk_zones = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM zones WHERE current_risk = 'High Risk'")
    high_risk_zones = cursor.fetchone()['count']

    # Active and Critical alerts
    cursor.execute("SELECT COUNT(*) as count FROM extreme_alerts WHERE status = 'Active'")
    active_alerts = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM extreme_alerts WHERE status = 'Active' AND risk_level = 'High Risk'")
    critical_alerts = cursor.fetchone()['count']

    # Recent 5 readings
    cursor.execute('''
        SELECT r.*, z.name as zone_name, z.zone_code
        FROM sensor_readings r
        JOIN zones z ON r.zone_id = z.id
        ORDER BY r.timestamp DESC
        LIMIT 6
    ''')
    recent_readings = [dict(row) for row in cursor.fetchall()]

    # Recent 5 alerts
    cursor.execute('''
        SELECT a.*, z.name as zone_name, z.zone_code
        FROM extreme_alerts a
        JOIN zones z ON a.zone_id = z.id
        ORDER BY a.created_at DESC
        LIMIT 5
    ''')
    recent_alerts = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        'total_zones': total_zones,
        'low_risk_zones': low_risk_zones,
        'med_risk_zones': med_risk_zones,
        'high_risk_zones': high_risk_zones,
        'active_alerts': active_alerts,
        'critical_alerts': critical_alerts,
        'recent_readings': recent_readings,
        'recent_alerts': recent_alerts
    }


# -------------------------------------------------------------------------
# Web Routes
# -------------------------------------------------------------------------

@app.route('/')
@app.route('/dashboard')
def dashboard():
    """Module 1: Main System Dashboard."""
    summary = get_dashboard_summary()
    return render_template('dashboard.html', summary=summary)


@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    """
    Module 2 & 3: Supervised Machine Learning Risk Prediction
    and Independent Rule-Based Extreme Reading Detection.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, zone_code, name FROM zones ORDER BY id ASC')
    zones = [dict(row) for row in cursor.fetchall()]
    conn.close()

    prediction_result = None
    rule_result = None
    evacuation_notice = None

    if request.method == 'POST':
        try:
            zone_id = request.form.get('zone_id')
            rainfall_mm = float(request.form.get('rainfall_mm', 0.0))
            slope_angle_deg = float(request.form.get('slope_angle_deg', 45.0))
            vibration_intensity = float(request.form.get('vibration_intensity', 0.0))
            soil_moisture_pct = float(request.form.get('soil_moisture_pct', 20.0))
            displacement_rate_mm_day = float(request.form.get('displacement_rate_mm_day', 0.0))
            rock_movement_mm = float(request.form.get('rock_movement_mm', 0.0))
            geological_condition = request.form.get('geological_condition', 'Stable Bedrock')

            sensor_payload = {
                'rainfall_mm': rainfall_mm,
                'slope_angle_deg': slope_angle_deg,
                'vibration_intensity': vibration_intensity,
                'soil_moisture_pct': soil_moisture_pct,
                'displacement_rate_mm_day': displacement_rate_mm_day,
                'rock_movement_mm': rock_movement_mm,
                'geological_condition': geological_condition
            }

            # 1. Supervised Machine Learning Risk Classification
            prediction_result = predict_risk(sensor_payload)

            # 2. Independent Rule-Based Extreme Reading Detection
            rule_result = evaluate_sensor_readings(sensor_payload)

            # Determine selected zone info
            selected_zone = None
            if zone_id and zone_id != '':
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM zones WHERE id = ?', (zone_id,))
                row = cursor.fetchone()
                if row:
                    selected_zone = dict(row)
                conn.close()

            # 3. Emergency Protocol Retrieval if High Risk or Critical Alert triggered
            is_high_risk = (prediction_result['predicted_risk'] == 'High Risk') or (rule_result['max_severity'] == 'Critical')
            if is_high_risk and selected_zone:
                trigger_reason = f"Elevated Hazard Detected: ML Prediction ({prediction_result['predicted_risk']}) "
                if rule_result['has_alerts']:
                    trigger_reason += f"with {len(rule_result['alerts'])} extreme sensor threshold breaches"
                evacuation_notice = generate_grounded_evacuation_notice(
                    selected_zone, trigger_reason, alert_severity='High Risk', sensor_telemetry=sensor_payload
                )

            # 4. Save to prediction history in database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO prediction_history (
                    input_source, zone_name, rainfall_mm, slope_angle_deg,
                    vibration_intensity, soil_moisture_pct, displacement_rate_mm_day,
                    rock_movement_mm, geological_condition, predicted_risk,
                    confidence_score, rule_alert_triggered, rule_alert_details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'Manual Input Form',
                selected_zone['name'] if selected_zone else 'Ad-hoc Assessment',
                rainfall_mm,
                slope_angle_deg,
                vibration_intensity,
                soil_moisture_pct,
                displacement_rate_mm_day,
                rock_movement_mm,
                geological_condition,
                prediction_result['predicted_risk'],
                prediction_result['confidence'],
                1 if rule_result['has_alerts'] else 0,
                ', '.join([a['sensor_label'] for a in rule_result['alerts']]) if rule_result['has_alerts'] else 'None'
            ))
            conn.commit()
            conn.close()

        except Exception as e:
            flash(f"Error processing sensor inputs: {str(e)}", 'danger')

    return render_template(
        'prediction.html',
        zones=zones,
        prediction_result=prediction_result,
        rule_result=rule_result,
        evacuation_notice=evacuation_notice
    )


@app.route('/monitoring', methods=['GET', 'POST'])
def monitoring():
    """Module 5: Zone Monitoring and Telemetry Input."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Handle adding a new zone
    if request.method == 'POST' and request.form.get('action') == 'add_zone':
        zone_code = request.form.get('zone_code', '').strip().upper()
        name = request.form.get('name', '').strip()
        location = request.form.get('location', '').strip()
        rock_type = request.form.get('rock_type', 'Fractured Limestone')
        slope_angle_deg = float(request.form.get('slope_angle_deg', 50.0))

        if zone_code and name:
            try:
                cursor.execute('''
                    INSERT INTO zones (zone_code, name, location, rock_type, slope_angle_deg, current_risk)
                    VALUES (?, ?, ?, ?, ?, 'Low Risk')
                ''', (zone_code, name, location, rock_type, slope_angle_deg))
                conn.commit()
                flash(f"Zone '{name}' ({zone_code}) added successfully.", 'success')
            except sqlite3.IntegrityError:
                flash(f"Zone code '{zone_code}' already exists.", 'danger')
        return redirect(url_for('monitoring'))

    # Handle submitting new sensor readings for a zone
    if request.method == 'POST' and request.form.get('action') == 'submit_reading':
        try:
            zone_id = int(request.form.get('zone_id'))
            rainfall_mm = float(request.form.get('rainfall_mm', 0.0))
            slope_angle_deg = float(request.form.get('slope_angle_deg', 50.0))
            vibration_intensity = float(request.form.get('vibration_intensity', 0.0))
            soil_moisture_pct = float(request.form.get('soil_moisture_pct', 20.0))
            displacement_rate_mm_day = float(request.form.get('displacement_rate_mm_day', 0.0))
            rock_movement_mm = float(request.form.get('rock_movement_mm', 0.0))
            geological_condition = request.form.get('geological_condition', 'Stable Bedrock')

            sensor_payload = {
                'rainfall_mm': rainfall_mm,
                'slope_angle_deg': slope_angle_deg,
                'vibration_intensity': vibration_intensity,
                'soil_moisture_pct': soil_moisture_pct,
                'displacement_rate_mm_day': displacement_rate_mm_day,
                'rock_movement_mm': rock_movement_mm,
                'geological_condition': geological_condition
            }

            # Predict risk
            pred = predict_risk(sensor_payload)
            predicted_risk = pred['predicted_risk']
            confidence = pred['confidence']

            # Evaluate extreme rules
            rule_eval = evaluate_sensor_readings(sensor_payload)
            is_extreme = 1 if rule_eval['has_alerts'] else 0

            # Update zone risk level (if rule triggered critical, force zone to High Risk)
            final_zone_risk = 'High Risk' if rule_eval['max_severity'] == 'Critical' else predicted_risk
            cursor.execute('''
                UPDATE zones 
                SET current_risk = ?, last_updated = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (final_zone_risk, zone_id))

            # Record reading
            cursor.execute('''
                INSERT INTO sensor_readings (
                    zone_id, rainfall_mm, slope_angle_deg, vibration_intensity,
                    soil_moisture_pct, displacement_rate_mm_day, rock_movement_mm,
                    geological_condition, predicted_risk, confidence_score, is_extreme_alert
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                zone_id, rainfall_mm, slope_angle_deg, vibration_intensity,
                soil_moisture_pct, displacement_rate_mm_day, rock_movement_mm,
                geological_condition, predicted_risk, confidence, is_extreme
            ))
            reading_id = cursor.lastrowid

            # If extreme rules triggered, generate alerts in DB
            for alert in rule_eval['alerts']:
                record_alert_in_db(zone_id, reading_id, alert)

            conn.commit()
            flash(f"Sensor telemetry recorded for Zone ID {zone_id}. Risk Evaluated: {final_zone_risk}", 'success')
            return redirect(url_for('monitoring'))

        except Exception as e:
            flash(f"Error recording sensor reading: {str(e)}", 'danger')

    # Fetch all zones with reading count and latest timestamp
    cursor.execute('''
        SELECT z.*, 
               COUNT(r.id) as reading_count,
               MAX(r.timestamp) as latest_reading_time
        FROM zones z
        LEFT JOIN sensor_readings r ON z.id = r.zone_id
        GROUP BY z.id
        ORDER BY z.id ASC
    ''')
    zones_list = [dict(row) for row in cursor.fetchall()]

    # Fetch recent readings
    cursor.execute('''
        SELECT r.*, z.name as zone_name, z.zone_code
        FROM sensor_readings r
        JOIN zones z ON r.zone_id = z.id
        ORDER BY r.timestamp DESC
        LIMIT 15
    ''')
    readings = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return render_template('monitoring.html', zones=zones_list, readings=readings)


@app.route('/sensor-data')
def sensor_data():
    """Module 5/Data: Full Sensor Data explorer and dataset management."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT r.*, z.name as zone_name, z.zone_code
        FROM sensor_readings r
        JOIN zones z ON r.zone_id = z.id
        ORDER BY r.timestamp DESC
    ''')
    readings = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return render_template('sensor_data.html', readings=readings)


@app.route('/sensor-data/download-csv')
def download_sensor_csv():
    """Exports all recorded sensor readings to CSV."""
    conn = get_db_connection()
    df = pd.read_sql_query('''
        SELECT r.id, z.zone_code, z.name as zone_name, r.rainfall_mm, r.slope_angle_deg,
               r.vibration_intensity, r.soil_moisture_pct, r.displacement_rate_mm_day,
               r.rock_movement_mm, r.geological_condition, r.predicted_risk,
               r.confidence_score, r.is_extreme_alert, r.timestamp
        FROM sensor_readings r
        JOIN zones z ON r.zone_id = z.id
        ORDER BY r.timestamp DESC
    ''', conn)
    conn.close()

    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'rockfall_sensor_telemetry_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
    )


@app.route('/sensor-data/upload-csv', methods=['POST'])
def upload_sensor_csv():
    """Uploads a CSV of sensor data, runs batch prediction, and optionally adds to DB."""
    file = request.files.get('dataset_file')
    if not file or file.filename == '':
        flash('No CSV file selected.', 'warning')
        return redirect(url_for('sensor_data'))

    try:
        df = pd.read_csv(file)
        results_df = predict_batch(df)

        # Count predicted risks
        risk_counts = results_df['predicted_risk'].value_counts().to_dict()
        flash(f"Successfully processed CSV ({len(results_df)} records). "
              f"Predictions: High: {risk_counts.get('High Risk', 0)}, "
              f"Medium: {risk_counts.get('Medium Risk', 0)}, "
              f"Low: {risk_counts.get('Low Risk', 0)}", 'success')

    except Exception as e:
        flash(f"Error parsing uploaded CSV: {str(e)}", 'danger')

    return redirect(url_for('sensor_data'))


@app.route('/alerts')
def alerts():
    """Module 6: Alert Management Center."""
    status_filter = request.args.get('status', 'All')

    conn = get_db_connection()
    cursor = conn.cursor()

    if status_filter != 'All':
        cursor.execute('''
            SELECT a.*, z.name as zone_name, z.zone_code, z.location
            FROM extreme_alerts a
            JOIN zones z ON a.zone_id = z.id
            WHERE a.status = ?
            ORDER BY a.created_at DESC
        ''', (status_filter,))
    else:
        cursor.execute('''
            SELECT a.*, z.name as zone_name, z.zone_code, z.location
            FROM extreme_alerts a
            JOIN zones z ON a.zone_id = z.id
            ORDER BY a.created_at DESC
        ''')

    alert_rows = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return render_template('alerts.html', alerts=alert_rows, active_filter=status_filter)


@app.route('/alerts/update-status', methods=['POST'])
def update_alert_status():
    """Updates an alert status (Active, Acknowledged, Evacuating, Resolved)."""
    alert_id = request.form.get('alert_id')
    new_status = request.form.get('status')

    if alert_id and new_status:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE extreme_alerts
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_status, alert_id))
        conn.commit()
        conn.close()
        flash(f"Alert #{alert_id} status updated to '{new_status}'.", 'success')

    return redirect(url_for('alerts'))


@app.route('/protocols', methods=['GET', 'POST'])
def protocols():
    """Module 4: Verified Safety Protocols & RAG AI Response Coordination."""
    all_protocols = get_all_protocols_with_zones()
    rag_result = None
    query_text = ""
    selected_zone_id = None

    if request.method == 'POST':
        query_text = request.form.get('rag_query', '').strip()
        zone_id_raw = request.form.get('zone_id', '').strip()
        selected_zone_id = int(zone_id_raw) if zone_id_raw.isdigit() else None
        if query_text:
            rag_result = generate_rag_response(query_text, zone_id=selected_zone_id)
    elif request.args.get('q'):
        query_text = request.args.get('q', '').strip()
        zone_id_raw = request.args.get('zone_id', '').strip()
        selected_zone_id = int(zone_id_raw) if zone_id_raw.isdigit() else None
        if query_text:
            rag_result = generate_rag_response(query_text, zone_id=selected_zone_id)

    return render_template(
        'protocols.html',
        protocols=all_protocols,
        rag_result=rag_result,
        query_text=query_text,
        selected_zone_id=selected_zone_id
    )


@app.route('/protocols/generate-notice/<int:zone_id>')
def generate_notice(zone_id):
    """Generates and displays the grounded evacuation message for a designated zone."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM zones WHERE id = ?', (zone_id,))
    zone_row = cursor.fetchone()
    conn.close()

    if not zone_row:
        flash('Zone not found.', 'danger')
        return redirect(url_for('protocols'))

    zone = dict(zone_row)
    notice = generate_grounded_evacuation_notice(
        zone=zone,
        trigger_reason=f"Emergency Drill / Geotechnical Alert Verification for {zone['name']}",
        alert_severity=zone['current_risk']
    )

    return render_template('protocols.html', protocols=get_all_protocols_with_zones(), selected_notice=notice)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Module 7: Administrator Panel."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Threshold update handling
    if request.method == 'POST' and request.form.get('action') == 'update_threshold':
        sensor_key = request.form.get('sensor_key')
        warning_thresh = float(request.form.get('warning_threshold'))
        critical_thresh = float(request.form.get('critical_threshold'))
        update_threshold_config(sensor_key, warning_thresh, critical_thresh)
        flash(f"Thresholds for {sensor_key} updated.", 'success')
        return redirect(url_for('admin'))

    # Protocol upload/save handling
    if request.method == 'POST' and request.form.get('action') == 'save_protocol':
        zone_id = int(request.form.get('zone_id'))
        protocol_code = request.form.get('protocol_code').strip()
        title = request.form.get('title').strip()
        authority_source = request.form.get('authority_source').strip()
        evacuation_route = request.form.get('evacuation_route').strip()
        safe_assembly_point = request.form.get('safe_assembly_point').strip()
        emergency_commander = request.form.get('emergency_commander').strip()
        contact_phone = request.form.get('contact_phone').strip()
        is_verified = 1 if request.form.get('is_verified') == '1' else 0

        # Handle optional file upload
        doc_file = request.files.get('protocol_file')
        doc_filename = 'protocol_document.pdf'
        if doc_file and doc_file.filename != '':
            doc_filename = secure_filename(doc_file.filename)
            doc_file.save(os.path.join(UPLOAD_PROTOCOLS_DIR, doc_filename))

        save_or_update_protocol({
            'zone_id': zone_id,
            'protocol_code': protocol_code,
            'title': title,
            'authority_source': authority_source,
            'evacuation_route': evacuation_route,
            'safe_assembly_point': safe_assembly_point,
            'emergency_commander': emergency_commander,
            'contact_phone': contact_phone,
            'is_verified': is_verified,
            'document_filename': doc_filename
        })
        flash(f"Safety Protocol for Zone ID {zone_id} saved successfully.", 'success')
        return redirect(url_for('admin'))

    # Retrain model handling
    if request.method == 'POST' and request.form.get('action') == 'retrain_model':
        try:
            train_and_evaluate_models()
            reload_model_bundle()
            flash("Machine Learning models retrained and serialized successfully.", 'success')
        except Exception as e:
            flash(f"Error during retraining: {str(e)}", 'danger')
        return redirect(url_for('admin'))

    # Fetch zones, thresholds, and prediction history
    cursor.execute('SELECT * FROM zones ORDER BY id ASC')
    zones = [dict(r) for r in cursor.fetchall()]

    cursor.execute('SELECT * FROM threshold_configs ORDER BY id ASC')
    thresholds = [dict(r) for r in cursor.fetchall()]

    cursor.execute('SELECT * FROM prediction_history ORDER BY timestamp DESC LIMIT 20')
    prediction_history = [dict(r) for r in cursor.fetchall()]

    # Load model evaluation metrics from JSON
    metrics_path = os.path.join(MODELS_DIR, 'model_metrics.json')
    model_metrics = {}
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            model_metrics = json.load(f)

    conn.close()
    return render_template(
        'admin.html',
        zones=zones,
        thresholds=thresholds,
        prediction_history=prediction_history,
        metrics=model_metrics
    )


@app.route('/about')
def about():
    """Module 8: About Project and Academic Evaluation Dossier."""
    metrics_path = os.path.join(MODELS_DIR, 'model_metrics.json')
    metrics = {}
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)

    return render_template('about.html', metrics=metrics)


@app.route('/chatbot')
@app.route('/assistant')
def chatbot():
    """Module 9: Interactive TerraSense AI Assistant & RAG Chatbot."""
    return render_template('chatbot.html')


# -------------------------------------------------------------------------
# REST API Endpoints (For Asynchronous UI Updates & Testing)
# -------------------------------------------------------------------------

@app.route('/api/stats')
def api_stats():
    """Returns real-time risk statistics for dashboard charts."""
    summary = get_dashboard_summary()
    return jsonify(summary)


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """JSON API for real-time model inference and rule check."""
    data = request.get_json() or {}
    try:
        pred = predict_risk(data)
        rule_eval = evaluate_sensor_readings(data)
        return jsonify({
            'success': True,
            'prediction': pred,
            'extreme_rules': rule_eval
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/protocol/<int:zone_id>')
def api_protocol(zone_id):
    """Returns grounded evacuation directive JSON."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM zones WHERE id = ?', (zone_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({'error': 'Zone not found'}), 404

    notice = generate_grounded_evacuation_notice(
        dict(row),
        trigger_reason="API Telemetry Trigger",
        alert_severity=row['current_risk']
    )
    return jsonify(notice)


@app.route('/api/chat', methods=['POST'])
@app.route('/api/rag/ask', methods=['POST'])
def api_rag_ask():
    """JSON API for RAG AI Question Answering & ChatGPT-Style Conversational Intelligence."""
    data = request.get_json(silent=True) or request.form or {}
    query = (data.get('query') or data.get('rag_query') or data.get('message') or '').strip()
    zone_id = data.get('zone_id')
    telemetry = data.get('sensor_telemetry')
    if not query:
        return jsonify({'success': False, 'error': 'Query text is required'}), 400
    try:
        if zone_id is not None:
            zone_id = int(zone_id)
    except (ValueError, TypeError):
        zone_id = None

    result = process_chat_query(query, zone_id=zone_id, sensor_telemetry=telemetry)
    return jsonify(result)


@app.route('/api/knowledge-base', methods=['GET'])
def api_knowledge_base():
    """Returns all indexed knowledge topics across all domains."""
    topics = get_all_indexed_topics()
    return jsonify({
        'success': True,
        'topics': topics,
        'total_indexed': len(topics)
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("="*60)
    print("Rockfall Early Warning and Response Coordination System")
    print(f"Server starting on http://127.0.0.1:{port} (0.0.0.0)")
    print("="*60)
    app.run(host='0.0.0.0', port=port, debug=False)
