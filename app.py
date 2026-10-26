import os, sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session

ROOT = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(ROOT, "morning_star.db")
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "replace-this-secret-before-deployment")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "MorningStar@123")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_name TEXT NOT NULL, child_name TEXT NOT NULL, phone TEXT NOT NULL,
            email TEXT, class_name TEXT NOT NULL, branch TEXT, message TEXT,
            created_at TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT,
            email TEXT, subject TEXT, message TEXT NOT NULL, created_at TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, body TEXT NOT NULL,
            created_at TEXT NOT NULL)""")
        if con.execute("SELECT COUNT(*) FROM announcements").fetchone()[0] == 0:
            con.execute("INSERT INTO announcements(title,body,created_at) VALUES(?,?,?)",
                ("Welcome to Morning Star!", "Where Learning Begins with Joy! Contact us for class and admission information.", now()))

def now():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")

def admin_only(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            flash("Please log in to access the admin dashboard.", "warning")
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    with db() as con:
        announcements = con.execute("SELECT * FROM announcements ORDER BY id DESC LIMIT 4").fetchall()
    return render_template("index.html", announcements=announcements)

@app.route("/admissions", methods=["GET", "POST"])
def admissions():
    if request.method == "POST":
        fields = {key: request.form.get(key, "").strip() for key in
                  ["parent_name", "child_name", "phone", "email", "class_name", "branch", "message"]}
        if not all(fields[k] for k in ["parent_name", "child_name", "phone", "class_name"]):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("admissions"))
        if len(fields["phone"]) < 7 or len(fields["phone"]) > 20:
            flash("Please enter a valid contact number.", "error")
            return redirect(url_for("admissions"))
        with db() as con:
            con.execute("""INSERT INTO enquiries(parent_name,child_name,phone,email,class_name,branch,message,created_at)
                VALUES(:parent_name,:child_name,:phone,:email,:class_name,:branch,:message,:created_at)""",
                {**fields, "created_at": now()})
        flash("Thank you! Your admission enquiry has been saved. The school team can follow up.", "success")
        return redirect(url_for("admissions"))
    return render_template("admissions.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        fields = {key: request.form.get(key, "").strip() for key in
                  ["name", "phone", "email", "subject", "message"]}
        if not fields["name"] or not fields["message"]:
            flash("Please enter your name and message.", "error")
            return redirect(url_for("contact"))
        with db() as con:
            con.execute("""INSERT INTO messages(name,phone,email,subject,message,created_at)
                VALUES(:name,:phone,:email,:subject,:message,:created_at)""",
                {**fields, "created_at": now()})
        flash("Your message has been saved. Thank you for contacting Morning Star!", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.clear()
            session["admin"] = True
            session["admin_username"] = username
            return redirect(url_for("admin_dashboard"))
        flash("Incorrect username or password.", "error")
    return render_template("admin_login.html")

@app.route("/admin")
@admin_only
def admin_dashboard():
    with db() as con:
        enquiries = con.execute("SELECT * FROM enquiries ORDER BY id DESC").fetchall()
        messages = con.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
        announcements = con.execute("SELECT * FROM announcements ORDER BY id DESC").fetchall()
    return render_template("admin.html", enquiries=enquiries, messages=messages, announcements=announcements)

@app.post("/admin/announcement")
@admin_only
def add_announcement():
    title, body = request.form.get("title", "").strip(), request.form.get("body", "").strip()
    if title and body:
        with db() as con:
            con.execute("INSERT INTO announcements(title,body,created_at) VALUES(?,?,?)", (title, body, now()))
        flash("Announcement published on the home page.", "success")
    else:
        flash("Please add both a title and message.", "error")
    return redirect(url_for("admin_dashboard") + "#announcements")

@app.post("/admin/delete/<kind>/<int:item_id>")
@admin_only
def delete_item(kind, item_id):
    tables = {"enquiry": "enquiries", "message": "messages", "announcement": "announcements"}
    if kind not in tables:
        return ("Not found", 404)
    with db() as con:
        con.execute(f"DELETE FROM {tables[kind]} WHERE id = ?", (item_id,))
    flash("Item deleted.", "success")
    return redirect(url_for("admin_dashboard") + "#" + {"enquiry":"enquiries","message":"messages","announcement":"announcements"}[kind])

@app.post("/admin/logout")
@admin_only
def admin_logout():
    session.clear()
    return redirect(url_for("home"))

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
