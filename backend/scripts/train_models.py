import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import json

# Ensure python path catches the app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.lexical_analysis import URLExtractor
from app.services.ml_service import FEATURE_ORDER

def normalize_url(url: str) -> str:
    """Strip protocols so that every URL is treated the same way during training.
    The dataset stores benign URLs mostly without protocols and malicious ones
    often with protocols — this normalization prevents that bias."""
    url = str(url).strip()
    url = url.replace('https://', '').replace('http://', '')
    url = url.strip('/')
    return url

def train():
    print("=" * 60)
    print("LinkGuard-AI Model Training v2")
    print("=" * 60)
    
    print("\nLoading Kaggle Dataset...")
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dataset', 'malicious_phish.csv'))
    df = pd.read_csv(csv_path)
    
    df.columns = df.columns.str.strip()
    if 'type' not in df.columns and len(df.columns) >= 2:
        df.rename(columns={df.columns[1]: 'type', df.columns[0]: 'url'}, inplace=True)
    
    # Binary label: 0 = benign, 1 = malicious (phishing + defacement + malware)
    df['is_malicious'] = df['type'].apply(lambda x: 1 if str(x).lower() != 'benign' else 0)
    
    # Normalize all URLs — critical for removing protocol bias
    print("Normalizing all URLs (stripping protocols)...")
    df['url'] = df['url'].apply(normalize_url)
    
    # Remove duplicates after normalization
    df = df.drop_duplicates(subset=['url']).reset_index(drop=True)
    print(f"After dedup: {len(df)} unique URLs")
    
    # --- Balanced Sampling ---
    print("\nPerforming Balanced Sampling (100k per class)...")
    malicious_df = df[df['is_malicious'] == 1]
    benign_df = df[df['is_malicious'] == 0]
    
    print(f"Available: {len(benign_df)} benign, {len(malicious_df)} malicious")
    
    sample_size = 100000  # Per class
    
    # For benign: ensure diversity — mix of root domains and paths
    benign_has_path = benign_df['url'].str.contains('/', regex=False)
    benign_root = benign_df[~benign_has_path]
    benign_path = benign_df[benign_has_path]
    
    print(f"Benign breakdown: {len(benign_root)} root domains, {len(benign_path)} with paths")
    
    # Include proportional representation of root domains
    root_ratio = len(benign_root) / len(benign_df)
    target_root = min(len(benign_root), int(sample_size * max(root_ratio, 0.20)))
    target_path = sample_size - target_root
    
    if target_path > len(benign_path):
        target_path = len(benign_path)
        target_root = sample_size - target_path
    
    benign_sample = pd.concat([
        benign_root.sample(n=min(target_root, len(benign_root)), random_state=42),
        benign_path.sample(n=min(target_path, len(benign_path)), random_state=42)
    ])
    
    # For malicious: take representative sample
    if len(malicious_df) > sample_size:
        malicious_sample = malicious_df.sample(n=sample_size, random_state=42)
    else:
        malicious_sample = malicious_df
    
    balanced_df = pd.concat([malicious_sample, benign_sample]).sample(frac=1.0, random_state=42).reset_index(drop=True)
    print(f"Training set: {len(balanced_df)} records ({(balanced_df['is_malicious']==0).sum()} benign, {(balanced_df['is_malicious']==1).sum()} malicious)")

    urls = balanced_df['url'].tolist()
    y = balanced_df['is_malicious'].values
    
    print(f"\nExtracting {len(FEATURE_ORDER)} features from {len(urls)} URLs...")
    
    X = []
    extractor = URLExtractor()
    
    count = 0
    total = len(urls)
    for url in urls:
        features_dict = extractor.extract_features(url)
        feature_vector = [features_dict.get(f, 0) for f in FEATURE_ORDER]
        X.append(feature_vector)
        count += 1
        if count % 20000 == 0:
            print(f"  Progress: {count}/{total} ({100*count/total:.0f}%)")
        
    X = np.array(X)
    
    print(f"\nSplitting into Train (80%) / Test (20%)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
    
    # --- Random Forest ---
    print("\nTraining Random Forest (200 estimators, max_depth=25)...")
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=25,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    rf_model.fit(X_train, y_train)
    
    # --- Decision Tree ---
    print("Training Decision Tree (max_depth=20)...")
    dt_model = DecisionTreeClassifier(
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        class_weight='balanced'
    )
    dt_model.fit(X_train, y_train)
    
    # --- Evaluation ---
    print("\n" + "=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)
    
    rf_preds = rf_model.predict(X_test)
    dt_preds = dt_model.predict(X_test)
    
    metrics = {
        "random_forest": {
            "accuracy": float(accuracy_score(y_test, rf_preds)),
            "precision": float(precision_score(y_test, rf_preds)),
            "recall": float(recall_score(y_test, rf_preds)),
            "f1_score": float(f1_score(y_test, rf_preds))
        },
        "decision_tree": {
            "accuracy": float(accuracy_score(y_test, dt_preds)),
            "precision": float(precision_score(y_test, dt_preds)),
            "recall": float(recall_score(y_test, dt_preds)),
            "f1_score": float(f1_score(y_test, dt_preds))
        }
    }
    
    for model_name, m in metrics.items():
        print(f"\n{model_name}:")
        print(f"  Accuracy:  {m['accuracy']*100:.2f}%")
        print(f"  Precision: {m['precision']*100:.2f}%")
        print(f"  Recall:    {m['recall']*100:.2f}%")
        print(f"  F1 Score:  {m['f1_score']*100:.2f}%")
    
    # --- Feature importance ---
    print("\nTop 10 Feature Importances (Random Forest):")
    importances = rf_model.feature_importances_
    indices = np.argsort(importances)[::-1]
    for i in range(min(10, len(FEATURE_ORDER))):
        print(f"  {FEATURE_ORDER[indices[i]]:<30} {importances[indices[i]]:.4f}")
    
    # Add feature importance to metrics (used by the frontend ML Monitoring page)
    metrics["feature_importance"] = {
        FEATURE_ORDER[i]: float(importances[i]) for i in indices
    }
    
    # --- Save ---
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app', 'ml_models'))
    os.makedirs(models_dir, exist_ok=True)
    
    print("\nSaving models...")
    joblib.dump(rf_model, os.path.join(models_dir, 'random_forest.joblib'))
    joblib.dump(dt_model, os.path.join(models_dir, 'decision_tree.joblib'))
    
    metrics_path = os.path.join(models_dir, 'metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=4)
        
    print(f"Metrics saved to {metrics_path}")
    
    # --- Quick sanity check on known URLs ---
    print("\n" + "=" * 60)
    print("SANITY CHECK")
    print("=" * 60)
    
    test_urls = [
        ("https://www.google.com", "SAFE"),
        ("https://github.com/repo/project", "SAFE"),
        ("https://stackoverflow.com/questions", "SAFE"),
        ("http://phish-site.com/login/verify-account", "MALICIOUS"),
        ("http://login-google.com", "MALICIOUS"),
        ("http://google-verify.xyz", "MALICIOUS"),
        ("http://192.168.1.1/admin/config.php", "MALICIOUS"),
    ]
    
    print(f"\n{'URL':<45} {'RF%':<8} {'DT%':<8} {'Expected':<10} {'RF Result'}")
    print("-" * 95)
    
    for url, expected in test_urls:
        feats = extractor.extract_features(url)
        vec = np.array([feats.get(f, 0) for f in FEATURE_ORDER]).reshape(1, -1)
        rf_prob = rf_model.predict_proba(vec)[0][1]
        dt_prob = dt_model.predict_proba(vec)[0][1]
        result = "Malicious" if rf_prob > 0.5 else "Safe"
        match = "PASS" if (result.upper() == expected) else "FAIL"
        print(f"{url:<45} {rf_prob:<8.4f} {dt_prob:<8.4f} {expected:<10} {result} {match}")
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    train()
