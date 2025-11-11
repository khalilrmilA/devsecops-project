from flask import Flask, request, render_template, g
import sqlite3
import os

app = Flask(__name__)

# HARD-CODED SECRET (intentional vulnerable)
API_KEY = "SECRET_API_KEY_12345"

DATABASE = './app.db'

def get_db():
    db = getattr(g, '_database', None)
    print("✅ Testing Jenkins CI trigger2")
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db:
        db.close()

# Home page
@app.route('/')
def index():
    return "Welcome to VulnerableApp - test SQLi, XSS, and secrets"

# 1) Vulnerable search endpoint (SQL INJECTION)
@app.route('/search')
def search():
    q = request.args.get('q', '')
    # BAD: building SQL by string concatenation -> SQLi
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT id, name, comment FROM items WHERE name LIKE '%{}%'".format(q)
    cursor.execute(query)
    results = cursor.fetchall()
    # Render results; template will reflect user input (see XSS)
    return render_template('search.html', query=q, results=results)

# 2) Endpoint that reveals the hard-coded secret (for testing)
@app.route('/apikey')
def apikey():
    # BAD: exposing secret
    return f"API_KEY = {API_KEY}"

# 3) Endpoint returning user-supplied string (reflected XSS)
@app.route('/greet')
def greet():
    name = request.args.get('name', 'guest')
    # BAD: no escaping in template usage (search.html will show this raw)
    return f"Hello, {name}!"

if __name__ == "__main__":
    # Initialize DB if doesn't exist
    if not os.path.exists(DATABASE):
        import sqlite3
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
