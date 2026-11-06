import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from config import FEATURES, TARGET, DATASET, MODEL_FILE

CLASSES = ["LOW", "MODERATE", "HIGH"]

def create_demo_dataset(rows=1200, seed=27):
    """Generate labelled synthetic data for interface and pipeline demonstration."""
    rng = np.random.default_rng(seed)
    data = []
    for _ in range(rows):
        vals = [
            rng.uniform(0, 100), rng.uniform(18, 78), rng.uniform(0.02, 1.4),
            rng.uniform(12, 100), rng.uniform(0, 35), rng.uniform(0, 28)
        ]
        # Transparent rule used only to create demo labels, not a validated hazard model.
        normalized = np.array([
            vals[0]/100, vals[1]/80, vals[2]/1.4,
            vals[3]/100, vals[4]/35, vals[5]/28
        ])
        score = 0.18*normalized[0] + 0.14*normalized[1] + 0.17*normalized[2] + 0.13*normalized[3] + 0.20*normalized[4] + 0.18*normalized[5]
        score += rng.normal(0, 0.035)
        label = "LOW" if score < 0.34 else ("MODERATE" if score < 0.58 else "HIGH")
        data.append(vals + [label])
    df = pd.DataFrame(data, columns=FEATURES + [TARGET])
    DATASET.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATASET, index=False)
    return df

def get_dataset():
    if not DATASET.exists():
        return create_demo_dataset()
    return pd.read_csv(DATASET)

def build_pipeline():
    prep = ColumnTransformer([
        ("numeric", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]), FEATURES)
    ])
    return Pipeline([
        ("preprocess", prep),
        ("classifier", RandomForestClassifier(
            n_estimators=240, max_depth=12, min_samples_leaf=2,
            class_weight="balanced_subsample", random_state=27, n_jobs=-1
        ))
    ])

def train_and_evaluate():
    df = get_dataset()
    X, y = df[FEATURES], df[TARGET].astype(str).str.upper()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.22, random_state=27, stratify=y
    )
    pipeline = build_pipeline()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=27)
    scores = cross_validate(pipeline, X_train, y_train, cv=cv,
                            scoring={"accuracy":"accuracy","f1_macro":"f1_macro"},
                            return_train_score=False)
    pipeline.fit(X_train, y_train)
    pred = pipeline.predict(X_test)
    labels = [c for c in CLASSES if c in sorted(y.unique())]
    report = classification_report(y_test, pred, labels=labels, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_test, pred, labels=labels)
    importance = permutation_importance(pipeline, X_test, y_test, n_repeats=5,
                                         random_state=27, scoring="f1_macro")
    fi = sorted(zip(FEATURES, importance.importances_mean), key=lambda x:x[1], reverse=True)
    metrics = {
        "accuracy": round(accuracy_score(y_test,pred)*100,2),
        "f1": round(f1_score(y_test,pred,average="macro")*100,2),
        "cv_accuracy": round(float(scores["test_accuracy"].mean())*100,2),
        "cv_std": round(float(scores["test_accuracy"].std())*100,2),
        "report": report, "labels": labels, "confusion": cm.tolist(),
        "importance_names": [x[0] for x in fi],
        "importance_values": [round(float(x[1]),5) for x in fi],
        "rows": len(df), "synthetic": True
    }
    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline":pipeline,"features":FEATURES,"metrics":metrics}, MODEL_FILE)
    return metrics

def load_bundle():
    if not MODEL_FILE.exists():
        train_and_evaluate()
    return joblib.load(MODEL_FILE)

def predict(values):
    bundle = load_bundle()
    row = pd.DataFrame([[float(values[f]) for f in FEATURES]], columns=FEATURES)
    model = bundle["pipeline"]
    prediction = str(model.predict(row)[0])
    probabilities = model.predict_proba(row)[0]
    confidence = float(max(probabilities))*100
    class_probabilities = {str(k): round(float(v)*100,2) for k,v in zip(model.classes_,probabilities)}
    return prediction, round(confidence,2), class_probabilities
