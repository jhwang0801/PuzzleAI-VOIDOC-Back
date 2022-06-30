import json
import jwt
import re

from datetime               import datetime, timedelta

from django.views           import View
from django.http            import JsonResponse
from django.db.utils        import IntegrityError
from django.forms           import ValidationError
from django.core.validators import validate_email
from django.contrib.auth    import login, authenticate
from django.conf            import settings

from users.models import CustomUser

class Validation:
    def check_duplicate_email(email):
        if CustomUser.objects.filter(email = email).exists():
            raise IntegrityError

    def generate_jwt(user):
        payload      = {'user_id': user.id, 'exp': datetime.now() +timedelta(hours=2)}
        access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return access_token

class SignUpView(View):
    def validate_password(self, password):
        REGEX_PASSWORD = '^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z]{8,}$'

        if not re.match(REGEX_PASSWORD, password):
            raise ValidationError('Enter a valid password.')

    def post(self, request):
        try:
            data = json.loads(request.body)
            name            = data['name']
            email           = data['email']
            password        = data['password']
            is_doctor       = data['is_doctor']

            validate_email(email)
            self.validate_password(password)
            Validation.check_duplicate_email(email)

            CustomUser.objects.create_user(
                name      = name,
                email     = email,
                password  = password,
                is_doctor = is_doctor
            )
            return JsonResponse({'message' : 'SUCCESS'}, status=201)
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)
        except ValidationError as e:
            return JsonResponse({'message' : e.message}, status=400)
        except ValueError as e:
            return JsonResponse({'message' : str(e)}, status=400)
        except IntegrityError:
            return JsonResponse({'message' : 'EMAIL_IS_ALREADY_REGISTERED'}, status=400)

class LoginView(View):
    def generate_jwt(self, user):
        payload      = {'user_id': user.id, 'exp': datetime.now() +timedelta(hours=2)}
        access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        return access_token

    def post(self, request):
        data     = json.loads(request.body)
        email    = data['email']
        password = data['password']
        user     = authenticate(request, email=email, password=password)

        if user is not None:
            application_type = request.META['HTTP_TYPE_OF_APPLICATION']
            if application_type == "app":
                if user.is_doctor == False:
                    login(request, user)

                    return JsonResponse({
                        'message'     : 'SUCCESS_PATIENT_LOGIN',
                        "access_token": Validation.generate_jwt(user),
                        'user_id'     : user.id,
                        'user_name'   : user.name
                    }, status=200)
                else:
                    return JsonResponse({
                        'message' : 'DOCTOR_CAN_NOT_LOGIN_ON_APP'
                    }, status=401)

            elif application_type == "web":
                login(request, user)

                return JsonResponse({
                    'message'     : 'SUCCESS_LOGIN',
                    "access_token": Validation.generate_jwt(user),
                    'user_id'     : user.id,
                    'user_name'   : user.name
                }, status=200)

            else:
                return JsonResponse({'message' : 'INVALID_TYPE_OF_APPLICATION_ON_HEADER'}, status=400)
        else:
            return JsonResponse({'message' : 'WRONG_EMAIL_OR_PASSWORD'}, status=401)

class CheckDuplicateEmailView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data['email']
            Validation.check_duplicate_email(email)
            
            return JsonResponse({'message' : 'CAN_REGISTER_WITH_THIS_EMAIL'}, status=201)
        except IntegrityError:
            return JsonResponse({'message' : 'EMAIL_IS_ALREADY_REGISTERED'}, status=400)
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)