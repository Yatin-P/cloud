import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import os

project_root = os.path.dirname(__file__)
template_path = os.path.join(project_root, './templates')

DATABASE = '/var/www/html/flaskapp/users.db'

app = Flask(__name__, template_folder=template_path)
app.config.from_object(__name__)

# Initialize Database
def init_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()
# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()

        # Check if email exists
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            conn.close()
            return "Email already registered. Try logging in."

        # Insert new user
        cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (username, email, password))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and password:  
            return redirect(url_for('profile', user_id=user[0]))  
        else:
            return "Invalid credentials. Try again."

    return render_template('login.html')

# Profile Route
@app.route('/profile/<user_id>')
def profile(user_id):
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()

    cursor.execute("SELECT username, email FROM users WHERE rowid = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return render_template('profile.html', user={'username': user[0], 'email': user[1]})
    else:
        return "User not found."

# Logout Route
@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/')
def home():
    return redirect(url_for('register'))
if __name__ == '__main__':
    app.run(debug=True)
