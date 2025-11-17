# routes/auth.py
from flask import Blueprint, request, jsonify, session
from extensions import db
from models import User
from services.state_manager import clear_cache_for_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/status', methods=['GET'])
def auth_status():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return jsonify({'isLoggedIn': True, 'email': user.email if user else ''})
    return jsonify({'isLoggedIn': False})

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password required'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'Email already registered'}), 409

    new_user = User(email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Account created! Please login.'})

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        
    session['user_id'] = user.id
    session['user_email'] = user.email
    return jsonify({'success': True, 'email': user.email})

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    clear_cache_for_user() # Though now stateless, good to clear just in case
    return jsonify({'success': True})