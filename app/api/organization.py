from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utilis.models import Organization, Story, Beneficiary
from utilis.schemas import OrganizationSchema, StorySchema, BeneficiarySchema
from app import db
from services.auth import admin_required

bp = Blueprint('organizations', __name__)
org_schema = OrganizationSchema()
story_schema = StorySchema()
beneficiary_schema = BeneficiarySchema()

@bp.route('/apply', methods=['POST'])
@jwt_required()
def apply_organization():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        org_data = org_schema.load(data)
        organization = Organization(
            name=org_data['name'],
            description=org_data['description'],
            user_id=current_user_id,
            status='pending'
        )
        
        db.session.add(organization)
        db.session.commit()
        
        return jsonify(org_schema.dump(organization)), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/stories', methods=['POST'])
@jwt_required()
def create_story():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Verify user belongs to organization
        organization = Organization.query.filter_by(user_id=current_user_id).first()
        if not organization:
            return jsonify({'error': 'Unauthorized'}), 403
            
        story_data = story_schema.load(data)
        story = Story(
            title=story_data['title'],
            content=story_data['content'],
            image_url=story_data.get('image_url'),
            organization_id=organization.id
        )
        
        db.session.add(story)
        db.session.commit()
        
        return jsonify(story_schema.dump(story)), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/beneficiaries', methods=['POST'])
@jwt_required()
def create_beneficiary():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Verify user belongs to organization
        organization = Organization.query.filter_by(user_id=current_user_id).first()
        if not organization:
            return jsonify({'error': 'Unauthorized'}), 403
            
        beneficiary_data = beneficiary_schema.load(data)
        beneficiary = Beneficiary(
            name=beneficiary_data['name'],
            description=beneficiary_data['description'],
            organization_id=organization.id
        )
        
        db.session.add(beneficiary)
        db.session.commit()
        
        return jsonify(beneficiary_schema.dump(beneficiary)), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:id>/approve', methods=['POST'])
@jwt_required()
@admin_required()
def approve_organization(id):
    try:
        organization = Organization.query.get_or_404(id)
        organization.status = 'approved'
        db.session.commit()
        
        return jsonify(org_schema.dump(organization)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:id>/reject', methods=['POST'])
@jwt_required()
@admin_required()
def reject_organization(id):
    try:
        organization = Organization.query.get_or_404(id)
        organization.status = 'rejected'
        db.session.commit()
        
        return jsonify(org_schema.dump(organization)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400