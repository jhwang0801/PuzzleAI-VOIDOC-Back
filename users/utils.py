import re
import jwt

from datetime               import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db.utils        import IntegrityError
from django.conf            import settings

from users.models import CustomUser

def validate_password(password):
    REGEX_PASSWORD = '^[A-Za-z0-9]{8,}$'

    if not re.match(REGEX_PASSWORD, password):
        raise ValidationError('Enter a valid password.')

def check_duplicate_email(email):
    if CustomUser.objects.filter(email = email).exists():
        raise IntegrityError

def generate_jwt(user):
    payload = {'user_id': user.id, 'exp': datetime.now() +timedelta(hours=2)}
    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return access_token