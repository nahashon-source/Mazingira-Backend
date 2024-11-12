import unittest
from app import create_app, db
from utilis.models import User, Organization, Donation
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class DonationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user and organization
        self.user = User(email='test@example.com')
        self.user.set_password('password')
        self.org = Organization(name='Test Org', status='approved')
        db.session.add_all([self.user, self.org])
        db.session.commit()
        
        # Get auth token
        response = self.client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password'
        })
        self.token = response.json['access_token']
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_create_one_time_donation(self):
        response = self.client.post(
            '/api/donations/',
            json={
                'amount': 100.00,
                'currency': 'USD',
                'organization_id': self.org.id,
                'is_recurring': False
            },
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Donation.query.count(), 1)
        
    def test_create_recurring_donation(self):
        response = self.client.post(
            '/api/donations/',
            json={
                'amount': 50.00,
                'currency': 'USD',
                'organization_id': self.org.id,
                'is_recurring': True,
                'recurring_interval': 'monthly'
            },
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        self.assertEqual(response.status_code, 201)
        donation = Donation.query.first()
        self.assertTrue(donation.is_recurring)
        self.assertEqual(donation.recurring_interval, 'monthly')
        
    def test_anonymous_donation(self):
        response = self.client.post(
            '/api/donations/',
            json={
                'amount': 75.00,
                'currency': 'USD',
                'organization_id': self.org.id,
                'is_anonymous': True
            },
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        self.assertEqual(response.status_code, 201)
        donation = Donation.query.first()
        self.assertTrue(donation.is_anonymous)