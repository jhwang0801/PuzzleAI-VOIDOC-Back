import json

from django.views           import View
from django.http            import JsonResponse
from django.db.utils        import IntegrityError
from django.forms           import ValidationError
from django.core            import mail
from django.core.validators import validate_email
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth    import login, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site  
from django.template.loader import render_to_string  
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

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

            user = CustomUser.objects.create_user(
                name      = name,
                email     = email,
                password  = password,
                is_doctor = is_doctor,
            )

            user.is_active = False
            
            connection = mail.get_connection()
            connection.open()
            current_site = get_current_site(request)  
            message = render_to_string('acc_active_email.html', {  
                'name': name,  
                'domain': current_site.domain,  
                'uid': urlsafe_base64_encode(force_bytes(user.id)),  
                'token': default_token_generator.make_token(user),  
            })
            email = mail.EmailMessage(
                'Welcome, ' + name + ', to VOIDOC!',
                message,
                'noreply.voidoc@gmail.com',
                [email],
                connection=connection,
            )
            connection.send_messages([email])
            connection.close()

            return JsonResponse({'message' : 'SUCCESS'}, status=201)
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)
        except ValidationError as e:
            return JsonResponse({'message' : e.message}, status=400)
        except ValueError as e:
            return JsonResponse({'message' : str(e)}, status=400)
        except IntegrityError:
            return JsonResponse({'message' : 'EMAIL_IS_ALREADY_REGISTERED'}, status=400)

class ActivateUserView(View, Validation):
    def get(self, request, uid, token):
        try:
            id = force_str(urlsafe_base64_decode(uid))
            user = CustomUser.objects.get(pk=id)  
        except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):  
            user = None
        if user is not None and default_token_generator.check_token(user, token):  
            user.is_active = True  
            user.save()  
            return JsonResponse({'message' : 'SUCCESS_USER_ACTIVATED'}, status=200)  
        else:  
            return JsonResponse({'message' : 'INVALID_AUTHORIZATION_LINK'}, status=400)    

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
            try:
                user = CustomUser.objects.get(email=email)
                if(user.is_active == False):
                    return JsonResponse({'message' : 'USER_NOT_YET_ACTIVATED'}, status=401)
                else:
                    return JsonResponse({'message' : 'WRONG_EMAIL_OR_PASSWORD'}, status=401)
            except ObjectDoesNotExist:
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

class PasswordChangeView(View, Validation):
    def post(self, request):
        data            = json.loads(request.body)
        email           = data['email']
        old_password    = data['old_password']
        new_password    = data['new_password']
        try:
            user = CustomUser.objects.get(email=email)
            user.check_password(old_password)
            self.validate_password(new_password)
            user.set_password(new_password)
            user.save()
            return JsonResponse({
                'message'     : 'PASSWORD_CHANGED_SUCCESSFULLY',
                'email'       : user.email,
                'new_password': new_password,
                }, status=201) 
        except ObjectDoesNotExist:
            return JsonResponse({'message' : 'NO_USER_EXISTS_WITH_THIS_EMAIL'}, status=404)
        except ValidationError as e:
            return JsonResponse({'message' : e.message}, status=400)