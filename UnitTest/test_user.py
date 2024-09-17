import unittest
from teamwork import app

class TestUserEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = app
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_empty_email_or_password_for_login(self):
        """Test empty email or password"""
        response = self.client.post("/user/login", data={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('Please enter both email and password', data['message'])

    def test_wrong_email_password(self):
        """Test with incorrect email and password"""
        response = self.client.post("/user/login", data={"email": "123@uic.edu.cn", "password": "wrongpass"})
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn('Incorrect password', data['message'])

    def test_correct_email_password(self):
        """Test with correct email and password"""
        response = self.client.post("/user/login", data={"email": "123@uic.edu.cn", "password": "123"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('Login successful! Welcome, teacher.', data['message'])

    def test_empty_email_or_password_for_register(self):
        """Test empty email or password"""
        response = self.client.post("/user/register", data={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('Please enter both email and password', data['message'])

    def test_existing_user(self):
        """Test register with an existing user email"""
        response = self.client.post("/user/register", data={"email": "123@uic.edu.cn", "password": "existing"})
        self.assertEqual(response.status_code, 409)
        data = response.get_json()
        self.assertIn('Email already registered', data['message'])

    def test_correct_email_password_for_register(self):
        """Test with correct email and password"""
        response = self.client.post("/user/register", data={"email": "789@uic.edu.cn", "password": "123"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('Registration successful! Welcome, teacher.', data['message'])

if __name__ == '__main__':
    unittest.main()
