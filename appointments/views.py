from datetime import datetime

from django.http                import JsonResponse
from django.views               import View
from django.conf                import settings
from django.core                import serializers
from django.core.paginator      import Paginator, PageNotAnInteger, EmptyPage
from django.db.models           import CharField, IntegerField, Value as V, Q, Func, F, ExpressionWrapper
from django.db.models.functions import Concat

from users.utils  import login_decorator, DateTimeFormat
from users.models import Department, Doctor, WorkingDay, WorkingTime
from appointments.models import Appointment, UserAppointment

class DepartmentsListView(View):
    @login_decorator
    def get(self, request):
        departments_list = Department.objects.annotate(
            thumbnails = Concat(V(f'{settings.LOCAL_PATH}/department_thumbnail/'), 'thumbnail', output_field=CharField())
            ).values('id', 'name', 'thumbnails')

        return JsonResponse({"result" : list(departments_list)}, status = 200)

class DoctorListView(View):
    @login_decorator
    def get(self, request, department_id):
        try: 
            page    = request.GET.get('page', 1)
            doctors = Doctor.objects.select_related('user', 'department', 'hospital').filter(department_id=department_id)\
                .annotate(
                    names        = Concat(V(''), 'user__name', output_field=CharField()),
                    departments  = Concat(V(''), 'department__name', output_field=CharField()),
                    hospitals    = Concat(V(''), 'hospital__name', output_field=CharField()),
                    profile_imgs = Concat(V(f'{settings.LOCAL_PATH}/doctor_profile_img/'), 'profile_img', output_field=CharField())
                ).values('id', 'names', 'departments', 'hospitals', 'profile_imgs').order_by('id')

            doctors_paginator = Paginator(doctors, 6).page(page).object_list

            return JsonResponse({"result" : list(doctors_paginator)}, status=200)

        except PageNotAnInteger:
            return JsonResponse({'message' : 'PAGE_HAS_TO_BE_AN_INTEGER'})

        except EmptyPage:
            return JsonResponse({'message' : 'THE_GIVEN_PAGE_CONTAINS_NOTHING'})

class WorkingDayView(View):
    @login_decorator
    def get(self, request, doctor_id):
        year        = int(request.GET.get('year'))
        month       = int(request.GET.get('month'))
        not_day_off = [working_day.date.day for working_day in WorkingDay.objects.filter(doctor_id=doctor_id, date__year = year, date__month = month)]

        return JsonResponse({'result' : not_day_off}, status=200)

class WorkingTimeView(View):
    @login_decorator
    def get(self, request, doctor_id):
        year          = int(request.GET.get('year'))
        month         = int(request.GET.get('month'))
        day           = int(request.GET.get('day'))
        selected_date = datetime(year, month, day)
        current       = datetime.strptime((datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d")

        if selected_date < current:
            return JsonResponse({'message' : 'CANNOT_MAKE_AN_APPOINTMENT_FOR PAST_DATES'}, status=400)

        elif selected_date == current:
            return JsonResponse({'message' : 'NOT_AVAILABLE_ON_THE_DAY_OF_MAKING_AN_APPOINTMENT'}, status=400)

        q = Q()
        q.add(Q(userappointment__doctor_id = doctor_id), q.AND)
        q.add(Q(date = selected_date), q.AND)
        q.add(Q(state_id = 1) | Q(state_id = 2), q.AND)

        appointments            = Appointment.objects.filter(q)
        working_times           = WorkingTime.objects.filter(working_day__doctor_id = doctor_id, working_day__date = selected_date.date())
        appointmented_time_list = [appointment.time.strftime("%H:%M") for appointment in appointments]
        working_time_list       = [working_time.time.strftime("%H:%M") for working_time in working_times]

        return JsonResponse({'working_time' : working_time_list, 'appointmented_time' : appointmented_time_list}, status=200)

class AppointmentListView(View, DateTimeFormat):
    @login_decorator
    def get(self, request):
        try: 
            page    = request.GET.get('page', 1)
            patient_id = request.user.id
            appointment_info = Appointment.objects.filter(userappointment__patient_id=patient_id)\
                .annotate(
                    appointment_id = Concat(V(''), 'id', output_field=IntegerField()),
                    appointment_date = Concat(V(''), 
                        Func(F('date'), V('%m-%d-%Y(%W) '), function='DATE_FORMAT', output_field=CharField()), 
                        Func(F('time'), V('%p %h:%i'), function='TIME_FORMAT', output_field=CharField()),
                        output_field=CharField()), 
                    state_name     = Concat(V(''), 'state_id', output_field=CharField()),
                ).values('appointment_id', 'appointment_date', 'state_name')
            
            appointment_people = UserAppointment.objects.filter(patient_id=patient_id)\
                .annotate(
                    doctor_name  = Concat(V(''), 'doctor__user__name', output_field=CharField()),         
                    doctor_hospital    = Concat(V(''), 'doctor__hospital__name', output_field=CharField()),
                    doctor_department  = Concat(V(''), 'doctor__department__name', output_field=CharField()),
                    doctor_profile_img = Concat(V(f'{settings.LOCAL_PATH}/doctor_profile_img/'), 'doctor__profile_img', output_field=CharField())
                ).values('appointment_id', 'doctor_name', 'doctor_hospital', 'doctor_department', 'doctor_profile_img')

            lst = sorted(chain(appointment_info, appointment_people), key=lambda x:x['appointment_id'])
            appointments = []
            for k,v in groupby(lst, key=lambda x:x['appointment_id']):
                d = {}
                for dct in v:
                    d.update(dct)
                appointments.append(d)

            appointments_paginator = Paginator(appointments, 4).page(page).object_list

            return JsonResponse({"result" : list(appointments_paginator)}, status=200)

        except PageNotAnInteger:
            return JsonResponse({'message' : 'PAGE_HAS_TO_BE_AN_INTEGER'})

        except EmptyPage:
            return JsonResponse({'message' : 'THE_GIVEN_PAGE_CONTAINS_NOTHING'})

class AppointmentDetailView(View):
    @login_decorator
    def get(self, request, appointment_id):
        patient_id = request.user.id
        appointment_info = Appointment.objects.filter(userappointment__patient_id=patient_id, userappointment__appointment_id=appointment_id)\
            .annotate(
                Wound_img   = Concat(V(f'{settings.LOCAL_PATH}/media/wound_img/'), 'appointmentimage__wound_img', output_field=CharField()),
                patient_symptom = Concat(V(''), 'symptom', output_field=CharField()),
                doctor_opinion = Concat(V(''), 'opinion', output_field=CharField()),
                appointment_date = Concat(V(''), 
                        Func(F('date'), V('%m-%d-%Y(%W) '), function='DATE_FORMAT', output_field=CharField()), 
                        Func(F('time'), V('%p %h:%i'), function='TIME_FORMAT', output_field=CharField()),
                        output_field=CharField())
            ).values('Wound_img','patient_symptom', 'doctor_opinion', 'appointment_date')
        
            
        return JsonResponse({"result" : list(appointment_info)}, status=200)
