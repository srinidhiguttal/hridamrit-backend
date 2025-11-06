from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}}, supports_credentials=True)

DB_PATH = "users.db"

# ---------- Database Setup ----------
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)
    print("✅ Users database ready.")

init_db()

# ---------- Routes ----------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return jsonify({"error": "All fields are required"}), 400

    if "@" not in email or "." not in email:
        return jsonify({"error": "Invalid email format"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    hashed_pw = generate_password_hash(password)

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_pw))
            conn.commit()
        print(f"🆕 User registered: {email}")
        return jsonify({"message": "Signup successful!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT password FROM users WHERE email=?", (email,))
        row = cursor.fetchone()

    if not row:
        return jsonify({"error": "User not found"}), 404

    if not check_password_hash(row[0], password):
        return jsonify({"error": "Invalid password"}), 401

    print(f"✅ Login success for {email}")
    return jsonify({"message": "Login successful"}), 200


if __name__ == "__main__":
    print("🚀 Authentication server running at http://localhost:5000")
    app.run(debug=True, port=5000)
