import json

from django.views           import View
from django.http            import JsonResponse
from django.db.utils        import IntegrityError
from django.forms           import ValidationError
from django.core.validators import validate_email
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth    import login, authenticate

from users.models import CustomUser
from users.utils  import Validation

class SignUpView(View, Validation):
    def post(self, request):
        try:
            data = json.loads(request.body)
            name            = data['name']
            email           = data['email']
            password        = data['password']
            is_doctor       = data['is_doctor']

            validate_email(email)
            self.validate_password(password)
            self.check_duplicate_email(email)

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

class LoginView(View, Validation):
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
                        "access_token": self.generate_jwt(user),
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
                    "access_token": self.generate_jwt(user),
                    'user_id'     : user.id,
                    'user_name'   : user.name
                }, status=200)

            else:
                return JsonResponse({'message' : 'INVALID_TYPE_OF_APPLICATION_ON_HEADER'}, status=400)
        else:
            return JsonResponse({'message' : 'WRONG_EMAIL_OR_PASSWORD'}, status=401)

class CheckDuplicateEmailView(View, Validation):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data['email']
            self.check_duplicate_email(email)
            
            return JsonResponse({'message' : 'CAN_REGISTER_WITH_THIS_EMAIL'}, status=201)
        except IntegrityError:
            return JsonResponse({'message' : 'EMAIL_IS_ALREADY_REGISTERED'}, status=400)
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)

class PasswordResetView(View, Validation):
    def post(self, request):
        data            = json.loads(request.body)
        email           = data['email']
        new_password    = data['password']
        try:
            user = CustomUser.objects.get(email=email)
            self.validate_password(new_password)
            user.set_password(new_password)
            user.save()
            return JsonResponse({
                'message' : 'PASSWORD_CHANGED_SUCCESSFULLY',
                'user_name'   : user.name,
                'new_password' : new_password,
                }, status=201) 
        except ObjectDoesNotExist:
            return JsonResponse({'message' : 'NO_USER_EXISTS_WITH_THIS_EMAIL'}, status=400)
        except ValidationError as e:
            return JsonResponse({'message' : e.message}, status=400)