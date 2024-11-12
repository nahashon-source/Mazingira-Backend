import unittest
from app import create_app, db
from utilis.models import User, Organization, Story, Beneficiary
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class OrganizationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create admin user
        self.admin = User(email='admin@example.com', is_admin=True)
        self.admin.set_password('password')
        db.session.add(self.admin)
        db.session.commit()
        
        # Get admin token
        response = self.client.post('/api/auth/login', json={
            'email': 'admin@example.com',
            'password': 'password'
        })
        self.admin_token = response.json['access_token']
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_create_organization(self):
        response = self.client.post(
            '/api/organizations/apply',
            json={
                'name': 'Test Organization',
                'description': 'Testing org creation'
            },
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Organization.query.count(), 1)
        
    def test_approve_organization(self):
        # Create organization
        org = Organization(name='Test Org', status='pending')
        db.session.add(org)
        db.session.commit()
        
        response = self.client.post(
            f'/api/admin/organizations/{org.id}/approve',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(org.status, 'approved')
        
    def test_create_story(self):
        org = Organization(name='Test Org', status='approved')
        db.session.add(org)
        db.session.commit()
        
        response = self.client.post(
            '/api/organizations/stories',
            json={
                'title': 'Test Story',
                'content': 'Story content',
                'organization_id': org.id
            },
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Story.query.count(), 1)
        
    def test_create_beneficiary(self):
        org = Organization(name='Test Org', status='approved')
        db.session.add(org)
        db.session.commit()
        
        response = self.client.post(
            '/api/organizations/beneficiaries',
            json={
                'name': 'Test Beneficiary',
                'description': 'Beneficiary description',
                'organization_id': org.id
            },
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Beneficiary.query.count(), 1)