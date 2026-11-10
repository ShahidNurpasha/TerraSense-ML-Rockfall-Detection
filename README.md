# Rockfall Early Warning and Response Coordination System for Decision Support (TerraSense ML)

[![Live Demo](https://img.shields.io/badge/Live_Demo-Render_Deployment-success?style=for-the-badge&logo=render)](https://terrasense-ml-rockfall-detection.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask_3.1-black.svg)](https://flask.palletsprojects.com/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-orange.svg)](https://scikit-learn.org/)
[![Database](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)](https://sqlite.org/)

> 🌐 **Live Cloud Deployment URL:** [https://terrasense-ml-rockfall-detection.onrender.com/](https://terrasense-ml-rockfall-detection.onrender.com/)

An AI-powered decision support web application that identifies potential rockfall risks from geological sensor telemetry, detects extreme reading anomalies through an independent deterministic backstop, and provides grounded evacuation coordination based exclusively on verified safety protocols.

---

## 🎓 Academic Project Information

- **Project Title:** Rockfall Early Warning and Response Coordination System for Decision Support
- **Course / Outcome:** SDE 2025 (Record ID: SDE25071) / CO3, CO4, CO5
- **Section / Group:** K23PD1L (Group Project)
- **Students / Investigators:**
  1. **Murpasha Sachid** | Reg No: `12513246` | Roll No: `RE3F261LA05`
  2. **Danala Yaswanth** | Reg No: `12501101` | Roll No: `RE3F261LA27`
- **Methodology & Competencies:** Supervised Classification, Production Systems, Explainable AI (XAI), Geotechnical Engineering Constraints.

---

## 🏛️ System Architecture & Three Core Pillars

The application combines three independent but tightly coordinated components into one cohesive web dashboard:

```
                          ┌──────────────────────────────────────────────┐
                          │         SENSOR & GEOLOGICAL TELEMETRY        │
                          │ Rainfall, Slope, Vibration, Moisture, Displ. │
                          └──────────────────────┬───────────────────────┘
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        │                                                 │
                        ▼                                                 ▼
        ┌───────────────────────────────┐                 ┌───────────────────────────────┐
        │   PILLAR 1: SUPERVISED ML     │                 │    PILLAR 2: RULE BACKSTOP    │
        │      (Probabilistic)          │                 │        (Deterministic)        │
        │  • Random Forest (Primary)    │                 │  • Configurable Thresholds    │
        │  • Decision Tree (Comparison) │                 │  • Operates unconditionally   │
        │  • Confidence & XAI Drivers   │                 │  • Explains physical danger   │
        └───────────────┬───────────────┘                 └───────────────┬───────────────┘
                        │                                                 │
                        └────────────────────────┬────────────────────────┘
                                                 │
                                                 ▼
                                ┌─────────────────────────────────┐
                                │   ELEVATED HAZARD ARBITRATION   │
                                └────────────────┬────────────────┘
                                                 │
                                                 ▼
                                ┌─────────────────────────────────┐
                                │   PILLAR 3: EMERGENCY GROUNDING │
                                │  • Retrieves Verified SOPs      │
                                │  • Zero Hallucination Constraint│
                                │  • Exact Routes & Assembly Pt   │
                                └─────────────────────────────────┘
```

1. **Pillar 1: Supervised Machine Learning Classifier**
   - Classifies multi-sensor telemetry into **Low Risk**, **Medium Risk**, or **High Risk**.
   - Primary model: **Random Forest** (85.0% accuracy, 85.0% 5-fold cross-validation).
   - Comparison benchmark: **Decision Tree** (75.0% accuracy).
   - Provides confidence scores and **Explainable AI (XAI)** feature contribution breakdowns.

2. **Pillar 2: Independent Rule-Based Extreme Reading Backstop**
   - Operates completely decoupled from the machine learning model.
   - Monitors physical thresholds (e.g., Displacement Rate > 15 mm/day, Rainfall > 120 mm/24h, Vibration PPV > 9 mm/s).
   - **Crucial Safety Guarantee:** Even if the ML model outputs "Low Risk" (e.g. edge-case sensor anomaly), this backstop unconditionally fires an emergency alert and explains why the reading is geotechnically dangerous.

3. **Pillar 3: Grounded Emergency Response Coordination**
   - **Zero Hallucination Constraint:** The system strictly refuses to invent or guess evacuation routes, safe assembly muster stations, or commander contacts.
   - For zones with registered, administrator-verified Standard Operating Procedures (SOPs), it delivers official directives citing regulatory authority documents (e.g., Mines Safety Directorate / SDMA).
   - For unverified zones, it explicitly triggers a safety fallback advisory directing personnel to emergency services (112).

---

## 📂 Project Folder Structure

```
rockfall_warning_system/
│
├── app.py                     # Flask application server and routing logic
├── model.py                   # ML data processing, training, 5-fold CV & evaluation
├── prediction.py              # ML inference engine and Explainable AI (XAI)
├── alert_system.py            # Independent rule-based extreme reading backstop
├── emergency_response.py      # Grounded emergency protocol retrieval and safety notices
├── database.py                # SQLite database management and baseline data seeding
├── requirements.txt           # Python dependency requirements
├── test_system.py             # Automated test suite (6 passing unit tests)
├── README.md                  # Comprehensive documentation and viva guide
│
├── templates/                 # Clean, modern HTML templates
│   ├── base.html              # Base navigation layout and dark navy theme
│   ├── index.html             # Dashboard entry point
│   ├── dashboard.html         # Module 1: Metric cards and live distribution graphs
│   ├── prediction.html        # Module 2 & 3: Dual-engine prediction and scenario testing
│   ├── monitoring.html        # Module 5: Zone telemetry overview and entry modals
│   ├── sensor_data.html       # Module 5/Data: Full table, CSV download & batch upload
│   ├── alerts.html            # Module 6: Alert management and incident lifecycle
│   ├── protocols.html         # Module 4: Grounded safety protocols and evacuation drill
│   ├── admin.html             # Module 7: Threshold calibration, protocol upload, retraining
│   └── about.html             # Module 8: Academic dossier, formulas, and viva questions
│
├── static/
│   ├── css/
│   │   └── style.css          # Dark blue & white styling with green/amber/red status badges
│   ├── js/
│   │   └── script.js          # Interactive scenario presets and search filters
│   └── img/
│       ├── confusion_matrix.png     # Generated Matplotlib confusion matrix
│       └── feature_importance.png   # Generated Matplotlib feature importance chart
│
├── data/
│   └── sample_dataset.csv     # 1,000 curated synthetic geotechnical sensor records
│
├── models/
│   ├── rockfall_model.pkl     # Serialized Joblib model bundle and preprocessors
│   └── model_metrics.json     # Saved evaluation metrics and cross-validation statistics
│
└── uploads/
    └── protocols/             # Storage for administrator-uploaded verified SOP documents
```

---

## 🚀 Installation & Quick Start Guide (Windows)

### Prerequisites
- Python 3.10+ or Python 3.11+ installed.
- PowerShell or Command Prompt.

### Step 1: Open Terminal in Project Folder
```powershell
cd "c:\Users\hp\Desktop\anti national"
```

### Step 2: (Optional but recommended) Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Flask Web Application
```powershell
python app.py
```

### Step 5: Open Application in Web Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running Automated Unit Tests

To verify that all database tables, ML inference pipelines, rule backstops, emergency grounding logic, and web routes are operating properly:

```powershell
python test_system.py
```

Expected output:
```
......
----------------------------------------------------------------------
Ran 6 tests in 0.457s

OK
```

---

## 🎯 How to Demonstrate Key Features in a Viva Presentation

### Scenario 1: Supervised ML Risk Prediction (Normal vs High)
1. Go to **Risk Prediction** (`/prediction`).
2. Click the quick scenario preset **"🟢 Stable Low Risk"** &rarr; Notice inputs populate with normal values &rarr; Click **Execute Dual-Engine Evaluation**.
   - Result: Classified as **Low Risk** with high confidence (>90%). Rule backstop reports all parameters safe.
3. Click the preset **"🔴 High Failure Risk"** &rarr; Notice inputs set high rainfall (148 mm), steep slope (74°), and high displacement (22.4 mm/day) &rarr; Click **Execute**.
   - Result: Classified as **High Risk** (Confidence ~90%), XAI drivers highlight displacement rate and rainfall, Rule-based backstop triggers critical breaches, and an **Official Evacuation Directive** opens automatically.

### Scenario 2: The Independent Rule-Based Backstop (Crucial Safety Demo)
*Demonstrate that the rule-based system functions independently even when ML would otherwise predict lower risk.*
1. On the **Risk Prediction** page, click **"🛡️ Extreme Rule Backstop Spike"**.
2. Notice: Rainfall is low (25 mm), slope is moderate (48°), but **Ground Vibration (PPV) is 11.8 mm/s** (exceeding the critical safety limit of 9.0 mm/s).
3. Click **Execute Dual-Engine Evaluation**.
4. Observe: The rule-based backstop immediately fires a **Critical Severity Alert** with exact physical rationale: *"Peak particle velocity from blasting or seismic shock exceeds tensile strength of fractured rock joints, dislodging hanging blocks."*

### Scenario 3: Grounded Emergency Protocols vs Safety Fallback
1. Go to **Safety Protocols** (`/protocols`).
2. Click **"⚡ Test Directive"** for **ZONE-A (North Ridge Pass)**:
   - Notice: Retrieves official verified route (*Service Access Track 1*), muster station (*Assembly Point Alpha*), commander name, and cites regulatory document `SDMA-MSD-102`.
3. Click **"⚡ Test Directive"** for **ZONE-E (Railway Tunnel Portal North)**:
   - Notice: Zone E has no verified protocol. The system **refuses to hallucinate fake routes**, triggers a safety banner, and advises following official civil defense lines (112).

---

## 📊 Machine Learning Model Evaluation Report

The supervised classification models were trained and evaluated on 1,000 geotechnical sensor records with a stratified 80/20 train-test split:

| Evaluation Metric | Primary Model (Random Forest) | Comparison Model (Decision Tree) |
|---|---|---|
| **Holdout Accuracy** | **85.00%** | 75.00% |
| **Weighted Precision** | **84.83%** | 74.20% |
| **Weighted Recall** | **85.00%** | 75.00% |
| **Weighted F1-Score** | **84.83%** | 74.57% |
| **5-Fold Cross Validation** | **85.00% (+/- 2.05%)** | 77.50% |
| **Inference Latency** | < 12 ms | < 4 ms |

### Data Quality & Leakage Prevention:
- **No Data Leakage:** The `StandardScaler` was fitted exclusively on the 80% training partition; holdout test records and production queries are transformed using the saved training parameters.
- **Explainable AI (XAI):** Relative feature importances were extracted and plotted to `static/img/feature_importance.png`, demonstrating that slope displacement rate, cumulative rock movement, and rainfall intensity are the primary physical drivers of slope instability.

---

## 🎓 University Viva Voce Q&A Cheat Sheet

**Q1: Why did you use both Machine Learning and a Rule-Based System?**
> *Answer:* Supervised Machine Learning is excellent at modeling complex, non-linear relationships across multiple sensors. However, ML is probabilistic and can be sensitive to unseen noise. In rockfall monitoring, lives are at stake. The Rule-Based Backstop provides a deterministic, failsafe safety boundary: if any sensor exceeds critical physical safety limits, an emergency alert is triggered unconditionally.

**Q2: What is the Mohr-Coulomb failure criterion and how does it relate to your sensor features?**
> *Answer:* Mohr-Coulomb states that rock shear strength is $\tau = c + (\sigma - u) \tan(\phi)$. 
> - **Rainfall and soil moisture** increase pore water pressure ($u$), directly reducing effective normal stress ($\sigma' = \sigma - u$) and reducing friction.
> - **Slope angle** increases driving shear stress ($\tau_d = W \sin \theta$).
> - **Vibration** adds transient inertial acceleration.
> - **Displacement velocity** signals tertiary creep prior to catastrophic detachment.

**Q3: How does your emergency response system avoid hallucination?**
> *Answer:* The emergency coordination module retrieves only administrator-verified protocols stored in SQLite. If a zone lacks a verified SOP, the system strictly refuses to guess evacuation routes or coordinates and outputs an explicit contingency notice with official emergency helpline numbers (112).

---

## ⚖️ Project License & Disclaimer
This project is developed for university academic demonstration and decision support research. Real-world life-critical mine or slope installations require calibrated, verified on-site geotechnical sensor telemetry and local civil defense sign-off.
