import stripe
from flask import current_app

def process_payment(amount, currency='KES', **kwargs):
    """Process payment using various payment methods"""
    payment_type = kwargs.get('payment_type')
    
    if payment_type == 'card':
        return process_card_payment(amount, currency, kwargs.get('payment_method_id'))
    elif payment_type == 'mpesa':
        return process_mpesa_payment(amount, currency, kwargs.get('phone_number'))
    elif payment_type == 'paypal':
        return process_paypal_payment(amount, currency, kwargs.get('paypal_email'))
    else:
        raise ValueError('Invalid payment type')

def process_card_payment(amount, currency, payment_method_id):
    """Process card payment using Stripe"""
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency=currency,
            payment_method=payment_method_id,
            confirm=True
        )
        
        return {
            'status': payment_intent.status,
            'client_secret': payment_intent.client_secret
        }
    except stripe.error.StripeError as e:
        return {
            'status': 'failed',
            'error': str(e)
        }

def process_mpesa_payment(amount, currency, phone_number):
    """Process M-PESA payment"""
    # Implement M-PESA payment integration
    # This is a placeholder - you'll need to implement actual M-PESA integration
    return {
        'status': 'succeeded',
        'transaction_id': 'mock_mpesa_id'
    }

def process_paypal_payment(amount, currency, paypal_email):
    """Process PayPal payment"""
    # Implement PayPal payment integration
    # This is a placeholder - you'll need to implement actual PayPal integration
    return {
        'status': 'succeeded',
        'transaction_id': 'mock_paypal_id'
    }

def setup_recurring_payment(donation):
    """Set up recurring payment schedule"""
    if donation.payment_method in ['creditCard', 'debitCard']:
        return setup_stripe_subscription(donation)
    elif donation.payment_method == 'mpesa':
        return setup_mpesa_recurring(donation)
    elif donation.payment_method == 'paypal':
        return setup_paypal_subscription(donation)
    
def setup_stripe_subscription(donation):
    """Set up recurring payment using Stripe"""
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    
    try:
        subscription = stripe.Subscription.create(
            customer=donation.user.stripe_customer_id,
            items=[{'price': get_price_id(donation)}],
            payment_behavior='default_incomplete'
        )
        
        return {
            'status': 'success',
            'subscription_id': subscription.id
        }
    except stripe.error.StripeError as e:
        return {
            'status': 'failed',
            'error': str(e)
        }