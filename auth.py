
from flask import Blueprint, request, jsonify, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_CONFIG

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400
        
    hashed_pw = generate_password_hash(password)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (%s, %s)", (email, hashed_pw))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'User created successfully'})
    except mysql.connector.Error as err:
        if err.errno == 1062: # Duplicate entry
            return jsonify({'error': 'Email already exists'}), 409
        return jsonify({'error': str(err)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['email'] = user['email']
            return jsonify({'message': 'Login successful', 'redirect': '/'})
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'})

@auth_bp.route('/verify_email', methods=['POST'])
def verify_email():
    data = request.json
    email = data.get('email')
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            return jsonify({'message': 'Email exists'})
        else:
            return jsonify({'error': 'Email not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    hashed_pw = generate_password_hash(password)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (hashed_pw, email))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Password updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/check_auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({'authenticated': True, 'email': session['email']})
    return jsonify({'authenticated': False}), 401
