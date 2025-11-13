from flask import Flask, request, render_template, g
import sqlite3
import os
from markupsafe import escape
from dotenv import load_dotenv

# Load .env variables (API_KEY will be stored securely)
load_dotenv()

app = Flask(__name__)

# ✅ FIX 1: Read API_KEY from environment instead of hardcoding
API_KEY = os.getenv("API_KEY")

DATABASE = './app.db'

def get_db():
    """Get or create a database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close DB connection on app teardown."""
    db = getattr(g, '_database', None)
    if db:
        db.close()

@app.route('/')
def index():
    return "Welcome to SecureApp ✅ — all vulnerabilities fixed!"

# ✅ FIX 2: Parameterized queries to prevent SQL Injection
@app.route('/search')
def search():
    q = request.args.get('q', '').strip()
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT id, name, comment FROM items WHERE name LIKE ?"
    cursor.execute(query, (f"%{q}%",))
    results = cursor.fetchall()
    return render_template('search.html', query=escape(q), results=results)

# ✅ FIX 3: Secure endpoint (no secret exposure)
@app.route('/apikey')
def apikey():
    if not API_KEY:
        return "API key not configured.", 403
    return "API key is securely stored in environment."

# ✅ FIX 4: Use template rendering (auto-escaped) instead of inline HTML
@app.route('/greet')
def greet():
    name = request.args.get('name', 'guest')
    safe_name = escape(name)
    return render_template('greet.html', name=safe_name)

if __name__ == "__main__":
    print("🚀 Starting DevSecOps vulnerable app python...")
    # Initialize DB if doesn't exist
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, comment TEXT)")
        c.executemany("INSERT INTO items (name, comment) VALUES (?,?)", [
            ('apple', 'fresh fruit'),
            ('banana', 'yellow'),
            ('choco', 'tasty snack')
        ])
        conn.commit()
        conn.close()
    app.run(host='0.0.0.0', port=5000)
