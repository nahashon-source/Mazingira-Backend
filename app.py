
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_migrate import Migrate
from models import db, User, Organization, Donation, Story, Beneficiary, Inventory
import stripe
from config import Config

# App initialization
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app)
db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)
stripe.api_key = Config.STRIPE_SECRET_KEY

# Auth Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        user = User(
            email=data['email'],
            name=data['name'],
            role=data['role']
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200

# Organization Routes
@app.route('/api/organizations', methods=['GET'])
def get_organizations():
    organizations = Organization.query.filter_by(status='approved').all()
    return jsonify([{
        'id': org.id,
        'name': org.name,
        'description': org.description
    } for org in organizations]), 200

@app.route('/api/organizations/apply', methods=['POST'])
@jwt_required()
def apply_organization():
    data = request.get_json()
    user_id = get_jwt_identity()
    org = Organization(
        user_id=user_id,
        name=data['name'],
        description=data['description']
    )
    db.session.add(org)
    db.session.commit()
    return jsonify({'message': 'Application submitted successfully'}), 201

# Donation Routes
@app.route('/api/donations', methods=['POST'])
@jwt_required()
def create_donation():
    data = request.get_json()
    user_id = get_jwt_identity()
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(data['amount'] * 100),
            currency='usd'
        )
        donation = Donation(
            user_id=user_id,
            organization_id=data['organization_id'],
            amount=data['amount'],
            is_anonymous=data.get('is_anonymous', False),
            is_recurring=data.get('is_recurring', False),
            frequency=data.get('frequency'),
            status='pending'
        )
        db.session.add(donation)
        db.session.commit()
        return jsonify({
            'client_secret': payment_intent.client_secret,
            'donation_id': donation.id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Story Routes
@app.route('/api/stories', methods=['POST'])
@jwt_required()
def create_story():
    data = request.get_json()
    user_id = get_jwt_identity()
    org = Organization.query.filter_by(user_id=user_id).first()
    if not org:
        return jsonify({'error': 'Unauthorized'}), 403
    story = Story(
        organization_id=org.id,
        title=data['title'],
        content=data['content'],
        image_url=data.get('image_url')
    )
    db.session.add(story)
    db.session.commit()
    return jsonify({'message': 'Story created successfully'}), 201

# Admin Routes
@app.route('/api/admin/organizations/<int:org_id>', methods=['PUT'])
@jwt_required()
def update_organization_status(org_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    org.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Organization status updated'}), 200

# Beneficiary Routes
@app.route('/api/beneficiaries', methods=['POST'])
@jwt_required()
def create_beneficiary():
    data = request.get_json()
    user_id = get_jwt_identity()
    org = Organization.query.filter_by(user_id=user_id).first()
    if not org:
        return jsonify({'error': 'Unauthorized'}), 403
    beneficiary = Beneficiary(
        organization_id=org.id,
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(beneficiary)
    db.session.commit()
    return jsonify({'message': 'Beneficiary created successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)