from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "rb_sqli_secret"
PORT = 5001

# Database Connection
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")


# -------------------------
# VULNERABLE LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # ❌ SQL Injection Vulnerable Query
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        conn = get_db()
        user = conn.execute(query).fetchone()

        if user:
            session["user"] = user["username"]
            session["is_admin"] = (user["role"] == "admin")
            return redirect("/dashboard")
        error = "Invalid credentials!"

    return render_template("login.html", error=error)


# -------------------------
# DASHBOARD
# -------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html", user=session["user"], is_admin=session.get("is_admin"))


# -------------------------
# VULNERABLE SEARCH (SQLi)
# -------------------------
@app.route("/search", methods=["GET", "POST"])
def search():
    result = None
    if request.method == "POST":
        search_term = request.form["q"]

        # ❌ SQL Injection Vulnerable Query
        query = f"SELECT username, email FROM users WHERE username LIKE '%{search_term}%'"
        conn = get_db()
        result = conn.execute(query).fetchall()

    return render_template("search.html", result=result)


# -------------------------
# ADMIN PANEL (Access via SQLi)
# -------------------------
@app.route("/admin")
def admin():
    if not session.get("is_admin"):
        return redirect("/login")
    conn = get_db()
    users = conn.execute("SELECT * FROM users").fetchall()
    return render_template("admin.html", users=users)


# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
