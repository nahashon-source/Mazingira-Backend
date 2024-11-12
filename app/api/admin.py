from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utilis.models import Organization, User
from utilis.schemas import OrganizationSchema
from app import db

bp = Blueprint('admin', __name__)
org_schema = OrganizationSchema()

def is_admin():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return user.is_admin

@bp.route('/organizations/<int:id>/approve', methods=['POST'])
@jwt_required()
def approve_organization(id):
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
        
    organization = Organization.query.get_or_404(id)
    organization.status = 'approved'
    db.session.commit()
    
    return jsonify(org_schema.dump(organization)), 200

@bp.route('/organizations/<int:id>/reject', methods=['POST'])
@jwt_required()
def reject_organization(id):
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
        
    organization = Organization.query.get_or_404(id)
    organization.status = 'rejected'
    db.session.commit()
    
    return jsonify(org_schema.dump(organization)), 200

@bp.route('/organizations/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_organization(id):
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
        
    organization = Organization.query.get_or_404(id)
    db.session.delete(organization)
    db.session.commit()
    
    return '', 204