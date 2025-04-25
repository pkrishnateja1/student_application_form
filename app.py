from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import csv

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database Initialization
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        email TEXT,
                        phone TEXT,
                        course TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS admin (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        password TEXT)''')
    
    cursor.execute("INSERT OR IGNORE INTO admin (id, username, password) VALUES (1, 'admin', 'password')")
    conn.commit()
    conn.close()

# Home Route - Application Form
@app.route('/')
def index():
    return render_template('form.html')

# Form Submission Route
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    course = request.form['course']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, email, phone, course) VALUES (?, ?, ?, ?)", (name, email, phone, course))
    conn.commit()
    conn.close()
    flash('Application Submitted Successfully!', 'success')
    return redirect(url_for('index'))

# Admin Login Route
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
        admin = cursor.fetchone()
        conn.close()
        if admin:
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials', 'danger')
    return render_template('admin_login.html')

# Admin Dashboard
@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', students=students)

# Export Data to CSV
@app.route('/export')
def export():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()
    with open('students.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Course'])
        writer.writerows(students)
    flash('Data Exported to CSV Successfully!', 'success')
    return redirect(url_for('dashboard'))

# Clear Database
@app.route('/clear')
def clear():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students")
    conn.commit()
    conn.close()
    flash('Database Cleared Successfully!', 'warning')
    return redirect(url_for('dashboard'))

# Logout - Exit Button
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
