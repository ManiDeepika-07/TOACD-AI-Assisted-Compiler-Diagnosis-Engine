import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

from sklearn.metrics import accuracy_score



def train():
    data_path = "data/features_new.csv"
    if not os.path.exists(data_path):
        data_path = "data/features.csv"
        
    if not os.path.exists(data_path):
        print("Features file not found! Run process_dataset.py first.")
        return
        
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path, keep_default_na=False)
    
    # Features are everything except label columns
    X = df.drop(columns=["file", "error_type", "severity", "category", "nature"])
    y_type = df["error_type"]
    y_sev = df["severity"]
    y_cat = df["category"]
    y_nat = df["nature"]
    
    print(f"Features: {list(X.columns)}")
    
    # Train Error Type Model
    X_train, X_test, y_train, y_test = train_test_split(X, y_type, test_size=0.2, random_state=42)
    model_type = RandomForestClassifier(n_estimators=100, random_state=42)
    model_type.fit(X_train, y_train)
    print("\nError Type Classification Report:")
    print(classification_report(y_test, model_type.predict(X_test)))
    
    # Train Severity Model
    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(X, y_sev, test_size=0.2, random_state=42)
    model_sev = RandomForestClassifier(n_estimators=100, random_state=42)
    model_sev.fit(X_train_s, y_train_s)
    print("\nSeverity Classification Report:")
    print(classification_report(y_test_s, model_sev.predict(X_test_s)))

    # Train Category Model (Compile-time vs Runtime)
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X, y_cat, test_size=0.2, random_state=42)
    model_cat = RandomForestClassifier(n_estimators=100, random_state=42)
    model_cat.fit(X_train_c, y_train_c)
    print("\nCategory Classification Report:")
    print(classification_report(y_test_c, model_cat.predict(X_test_c)))

    # Train Nature Model (Syntax vs Logical)
    X_train_n, X_test_n, y_train_n, y_test_n = train_test_split(X, y_nat, test_size=0.2, random_state=42)
    model_nat = RandomForestClassifier(n_estimators=100, random_state=42)
    model_nat.fit(X_train_n, y_train_n)
    print("\nNature Classification Report:")
    print(classification_report(y_test_n, model_nat.predict(X_test_n)))
    
       # Accuracy scores
    print("\nAccuracies:")
    print("Type:", accuracy_score(y_test, model_type.predict(X_test)))
    print("Severity:", accuracy_score(y_test_s, model_sev.predict(X_test_s)))
    print("Category:", accuracy_score(y_test_c, model_cat.predict(X_test_c)))
    print("Nature:", accuracy_score(y_test_n, model_nat.predict(X_test_n)))

    # Save models
    os.makedirs("models", exist_ok=True)
    joblib.dump(model_type, "models/error_classifier.pkl")
    joblib.dump(model_sev, "models/severity_classifier.pkl")
    joblib.dump(model_cat, "models/category_classifier.pkl")
    joblib.dump(model_nat, "models/nature_classifier.pkl")
    joblib.dump(list(X.columns), "models/feature_columns.pkl")
    
    print("\nModels saved to models/ directory.")

if __name__ == "__main__":
    train()
    
