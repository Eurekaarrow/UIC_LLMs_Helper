import unittest
from app.controller.user import app
import json


class TestLogin(unittest.TestCase):
    """ Define Test Case"""

    def setUp(self):
        """It is called before the specific test method is executed."""

        self.app = app
        # Activation test flag
        app.config['TESTING'] = True
        # Here, the test is performed using the test client provided by flask
        self.client = app.test_client()

    def test_empty_name_or_password(self):
        """Test empty name or password"""
        response = self.client.post("/login", data={})
        # response data
        resp_json = response.data
        # convert to json
        resp_dict = json.loads(resp_json)
        # assert if the code in the dict
        self.assertIn("code", resp_dict)
        # compare the code value 1001
        code = resp_dict.get("code")
        self.assertEqual(code, 1001)
        # Test only recieve name
        response = self.client.post("/login", data={"name": "admin"})
        # response data
        resp_json = response.data
        # convert to json
        resp_dict = json.loads(resp_json)
        # use assert to verify
        self.assertIn("code", resp_dict)
        # compare the code value 1001
        code = resp_dict.get("code")
        self.assertEqual(code, 1001)
        # return message
        msg = resp_dict.get('message')
        self.assertEqual(msg, "Parameter incomplete!")

    def test_wrong_name_password(self):
        response = self.client.post("/login", data={"name": "admin", "password": "123456"})
        # respoonse data
        resp_json = response.data
        # convert to json
        resp_dict = json.loads(resp_json)
        # use assert to verify
        self.assertIn("code", resp_dict)
        # compare the code value 1001
        code = resp_dict.get("code")
        self.assertEqual(code, 1001)
        # return message
        msg = resp_dict.get('message')
        self.assertEqual(msg, "Not correct username or password!")

    def test_correct_name_password(self):
        response = self.client.post("/login", data={"name": "admin", "password": "123321"})
        # response data
        resp_json = response.data
        # convert to json
        resp_dict = json.loads(resp_json)
        # use assert to verify
        self.assertIn("code", resp_dict)
        # compare the code value 0
        code = resp_dict.get("code")
        self.assertEqual(code, 0)
        # return message
        msg = resp_dict.get('message')
        self.assertEqual(msg, "Success!")

if __name__ == '__main__':
    unittest.main()
