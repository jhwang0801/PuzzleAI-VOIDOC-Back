import json

from django.test import TestCase, Client, TransactionTestCase

from users.models import CustomUser
from users.utils  import Validation

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
            'password' : '!@#12345qwertasdf',
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

class LoginTest(TestCase, Validation):
    def setUpTestData():
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

        user = CustomUser.objects.get(is_doctor=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'message'     : 'SUCCESS_PATIENT_LOGIN',
            'access_token': self.generate_jwt(user),
            'user_id'     : user.id,
            'user_name'   : user.name
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
        user = CustomUser.objects.get(is_doctor=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'message'     : 'SUCCESS_LOGIN',
            'access_token': self.generate_jwt(user),
            'user_id'     : user.id,
            'user_name'   : user.name
        })
    
    def test_success_web_doctor_login(self):
        client = Client()
        user   = {
            'email'    : 'doctor@gmail.com',
            'password' : 'doctor123',
        }

        headers  = {"HTTP_TYPE_OF_APPLICATION" : "web"}
        response = client.post('/users/login', json.dumps(user), content_type='application/json', **headers)
        doctor = CustomUser.objects.get(is_doctor=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'message'     : 'SUCCESS_LOGIN',
            'access_token': self.generate_jwt(doctor),
            'user_id'          : doctor.id,
            'user_name'        : doctor.name
            }
        )

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

class CheckDuplicateTest(TestCase):
    def setUp(self):
        CustomUser.objects.create_user(
            name      = 'kevin',
            email     = 'kevin@gmail.com',
            password  = 'asdf12345',
            is_doctor = 'False'            
        )

    def tearDown(self):
        CustomUser.objects.all().delete()

    def test_success_can_register_with_this_email(self): 
        client = Client()
        data   = {
            'email'    : 'john@gmail.com'
        }
        response = client.post('/users/check_duplicate', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            'message': 'CAN_REGISTER_WITH_THIS_EMAIL'
        })

    def test_fail_sign_up_view_with_key_error(self): 
        client = Client()
        data   = {
            'emails'   : 'john@gmail.com'
        }
        response = client.post('/users/check_duplicate', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'message': 'KEY_ERROR'
        })

class CheckDuplicateEmailIntegrityTest(TransactionTestCase):
    def setUp(self):
        CustomUser.objects.create_user(
            name      = 'kevin',
            email     = 'kevin@gmail.com',
            password  = 'asdf12345',
            is_doctor = 'False'            
        )

    def tearDown(self):
        CustomUser.objects.all().delete()

    def test_fail_check_duplicate_email_integrity_error(self):
        client = Client()
        data = {
            'email'    : 'kevin@gmail.com'
        }
        response = client.post('/users/check_duplicate', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'message': "EMAIL_IS_ALREADY_REGISTERED"
        }) 

class PasswordChangeTest(TestCase, Validation):
    def setUp(self):
        CustomUser.objects.create_user(
            name      = 'john',
            email     = 'john@gmail.com',
            password  = 'john1234',
            is_doctor = 'False'            
        )

    def tearDown(self):
        CustomUser.objects.all().delete()

    def test_success_change_password_success_login(self):
        client = Client()
        old_data = {
            'email' : 'john@gmail.com',
            'password' : 'john1234'
        }
        change_data = {
            'email' : 'john@gmail.com',
            'old_password' : 'john1234',
            'new_password' : 'john7980'
        }
        new_data = {
            'email' : 'john@gmail.com',
            'password' : 'john7980'
        }
        headers  = {"HTTP_TYPE_OF_APPLICATION" : "web"}
        email = old_data['email']
        new_password = change_data['new_password']

        user = CustomUser.objects.get(email=email)

        # Check login works with old user
        response = client.post('/users/login', json.dumps(old_data), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
                'message'     : 'SUCCESS_LOGIN',
                "access_token": self.generate_jwt(user),
                'user_id'     : user.id,
                'user_name'   : user.name
            })
        
        # Check password change
        response = client.post('/users/password_change', json.dumps(change_data), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            'message' : 'PASSWORD_CHANGED_SUCCESSFULLY',
            'email'   : user.email,
            'new_password' : new_password,
            }) 

        # Check login works with updated credentials
        response = client.post('/users/login', json.dumps(new_data), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
                'message'     : 'SUCCESS_LOGIN',
                "access_token": self.generate_jwt(user),
                'user_id'     : user.id,
                'user_name'   : user.name
            })

    def test_success_change_password_fail_login(self):    
        client = Client()
        old_user = {
            'email' : 'john@gmail.com',
            'password' : 'john1234'
        }
        change_data = {
            'email' : 'john@gmail.com',
            'old_password' : 'john1234',
            'new_password' : 'john7980'
        }

        headers  = {"HTTP_TYPE_OF_APPLICATION" : "web"}
        email = old_user['email']
        new_password = change_data['new_password']

        user = CustomUser.objects.get(email=email)

        # Check login works with old user
        response = client.post('/users/login', json.dumps(old_user), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
                'message'     : 'SUCCESS_LOGIN',
                "access_token": self.generate_jwt(user),
                'user_id'     : user.id,
                'user_name'   : user.name
            })
        
        # Check password reset
        response = client.post('/users/password_change', json.dumps(change_data), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            'message' : 'PASSWORD_CHANGED_SUCCESSFULLY',
            'email'   : user.email,
            'new_password' : new_password,
            }) 

        # Check login fails with old user credentials
        response = client.post('/users/login', json.dumps(old_user), content_type='application/json', **headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'message' : 'WRONG_EMAIL_OR_PASSWORD'})

    def test_fail_user_does_not_exist(self):
        client = Client()
        data = {
            'email' : 'brian@gmail.com',
            'old_password' : 'brian1234',
            'new_password' : 'brain8790'
        }
        
        # Check password reset
        response = client.post('/users/password_change', json.dumps(data), content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'message' : 'NO_USER_EXISTS_WITH_THIS_EMAIL'}) 

    def test_fail_user_invalid_password_form(self):
        client = Client()
        data = {
            'email' : 'john@gmail.com',
            'old_password' : 'john1234',
            'new_password' : 'john1'
        }
        
        # Check password reset
        response = client.post('/users/password_change', json.dumps(data), content_type='application/json')

        self.assertEqual(response.json(), {"message": "Enter a valid password."}) 