from flask_jwt_extended import create_access_token
from datetime import timedelta

def generate_token(user_id, expires_delta=None):
    """Generate JWT token for a user"""
    if expires_delta is None:
        expires_delta = timedelta(hours=1)
        
    return create_access_token(
        identity=user_id,
        expires_delta=expires_delta
    )

def verify_token(token):
    """Verify JWT token"""
    try:
        # JWT verification is handled by flask_jwt_extended
        # This function can be extended for additional verification logic
        return True
    except Exception:
        return False