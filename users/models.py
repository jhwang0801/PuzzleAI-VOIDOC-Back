from django.db                  import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, name, email, password, is_doctor):
        if not name:
            raise ValueError('Users must have the name')
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have the password')

        user = self.model(
            email     = self.normalize_email(email),
            name      = name,
            is_doctor = is_doctor
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, is_doctor, password):
    
        user = self.create_user(
            email     = self.normalize_email(email),
            name      = name,
            is_doctor = is_doctor,
            password  = password
        )

        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    name         = models.CharField(max_length=50)
    email        = models.EmailField(max_length=128, verbose_name='email', unique=True)
    is_doctor    = models.BooleanField(default=False, null=True)
    date_joined  = models.DateTimeField(auto_now_add=True)
    is_superuser = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['name', 'password', 'is_doctor']

    def __str__(self): 
        return self.email 
    
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_superuser

    class Meta: 
        db_table = 'users'

class Doctor(models.Model):
    user        = models.OneToOneField('CustomUser', on_delete=models.CASCADE)
    department  = models.ForeignKey('Department', on_delete=models.CASCADE)
    hospital    = models.ForeignKey('Hospital', on_delete=models.SET_NULL, null=True)
    profile_img = models.FileField(upload_to="doctor_profile_img")

    class Meta: 
        db_table = 'doctors'

class WorkingDay(models.Model): 
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE)
    date   = models.DateField()

    class Meta: 
        db_table = 'working_days'

class WorkingTime(models.Model):
    working_day = models.ForeignKey('WorkingDay', on_delete=models.CASCADE)
    time        = models.TimeField()

    class Meta:
        db_table = 'working_times'

class Hospital(models.Model): 
    name = models.CharField(max_length=50)

    class Meta: 
        db_table = 'hospitals'

class Department(models.Model): 
    name      = models.CharField(max_length=50)
    thumbnail = models.FileField(upload_to='department_thumbnail')

    class Meta: 
        db_table = 'departments'