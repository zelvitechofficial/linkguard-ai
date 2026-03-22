import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import json

# Ensure python path catches the app module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.lexical_analysis import URLExtractor
from app.services.ml_service import FEATURE_ORDER

def train():
    print("Loading Kaggle Dataset...")
    csv_path = os.path.join(os.path.dirname(__file__), 'dataset', 'malicious_phish.csv')
    df = pd.read_csv(csv_path)
    
    df.columns = df.columns.str.strip()
    if 'type' not in df.columns and len(df.columns) >= 2:
        df.rename(columns={df.columns[1]: 'type', df.columns[0]: 'url'}, inplace=True)
    
    # Stratified sampling to cut down training time 
    # (Full 650k dataset feature extraction takes too long for a live hot-reload scenario)
    sample_size = 50000
    if len(df) > sample_size:
        print(f"Sampling {sample_size} records to optimize training time...")
        df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)
    
    urls = df['url'].tolist()
    labels = df['type'].tolist()
    
    label_map = {'benign': 0, 'phishing': 1, 'malware': 1, 'defacement': 1}
    y = np.array([label_map.get(str(l).lower(), 1) for l in labels])
    
    print(f"Extracting 18 Lexical Features from {len(urls)} URLs...")
    feature_order = FEATURE_ORDER
    
    X = []
    extractor = URLExtractor()
    
    for url in urls:
        # Some URLs in dataset lack protocols, the extractor can handle raw domains
        features_dict = extractor.extract_features(url if url.startswith('http') else 'http://' + url)
        feature_vector = [features_dict.get(f, 0) for f in feature_order]
        X.append(feature_vector)
        
    X = np.array(X)
    
    print("Splitting dataset into Training (80%) and Testing (20%) sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    
    print("Training Decision Tree...")
    dt_model = DecisionTreeClassifier(random_state=42)
    dt_model.fit(X_train, y_train)
    
    print("Evaluating models...")
    rf_preds = rf_model.predict(X_test)
    dt_preds = dt_model.predict(X_test)
    
    rf_metrics = {
        "accuracy": float(accuracy_score(y_test, rf_preds)),
        "precision": float(precision_score(y_test, rf_preds)),
        "recall": float(recall_score(y_test, rf_preds)),
        "f1_score": float(f1_score(y_test, rf_preds))
    }
    
    dt_metrics = {
        "accuracy": float(accuracy_score(y_test, dt_preds)),
        "precision": float(precision_score(y_test, dt_preds)),
        "recall": float(recall_score(y_test, dt_preds)),
        "f1_score": float(f1_score(y_test, dt_preds))
    }
    
    print(f"Random Forest Accuracy: {rf_metrics['accuracy'] * 100:.2f}%")
    print(f"Decision Tree Accuracy: {dt_metrics['accuracy'] * 100:.2f}%")
    
    # Extract feature importance
    importances = rf_model.feature_importances_
    feature_importance_dict = {feature_order[i]: float(importances[i]) for i in range(len(feature_order))}
    
    metrics = {
        "random_forest": rf_metrics,
        "decision_tree": dt_metrics,
        "feature_importance": feature_importance_dict
    }
    
    models_dir = os.path.join(os.path.dirname(__file__), 'ml_models')
    os.makedirs(models_dir, exist_ok=True)
    
    print("Saving Models to /ml_models...")
    joblib.dump(rf_model, os.path.join(models_dir, 'random_forest.joblib'))
    joblib.dump(dt_model, os.path.join(models_dir, 'decision_tree.joblib'))
    
    metrics_path = os.path.join(models_dir, 'metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=4)
        
    print(f"Metrics saved to {metrics_path}")
    print("SUCCESS: Models baked!")

if __name__ == "__main__":
    train()
