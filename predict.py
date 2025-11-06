import joblib
import pandas as pd
import os

# ---------------- LOAD MODEL ----------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), "best_model", "best_final_pipeline.pkl")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ Model file not found at {MODEL_PATH}")

best_pipeline = joblib.load(MODEL_PATH)
print("✅ Best model pipeline loaded successfully!\n")

# ---------------- EXPECTED FEATURES ----------------
FEATURE_NAMES = [
    "age", "gender", "height", "weight", "ap_hi", "ap_lo",
    "cholesterol", "gluc", "smoke", "alco", "active", "bmi"
]

# ---------------- PREDICTION FUNCTION ----------------
def predict_heart_attack(input_data: dict):
    """Takes a dict with required features and returns prediction + probability."""
    missing = [f for f in FEATURE_NAMES if f not in input_data]
    if missing:
        raise KeyError(f"Missing features: {missing}")

    df = pd.DataFrame([input_data])
    pred_class = int(best_pipeline.predict(df)[0])
    pred_proba = float(best_pipeline.predict_proba(df)[0][1])
    return pred_class, pred_proba

# ---------------- MANUAL INPUT MODE ----------------
if __name__ == "__main__":
    print("🩺 Heart Attack Risk Prediction (Manual Mode)")
    print("Please enter the following details:")

    user_data = {}
    for feature in FEATURE_NAMES:
        while True:
            val = input(f"Enter {feature}: ").strip()
            if val == "":
                print("⚠️  Please enter a value for this field.")
                continue
            try:
                user_data[feature] = float(val)
                break
            except ValueError:
                print("❌ Invalid number. Please enter a numeric value.")

    print("\n🔍 Running prediction...\n")
    pred, prob = predict_heart_attack(user_data)

    print("✅ Prediction complete!")
    print(f"🧠 Predicted Class: {pred} ({'High Risk' if pred == 1 else 'Low Risk'})")
    print(f"📊 Probability of Heart Attack: {prob:.4f}")
