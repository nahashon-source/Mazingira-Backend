from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utilis.models import Donation, User
from utilis.schemas import DonationSchema
from app import db
from app.services.payment import process_payment, setup_recurring_payment
from utils.reminders import schedule_donation_reminder

bp = Blueprint('donations', __name__)
donation_schema = DonationSchema()

@bp.route('/', methods=['POST'])
@jwt_required()
def create_donation():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Process payment based on payment method
        payment_method = data.get('paymentMethod')
        payment_result = None
        
        if payment_method in ['creditCard', 'debitCard']:
            payment_result = process_payment(
                amount=data['amount'],
                currency='KES',
                payment_method_id=data.get('cardNumber'),
                payment_type='card'
            )
        elif payment_method == 'mpesa':
            payment_result = process_payment(
                amount=data['amount'],
                currency='KES',
                phone_number=data.get('phoneNumber'),
                payment_type='mpesa'
            )
        elif payment_method == 'paypal':
            payment_result = process_payment(
                amount=data['amount'],
                currency='KES',
                paypal_email=data.get('paypalEmail'),
                payment_type='paypal'
            )
            
        if payment_result and payment_result['status'] == 'succeeded':
            donation = Donation(
                amount=data['amount'],
                currency='KES',
                is_anonymous=data.get('isAnonymous', False),
                is_recurring=data.get('frequency') != 'one-time',
                recurring_interval=data.get('frequency'),
                user_id=current_user_id,
                organization_id=data['organizationId'],
                payment_method=payment_method
            )
            
            if donation.is_recurring:
                setup_recurring_payment(donation)
                schedule_donation_reminder(donation)
            
            db.session.add(donation)
            db.session.commit()
            
            return jsonify(donation_schema.dump(donation)), 201
            
        return jsonify({'error': 'Payment failed'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/history', methods=['GET'])
@jwt_required()
def get_donation_history():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if user.role == 'organization':
        donations = Donation.query.filter_by(organization_id=user.organization_id).all()
    else:
        donations = Donation.query.filter_by(user_id=current_user_id).all()
    
    return jsonify(donation_schema.dump(donations, many=True)), 200