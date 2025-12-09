import os
import sqlite3
import re
from flask import Flask, render_template, request, jsonify, Response
from datetime import datetime

app = Flask(__name__)

# Configuration from environment variables
CLUSTER_DOMAIN = os.getenv('CLUSTER_DOMAIN', 'example.com')
USER_PASSWORD = os.getenv('USER_PASSWORD', 'thisisthepassword')
MAX_USERS = int(os.getenv('MAX_USERS', '25'))
LAB_INSTRUCTIONS_URL = os.getenv('LAB_INSTRUCTIONS_URL', 'https://rhoai-genaiops.github.io/lab-instructions/')
DB_PATH = os.getenv('DB_PATH', '/data/users.db')
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', 'admin-secret-token-change-me')

def init_db():
    """Initialize the database with users table"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def validate_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_next_available_user():
    """Find the next available user from user1 to user{MAX_USERS}"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all assigned usernames
    cursor.execute('SELECT username FROM user_assignments')
    assigned_users = set(row['username'] for row in cursor.fetchall())
    conn.close()

    # Find first available user
    for i in range(1, MAX_USERS + 1):
        username = f'user{i}'
        if username not in assigned_users:
            return username

    return None

def assign_user(email):
    """Assign a user to an email address"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if email already has an assignment
        cursor.execute('SELECT username FROM user_assignments WHERE email = ?', (email,))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            return existing['username']

        # Get next available user
        username = get_next_available_user()

        if username is None:
            conn.close()
            return None

        # Assign the user
        cursor.execute(
            'INSERT INTO user_assignments (email, username) VALUES (?, ?)',
            (email, username)
        )
        conn.commit()
        conn.close()

        return username

    except sqlite3.IntegrityError:
        conn.close()
        return None

@app.route('/')
def index():
    """Render the main page"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM user_assignments')
    assigned_count = cursor.fetchone()['count']
    conn.close()

    return render_template('index.html',
                         assigned_count=assigned_count,
                         max_users=MAX_USERS)

@app.route('/signup', methods=['POST'])
def signup():
    """Handle user signup"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({'error': 'Email address is required'}), 400

    if not validate_email(email):
        return jsonify({'error': 'Invalid email address format'}), 400

    username = assign_user(email)

    if username is None:
        return jsonify({'error': 'All users have been assigned. No more slots available.'}), 400

    # Prepare response with user credentials and instructions
    response = {
        'username': username,
        'password': USER_PASSWORD,
        'cluster_domain': CLUSTER_DOMAIN,
        'lab_url': LAB_INSTRUCTIONS_URL,
        'instructions': f'Access the lab instructions at {LAB_INSTRUCTIONS_URL} and use your credentials to log into the cluster.'
    }

    return jsonify(response), 200

@app.route('/stats')
def stats():
    """Get current assignment statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM user_assignments')
    assigned_count = cursor.fetchone()['count']
    conn.close()

    return jsonify({
        'assigned': assigned_count,
        'available': MAX_USERS - assigned_count,
        'total': MAX_USERS
    })

@app.route('/admin/users')
def admin_users():
    """Admin endpoint to list all registered users (requires authentication)"""
    # Check for admin token in header
    auth_header = request.headers.get('Authorization')
    token = request.args.get('token')

    # Accept token from either Authorization header or query parameter
    provided_token = None
    if auth_header and auth_header.startswith('Bearer '):
        provided_token = auth_header[7:]
    elif token:
        provided_token = token

    if provided_token != ADMIN_TOKEN:
        return jsonify({'error': 'Unauthorized. Valid admin token required.'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, email, username, assigned_at
        FROM user_assignments
        ORDER BY assigned_at DESC
    ''')
    users = cursor.fetchall()
    conn.close()

    # Convert to list of dicts
    users_list = []
    for user in users:
        users_list.append({
            'id': user['id'],
            'email': user['email'],
            'username': user['username'],
            'assigned_at': user['assigned_at'],
            'password': USER_PASSWORD,
            'cluster_domain': CLUSTER_DOMAIN
        })

    return jsonify({
        'total': len(users_list),
        'users': users_list,
        'config': {
            'max_users': MAX_USERS,
            'cluster_domain': CLUSTER_DOMAIN,
            'password': USER_PASSWORD,
            'lab_url': LAB_INSTRUCTIONS_URL
        }
    })

@app.route('/admin/export')
def admin_export():
    """Admin endpoint to export users as CSV (requires authentication)"""
    # Check for admin token
    auth_header = request.headers.get('Authorization')
    token = request.args.get('token')

    provided_token = None
    if auth_header and auth_header.startswith('Bearer '):
        provided_token = auth_header[7:]
    elif token:
        provided_token = token

    if provided_token != ADMIN_TOKEN:
        return jsonify({'error': 'Unauthorized. Valid admin token required.'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT email, username, assigned_at
        FROM user_assignments
        ORDER BY username
    ''')
    users = cursor.fetchall()
    conn.close()

    # Generate CSV
    csv_lines = ['Email,Username,Password,Cluster Domain,Assigned At']
    for user in users:
        csv_lines.append(f"{user['email']},{user['username']},{USER_PASSWORD},{CLUSTER_DOMAIN},{user['assigned_at']}")

    csv_content = '\n'.join(csv_lines)

    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=lab-users.csv'}
    )

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=os.getenv('FLASK_DEBUG', 'False') == 'True')
