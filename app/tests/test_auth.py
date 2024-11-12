import unittest
from app import create_app, db
from utilis.models import User
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class AuthTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_user_registration(self):
        response = self.client.post('/api/auth/register', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.query.count(), 1)
        
    def test_user_login(self):
        # Create test user
        user = User(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        response = self.client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)
        
    def test_invalid_login(self):
        response = self.client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 401)
        
    def test_get_current_user(self):
        # Create and login user
        user = User(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        login_response = self.client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        token = login_response.json['access_token']
        
        response = self.client.get('/api/auth/me', headers={
            'Authorization': f'Bearer {token}'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'], 'test@example.com')
        
    def test_update_user(self):
        # Create and login user
        user = User(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        login_response = self.client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        token = login_response.json['access_token']
        
        response = self.client.put('/api/auth/me', 
            headers={'Authorization': f'Bearer {token}'},
            json={'email': 'updated@example.com'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'], 'updated@example.com')