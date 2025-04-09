from flask import Blueprint, request, jsonify
from models import User
from extensions import db
import jwt
import datetime
import os

auth_bp = Blueprint('auth', __name__)
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-dev-key')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    # print("User:", user.username if user else "None")
    # print("Password:", password)
    # print(user.check_password(password) if user else "None")
    if user and user.check_password(password):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({'token': token})

    return jsonify({'error': 'Invalid credentials'}), 401
