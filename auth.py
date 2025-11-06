from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3, re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY"
CORS(app)

# ---------- DATABASE ----------
def init_db():
    con = sqlite3.connect("users.db")
    con.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT)""")
    con.close()
init_db()

# ---------- SIGNUP ----------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name, email, password = data.get("name"), data.get("email"), data.get("password")
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return jsonify({"error": "Invalid email"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password too weak"}), 400
    hashed = generate_password_hash(password)
    try:
        con = sqlite3.connect("users.db")
        con.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)", (name,email,hashed))
        con.commit()
        return jsonify({"msg":"Signup successful"})
    except sqlite3.IntegrityError:
        return jsonify({"error":"Email already exists"}),400
    finally: con.close()

# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email, password = data.get("email"), data.get("password")
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    cur.execute("SELECT password FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    con.close()
    if not row or not check_password_hash(row[0], password):
        return jsonify({"error": "Invalid credentials"}), 401
    session["user"] = email
    return jsonify({"msg": "Login successful"})

if __name__ == "__main__":
    app.run(debug=True)
