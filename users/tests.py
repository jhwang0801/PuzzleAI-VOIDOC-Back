from http import client
import json

from django.test import TestCase, Client, TransactionTestCase

from users.models import CustomUser

class SignUpTest(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(
            name      = 'kevin',
            email     = 'kevin@gmail.com',
            password  = 'asdf12345',
            is_doctor = 'False'            
        )

    def tearDown(self):
        CustomUser.objects.all().delete()

    def test_success_sign_up_view(self): 
        client = Client()
        user   = {
            'name'     : 'john',
            'email'    : 'john@gmail.com',
            'password' : '12345qwert',
            'is_doctor': 'False'
        }
        response = client.post('/users/signup', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            'message': 'SUCCESS'
        })

    def test_fail_sign_up_view_with_key_error(self): 
        client = Client()
        user   = {
            'name'    : 'john',
            'email'   : 'john@gmail.com',
            'password': '12345qwert'
        }
        response = client.post('/users/signup', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'message': 'KEY_ERROR'
        })

    def test_fail_sign_up_view_with_email_validation_error(self): 
        client = Client()
        user   = {
            'name'     : 'john',
            'email'    : 'johngmailcom',
            'password' : '12345qwert',
            'is_doctor': 'False'
        }
        response = client.post('/users/signup', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'message': "Enter a valid email address."
        })

    def test_fail_sign_up_view_with_password_validation_error(self): 
        client = Client()
        user   = {
            'name'     : 'john',
            'email'    : 'john@gmail.com',
            'password' : '!@#12345qwert',
            'is_doctor': 'False'
        }
        response = client.post('/users/signup', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'message': "Enter a valid password."
        })

    def test_fail_sign_up_view_with_no_name_value_error(self): 
        client = Client()
        user   = {
            'name'     : '',
            'email'    : 'john@gmail.com',
            'password' : '12345qwert',
            'is_doctor': 'False'
        }
        response = client.post('/users/signup', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'message': "Users must have the name"
        })

class SignUpIntegrityTest(TransactionTestCase):
    def setUp(self):
        CustomUser.objects.create_user(
            name      = 'kevin',
            email     = 'kevin@gmail.com',
            password  = 'asdf12345',
            is_doctor = 'False'            
        )

    def tearDown(self):
        CustomUser.objects.all().delete()

    def test_fail_sign_up_view_with_existed_email_integrity_error(self):
        client = Client()
        user = {
            'name'     : 'john',
            'email'    : 'kevin@gmail.com',
            'password' : '12345qwert',
            'is_doctor': 'False'
        }
        response = client.post('/users/signup', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'message': "EMAIL_IS_ALREADY_REGISTERED"
        }) 

class LoginTest(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(
            name      = 'kevin',
            email     = 'kevin@gmail.com',
            password  = 'asdf12345',
            is_doctor = 'False'            
        )

    def tearDown(self):
        CustomUser.objects.all().delete()

    def test_successful_login(self):
        client = Client()
        user   = {
            'name'     : 'kevin',
            'email'    : 'kevin@gmail.com',
            'password' : 'asdf12345',
            'is_doctor': 'False'
        }
        response = client.post('/users/login', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            'message': 'SUCCESS'
        })

    def test_unsuccessful_login(self):
        client = Client()
        user   = {
            'name'     : 'james',
            'email'    : 'james@gmail.com',
            'password' : 'uiop67890',
            'is_doctor': 'False'
        }
        response = client.post('/users/login', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'message': 'Username or password is incorrect!'
        })

    def test_wrong_username_login(self):
        client = Client()
        user   = {
            'name'     : 'james',
            'email'    : 'james@gmail.com',
            'password' : 'asdf12345',
            'is_doctor': 'False'
        }
        response = client.post('/users/login', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'message': 'Username or password is incorrect!'
        })
    
    def test_wrong_password_login(self):
        client = Client()
        user   = {
            'name'     : 'kevin',
            'email'    : 'kevin@gmail.com',
            'password' : 'uiop67890',
            'is_doctor': 'False'
        }
        response = client.post('/users/login', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'message': 'Username or password is incorrect!'
        })
