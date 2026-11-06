from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import pandas as pd
from config import FEATURES, DEFAULT_THRESHOLDS, DATASET
from database import initialize_database, connect
from ml_pipeline import train_and_evaluate, load_bundle, predict, get_dataset
from risk_engine import evaluate_thresholds
from response_engine import response_message

app = Flask(__name__)
app.secret_key = "replace-with-a-random-secret-before-deployment"
initialize_database()

def current_thresholds(con):
    return {r["sensor_key"]:r["threshold_value"] for r in con.execute("SELECT * FROM threshold_config")}

def form_values(form):
    return {key:float(form[key]) for key in FEATURES}

@app.route("/")
def dashboard():
    with connect() as con:
        zones = con.execute("SELECT * FROM zones ORDER BY zone_code").fetchall()
        observations = con.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        open_alerts = con.execute("SELECT COUNT(*) FROM alerts WHERE status!='RESOLVED'").fetchone()[0]
        recent = con.execute("""SELECT a.*,z.zone_name,z.zone_code FROM alerts a
            JOIN zones z ON z.id=a.zone_id ORDER BY a.id DESC LIMIT 6""").fetchall()
        latest = con.execute("""SELECT o.*,z.zone_name,z.zone_code FROM observations o
            JOIN zones z ON z.id=o.zone_id ORDER BY o.id DESC LIMIT 8""").fetchall()
        class_counts = {c:con.execute("SELECT COUNT(*) FROM observations WHERE predicted_class=?",(c,)).fetchone()[0]
                        for c in ["LOW","MODERATE","HIGH"]}
    bundle = load_bundle()
    return render_template("dashboard.html", zones=zones, observations=observations,
                           open_alerts=open_alerts, recent=recent, latest=latest,
                           class_counts=class_counts, metrics=bundle["metrics"])

@app.route("/predict", methods=["GET","POST"])
def prediction():
    result = None
    with connect() as con:
        zones = con.execute("SELECT * FROM zones ORDER BY zone_code").fetchall()
        thresholds = current_thresholds(con)
    if request.method == "POST":
        try:
            values = form_values(request.form)
            zone_id = int(request.form["zone_id"])
            label, confidence, probabilities = predict(values)
            events = evaluate_thresholds(values, thresholds)
            with connect() as con:
                con.execute("""INSERT INTO observations(zone_id,rainfall_mm_hr,slope_angle_deg,vibration_rms,
                    soil_moisture_pct,displacement_mm,rock_movement_mm_hr,predicted_class,confidence)
                    VALUES(?,?,?,?,?,?,?,?,?)""", (zone_id,*[values[k] for k in FEATURES],label,confidence))
                for event in events:
                    con.execute("""INSERT INTO alerts(zone_id,sensor_key,sensor_value,threshold_value,
                        explanation,severity) VALUES(?,?,?,?,?,?)""",
                        (zone_id,event["sensor"],event["value"],event["threshold"],event["explanation"],event["severity"]))
                response = response_message(con,zone_id,label,events)
                zone = con.execute("SELECT zone_name,zone_code FROM zones WHERE id=?",(zone_id,)).fetchone()
            result = {"label":label,"confidence":confidence,"probabilities":probabilities,
                      "events":events,"response":response,"zone":zone}
        except Exception as e:
            flash(f"Analysis failed: {e}","error")
    return render_template("prediction.html", zones=zones, result=result, features=FEATURES)

@app.route("/zones", methods=["GET","POST"])
def zones():
    if request.method == "POST":
        try:
            with connect() as con:
                con.execute("INSERT INTO zones(zone_code,zone_name,geology,location_ref) VALUES(?,?,?,?)",
                            (request.form["zone_code"].upper(),request.form["zone_name"],
                             request.form.get("geology",""),request.form.get("location_ref","")))
            flash("Monitoring zone registered.","success")
        except Exception as e:
            flash(f"Could not add zone: {e}","error")
        return redirect(url_for("zones"))
    with connect() as con:
        items = con.execute("SELECT * FROM zones ORDER BY zone_code").fetchall()
    return render_template("zones.html",zones=items)

@app.route("/observations")
def observations():
    with connect() as con:
        rows = con.execute("""SELECT o.*,z.zone_name,z.zone_code FROM observations o
            JOIN zones z ON z.id=o.zone_id ORDER BY o.id DESC LIMIT 250""").fetchall()
    return render_template("observations.html",rows=rows)

@app.route("/alerts", methods=["GET","POST"])
def alerts():
    if request.method == "POST":
        status = request.form.get("status","OPEN")
        if status not in ["OPEN","INVESTIGATING","RESOLVED"]: status="OPEN"
        with connect() as con:
            con.execute("UPDATE alerts SET status=? WHERE id=?",(status,int(request.form["alert_id"])))
        flash("Alert workflow updated.","success")
        return redirect(url_for("alerts"))
    with connect() as con:
        rows = con.execute("""SELECT a.*,z.zone_name,z.zone_code FROM alerts a
            JOIN zones z ON z.id=a.zone_id ORDER BY a.id DESC""").fetchall()
    return render_template("alerts.html",rows=rows)

@app.route("/protocols", methods=["GET","POST"])
def protocols():
    if request.method == "POST":
        verified = 1 if request.form.get("verified") == "on" else 0
        zone_id = request.form.get("zone_id") or None
        with connect() as con:
            con.execute("""INSERT INTO protocols(zone_id,title,content,source_reference,verified)
                VALUES(?,?,?,?,?)""",(zone_id,request.form["title"],request.form["content"],
                                       request.form["source_reference"],verified))
        flash("Protocol record saved.","success")
        return redirect(url_for("protocols"))
    with connect() as con:
        rows = con.execute("""SELECT p.*,z.zone_name FROM protocols p LEFT JOIN zones z
            ON z.id=p.zone_id ORDER BY p.id DESC""").fetchall()
        zones = con.execute("SELECT * FROM zones").fetchall()
    return render_template("protocols.html",rows=rows,zones=zones)

@app.route("/model-lab")
def model_lab():
    metrics = load_bundle()["metrics"]
    return render_template("model_lab.html",m=metrics)

@app.route("/train", methods=["POST"])
def train():
    try:
        metrics = train_and_evaluate()
        flash(f"Model retrained. Test accuracy: {metrics['accuracy']}% (synthetic/demo dataset).","success")
    except Exception as e:
        flash(f"Training failed: {e}","error")
    return redirect(url_for("model_lab"))

@app.route("/thresholds", methods=["GET","POST"])
def thresholds():
    if request.method == "POST":
        with connect() as con:
            for key in FEATURES:
                con.execute("UPDATE threshold_config SET threshold_value=? WHERE sensor_key=?",
                            (float(request.form[key]),key))
        flash("Threshold configuration updated.","success")
        return redirect(url_for("thresholds"))
    with connect() as con:
        values = current_thresholds(con)
    return render_template("thresholds.html",values=values)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True,port=5001)
