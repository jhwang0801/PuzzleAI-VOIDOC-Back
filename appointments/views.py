from datetime import datetime

from django.http                import JsonResponse
from django.views               import View
from django.conf                import settings
from django.core.paginator      import Paginator, PageNotAnInteger, EmptyPage
from django.db.models           import CharField, Value as V, Q
from django.db.models.functions import Concat

from users.utils  import login_decorator
from users.models import Department, Doctor, WorkingDay, WorkingTime
from appointments.models import Appointment

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
        q.add(Q(userappointment__doctor_id = doctor_id, date=selected_date, state_id = 1), q.AND)
        q.add(Q(userappointment__doctor_id = doctor_id, date=selected_date, state_id = 2), q.OR)

        appointments            = Appointment.objects.filter(q)
        working_times           = WorkingTime.objects.filter(working_day__doctor_id = doctor_id, working_day__date = selected_date.date())
        appointmented_time_list = [appointment.time.strftime("%H:%M") for appointment in appointments]
        working_time_list       = [working_time.time.strftime("%H:%M") for working_time in working_times]

        return JsonResponse({'working_time' : working_time_list, 'appointmented_time' : appointmented_time_list}, status=200)