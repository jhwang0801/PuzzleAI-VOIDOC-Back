from http import client
import json

from django.test import TestCase, Client, TransactionTestCase

from users.models import CustomUser
from users.utils import generate_jwt

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
    def setUp():
        CustomUser.objects.create_user(
            name      = 'kevin',
            email     = 'kevin@gmail.com',
            password  = 'asdf12345',
            is_doctor = 'False'            
        )
        CustomUser.objects.create_user(
            name      = 'doctor',
            email     = 'doctor@gmail.com',
            password  = 'doctor123',
            is_doctor = 'True'
        )

    def tearDown(self):
        CustomUser.objects.all().delete()

    def test_success_app_patient_login(self):
        client = Client()
        user   = {
            'email'    : 'kevin@gmail.com',
            'password' : 'asdf12345',
        }

        headers  = {"HTTP_TYPE_OF_APPLICATION" : "app"}
        response = client.post('/users/login', json.dumps(user), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'message'     : 'SUCCESS_PATIENT_LOGIN',
            'access_token': generate_jwt(CustomUser.objects.get(id=1))
        })

    def test_fail_app_doctor_login(self):
        client = Client()
        user   = {
            'email'    : 'doctor@gmail.com',
            'password' : 'doctor123',
        }

        headers  = {"HTTP_TYPE_OF_APPLICATION" : "app"}
        response = client.post('/users/login', json.dumps(user), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
            'message'     : 'DOCTOR_CAN_NOT_LOGIN_ON_APP',
        })

    def test_success_web_patient_login(self):
        client = Client()
        user   = {
            'email'    : 'kevin@gmail.com',
            'password' : 'asdf12345',
        }

        headers  = {"HTTP_TYPE_OF_APPLICATION" : "web"}
        response = client.post('/users/login', json.dumps(user), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'message'     : 'SUCCESS_LOGIN',
            'access_token': generate_jwt(CustomUser.objects.get(id=1))
        })
    
    def test_success_web_doctor_login(self):
        client = Client()
        user   = {
            'email'    : 'doctor@gmail.com',
            'password' : 'doctor123',
        }

        headers  = {"HTTP_TYPE_OF_APPLICATION" : "web"}
        response = client.post('/users/login', json.dumps(user), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'message'     : 'SUCCESS_LOGIN',
            'access_token': generate_jwt(CustomUser.objects.get(id=2))
        })

    def test_fail_login_with_invalid_email(self):
        client = Client()
        user   = {
            'email'    : 'kevi@gmail.com',
            'password' : 'asdf12345',
        }

        headers  = {"HTTP_TYPE_OF_APPLICATION" : "app"}
        response = client.post('/users/login', json.dumps(user), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
            'message'     : 'WRONG_EMAIL_OR_PASSWORD',
        })

    def test_fail_login_with_invalid_password(self):
        client = Client()
        user   = {
            'email'    : 'kevin@gmail.com',
            'password' : 'asdf',
        }

        headers  = {"HTTP_TYPE_OF_APPLICATION" : "app"}
        response = client.post('/users/login', json.dumps(user), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
            'message'     : 'WRONG_EMAIL_OR_PASSWORD',
        })

    def test_fail_login_invalid_type_of_application_on_header(self):
        client = Client()
        user   = {
            'email'    : 'kevin@gmail.com',
            'password' : 'asdf12345',
        }

        headers  = {"HTTP_TYPE_OF_APPLICATION" : "nomoretest"}
        response = client.post('/users/login', json.dumps(user), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'message'     : 'INVALID_TYPE_OF_APPLICATION_ON_HEADER',
        })
