import json

from django.views           import View
from django.http            import JsonResponse
from django.db.utils        import IntegrityError
from django.forms           import ValidationError
from django.core.validators import validate_email
from django.contrib.auth    import authenticate, login

from users.models import CustomUser
from users.utils  import validate_password

class SignUpView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            name            = data['name']
            email           = data['email']
            password        = data['password']
            is_doctor       = data['is_doctor']

            validate_email(email)
            validate_password(password)

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
    def post(self,request):
        data = json.loads(request.body)
        username = data['email']
        password = data['password']

        # Authenticate that email and password match a user in the database
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message' : 'SUCCESS'}, status=201)
        else:
            return JsonResponse({'message' : 'Username or password is incorrect!'}, status=400)