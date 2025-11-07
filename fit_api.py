from flask import Flask, request, jsonify, redirect, session, url_for
from google_auth_oauthlib.flow import Flow
import requests, os, time
from flask_cors import CORS
from predict import predict_heart_attack  # Your ML predict function

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24))  # ✅ Masked, loaded from environment
CORS(app)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Allow HTTP for local testing

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = [
    "https://www.googleapis.com/auth/fitness.activity.read",
    "https://www.googleapis.com/auth/fitness.sleep.read",
    "https://www.googleapis.com/auth/fitness.body.read",
]

# ---------------- HOME ROUTE ----------------
@app.route('/')
def home():
    return jsonify({"message": "💖 Hridamrit Backend is Running Successfully!"}), 200


# ---------------- GOOGLE LOGIN ----------------
@app.route("/login")
def login():
    redirect_uri = url_for('oauth2callback', _external=True)
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, redirect_uri=redirect_uri)
    auth_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")
    session["state"] = state
    return redirect(auth_url)


@app.route("/oauth2callback")
def oauth2callback():
    redirect_uri = url_for('oauth2callback', _external=True)
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=session.get("state"), redirect_uri=redirect_uri
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    session["token"] = credentials.token
    return "✅ Google login successful! Now go to /predict_fit"


# ---------------- FETCH GOOGLE FIT DATA ----------------
def get_fit_data(token):
    headers = {"Authorization": f"Bearer {token}"}
    now = int(time.time() * 1000)
    one_week_ago = now - 7 * 24 * 60 * 60 * 1000

    def aggregate_data(data_type):
        body = {
            "aggregateBy": [{"dataTypeName": data_type}],
            "bucketByTime": {"durationMillis": 86400000},
            "startTimeMillis": one_week_ago,
            "endTimeMillis": now,
        }
        res = requests.post(
            "https://fitness.googleapis.com/fitness/v1/users/me/dataset:aggregate",
            headers=headers,
            json=body
        ).json()

        total = count = 0
        for bucket in res.get("bucket", []):
            for dataset in bucket.get("dataset", []):
                for point in dataset.get("point", []):
                    for val in point.get("value", []):
                        if "fpVal" in val:
                            total += val["fpVal"]
                            count += 1
        return (total / count) if count > 0 else 0

    fit_data = {
        "avg_steps": aggregate_data("com.google.step_count.delta"),
        "avg_calories": aggregate_data("com.google.calories.expended"),
        "height": aggregate_data("com.google.height"),  # meters
        "weight": aggregate_data("com.google.weight")   # kg
    }

    if fit_data["height"] == 0:
        fit_data["height"] = 1.7
    if fit_data["weight"] == 0:
        fit_data["weight"] = 70

    return fit_data


# ---------------- PREDICTION ----------------
@app.route("/predict_fit", methods=["GET", "POST"])
def predict_fit():
    token = session.get("token")
    fit_data = get_fit_data(token) if token else {"avg_steps": 4000, "avg_calories": 2000, "height": 1.7, "weight": 70}

    manual_data = {}
    if request.method == "POST":
        if request.is_json:
            manual_data = request.get_json()
        else:
            return jsonify({"error": "Content-Type must be application/json"}), 415

    final_data = {
        "age": manual_data.get("age", 30),
        "gender": manual_data.get("gender", 1),
        "height": fit_data.get("height"),
        "weight": fit_data.get("weight"),
        "ap_hi": manual_data.get("ap_hi", 120),
        "ap_lo": manual_data.get("ap_lo", 80),
        "cholesterol": manual_data.get("cholesterol", 2),
        "gluc": manual_data.get("gluc", 1),
        "smoke": manual_data.get("smoke", 0),
        "alco": manual_data.get("alco", 0),
        "active": 1 if fit_data["avg_steps"] > 5000 else 0,
        "bmi": manual_data.get("bmi", fit_data["weight"] / (fit_data["height"] ** 2))
    }

    pred_class, pred_proba = predict_heart_attack(final_data)

    return jsonify({
        "fit_data": fit_data,
        "manual_input": final_data,
        "predicted_class": pred_class,
        "probability": round(pred_proba, 4)
    })


# ---------------- HEALTH CHECK ----------------
@app.route('/health')
def health_check():
    return {"status": "Backend running successfully"}, 200


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
