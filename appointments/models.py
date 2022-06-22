from django.db import models

class Appointment(models.Model):
    symptom    = models.TextField()
    opinion    = models.TextField()
    state      = models.ForeignKey('State', on_delete=models.CASCADE)
    date       = models.DateField()
    time       = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        db_table = 'appointments'

class UserAppointment(models.Model): 
    user        = models.ForeignKey('users.User', on_delete=models.CASCADE)
    doctor      = models.ForeignKey('users.Doctor', on_delete=models.CASCADE)
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_appointments'

class State(models.Model): 
    name = models.CharField(max_length=30)

    class Meta: 
        db_table = 'states'

class AppointmentImage(models.Model):
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE)
    wound_img   = models.FileField(upload_to='wound_img')

    class Meta:
        db_table = 'appointment_images'