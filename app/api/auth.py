from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utilis.models import User
from utilis.schemas import UserSchema, LoginSchema
from app import db

bp = Blueprint('auth', __name__)
user_schema = UserSchema()
login_schema = LoginSchema()

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        user_data = user_schema.load(data)
        
        if User.query.filter_by(email=user_data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
            
        user = User(
            email=user_data['email'],
            name=user_data.get('name', ''),
            role=user_data.get('role', 'donor')
        )
        user.set_password(user_data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user_schema.dump(user)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        login_data = login_schema.load(data)
        
        user = User.query.filter_by(email=login_data['email']).first()
        
        if user and user.check_password(login_data['password']):
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'access_token': access_token,
                'user': user_schema.dump(user)
            }), 200
            
        return jsonify({'error': 'Invalid email or password'}), 401
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400