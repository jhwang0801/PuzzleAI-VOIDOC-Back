import re

from django.core.exceptions import ValidationError
from django.db.utils        import IntegrityError

from users.models import CustomUser

def validate_password(password):
    REGEX_PASSWORD = '^[A-Za-z0-9]{8,}$'

    if not re.match(REGEX_PASSWORD, password):
        raise ValidationError('Enter a valid password.')

def exist_email(email):
    if CustomUser.objects.filter(email = email).exists():
        raise IntegrityError