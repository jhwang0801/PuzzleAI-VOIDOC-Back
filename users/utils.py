import jwt

from django.conf import settings
from django.http import JsonResponse

from users.models import CustomUser

def login_decorator(func):
    def wrapper(self,request,*args,**kwargs):
        try:
            access_token = request.headers.get('Authorization')
            payload      = jwt.decode(access_token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
            user         = CustomUser.objects.get(id = payload['user_id'])
            request.user = user

        except jwt.exceptions.DecodeError: 
            return JsonResponse({'message' : 'INVALID_TOKEN'}, status = 400)
        except CustomUser.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_USER'}, status=400)
        except jwt.ExpiredSignatureError:
            return JsonResponse({'message' : 'EXPIRED_TOKEN'}, status=401)

        return func(self,request,*args,**kwargs)
    return wrapper