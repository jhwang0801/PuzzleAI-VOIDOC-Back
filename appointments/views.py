from django.http           import JsonResponse
from django.views          import View
from django.conf           import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.functions import Concat, Value as V

from users.utils  import login_decorator
from users.models import Department, Doctor, WorkingDay, WorkingTime, CustomUser

from appointments.models import Appointment, UserAppointment

class DepartmentsListView(View):
    @login_decorator
    def get(self, request):

        departments_list = [{
            'id'       : department.id,
            'name'     : department.name,
            'thumbnail': settings.LOCAL_PATH + "department_thumbnail/" + f"{department.thumbnail}"
        } for department in Department.objects.all()]

        return JsonResponse({"result" : departments_list, "user_name" : request.user.name}, status = 200)

class DoctorListView(View):
    @login_decorator
    def get(self, request, department_id):
        try: 
            page        = request.GET.get('page', 1)
            doctors     = Doctor.objects.select_related('user', 'department', 'hospital').filter(department_id=department_id)
            doctor_list = [{
                'id'         : doctor.id,
                'name'       : doctor.user.name,
                'department' : doctor.department.name,
                'hospital'   : doctor.hospital.name,
                'profile_img': settings.LOCAL_PATH + "doctor_profile_img/" + f"{doctor.profile_img}"
            } for doctor in doctors]

            doctors_paginator = Paginator(doctor_list, 6).page(page).object_list

            return JsonResponse({"result" : doctors_paginator}, status=200)

        except PageNotAnInteger:
            return JsonResponse({'message' : 'PAGE_HAS_TO_BE_AN_INTEGER'})

        except EmptyPage:
            return JsonResponse({'message' : 'THE_GIVEN_PAGE_CONTAINS_NOTHING'})
"""
class CalendarView(View):
    @login_decorator
    def get(self, request, doctor_id):
        # doctor = Doctor.objects.get(pk=doctor_id)
        dates_list = WorkingDay.select_related('doctor', 'date').filter(doctor_id=doctor_id)\
            .annotate(
                doctor = Concat(V(''), 'user__name', output_field=CharField()),
                date = Concat(V(''), 'date', output_field=DateField()),
            ).values('doctor', 'date').order_by('date')

        return JsonResponse({"result" : list(dates_list)}, status = 200)

class TimeSlotsView(View):
    @login_decorator
    def get(self, request, working_day_id):
        # working_day = WorkingDay.objects.get(pk=working_day_id)
        time_slots_list = WorkingTime.select_related('working_day_id', 'time').filter(working_day_id=working_day_id)\
            .annotate(
                working_day = Concat(V(''), 'date', output_field=DateField()),
                working_time = Concat(V(''), 'time', output_field=TimeField())
            ).values('working_day', 'working_time').order_by('working_time')
        
        return JsonResponse({"result" : list(time_slots_list)}, status = 200)
'''
Class Appointment(models.Model):
    symptom    = models.TextField()
    opinion    = models.TextField()
    state      = models.ForeignKey('State', on_delete=models.CASCADE)
    date       = models.DateField()
    time       = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
'''

class AppointmentView(View):
    @login_decorator
    def get(self, request):
        # View for all the appointment details
        # References the time slot and date given in the previous two views
        
class UserAppointmentView(View):
    @login_decorator
    def get(self, request, doctor_id, patient_id, appointment_id):
        doctor      = Doctor.objects.get(pk=doctor_id)
        patient     = CustomUser.objects.get(pk=patient_id)
        appointment = Appointment.objects.get(pk=appointment_id)

        user_appointment = UserAppointment.objects.select_related('doctor', 'patient', 'appointment').filter(appointment_id=appointment_id)\
            .annotate(
                names        = Concat(V(''), 'user__name', output_field=CharField()),
                departments  = Concat(V(''), 'department__name', output_field=CharField()),
                hospitals    = Concat(V(''), 'hospital__name', output_field=CharField()),
                profile_imgs = Concat(V(f'{settings.LOCAL_PATH}/doctor_profile_img/'), 'profile_img', output_field=CharField())
            ).values('id', 'names', 'departments', 'hospitals', 'profile_imgs').order_by('id')
    
        return JsonResponse({"result" : list(user_appointment)}, status=200)
                
"""