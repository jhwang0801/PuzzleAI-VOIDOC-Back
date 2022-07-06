from datetime import datetime, date, time, timedelta

from django.http                import JsonResponse
from django.db                  import transaction
from django.views               import View
from django.conf                import settings
from django.core.paginator      import Paginator, PageNotAnInteger, EmptyPage
from django.db.models           import CharField, Value as V, Q
from django.db.models.functions import Concat

from users.utils  import login_decorator, DateTimeFormat
from users.models import Department, Doctor, WorkingDay, WorkingTime
from appointments.models import Appointment, AppointmentImage, UserAppointment

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
            appointments = Appointment.objects.select_related('state').prefetch_related('userappointment_set', 'userappointment_set__doctor', 'userappointment_set__doctor__user', 'userappointment_set__doctor__department', 'userappointment_set__doctor__hospital')\
                .filter(userappointment__patient_id = request.user.id).order_by('state_id', 'date', 'time')
            appointment_list = [{
                "appointment_id"    : appointment.id,
                "appointment_date"  : self.format_date_time(appointment.date, appointment.time),
                "state_name"        : appointment.state.name,
                "doctor_name"       : appointment.userappointment_set.first().doctor.user.name,
                "doctor_hospital"   : appointment.userappointment_set.first().doctor.hospital.name,
                "doctor_department" : appointment.userappointment_set.first().doctor.department.name,
                "doctor_profile_img": f'{settings.LOCAL_PATH}/doctor_profile_img/{appointment.userappointment_set.first().doctor.profile_img}'
            } for appointment in appointments]

            appointments_paginator = Paginator(appointment_list, 4).page(page).object_list
            return JsonResponse({'result' : appointments_paginator}, status=200)

        except PageNotAnInteger:
            return JsonResponse({'message' : 'PAGE_HAS_TO_BE_AN_INTEGER'})

        except EmptyPage:
            return JsonResponse({'message' : 'THE_GIVEN_PAGE_CONTAINS_NOTHING'})

class AppointmentDetailView(View, DateTimeFormat):
    @login_decorator
    def get(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(userappointment__patient_id=request.user.id, userappointment__appointment_id=appointment_id)
            appointment_detail = {    
                "Wound_img"       : [f'{settings.LOCAL_PATH}/wound_img/{image.wound_img}' for image in appointment.appointmentimage_set.all()],  
                "patient_symptom"   : appointment.symptom,
                "doctor_opinion"    : appointment.opinion,
                "appointment_date"  : self.format_date_time(appointment.date, appointment.time)
            }

            return JsonResponse({'result' : appointment_detail}, status=200)
        
        except Appointment.DoesNotExist:
            return JsonResponse({'APPOINTMENT_DOES_NOT_EXIST'}, status=404)

class CancellationView(View):
    @login_decorator
    def patch(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id, userappointment__patient_id=request.user.id)
            appointment_datetime = datetime.combine(appointment.date, appointment.time)

            if appointment_datetime - datetime.now() < timedelta(seconds=3600):
                return JsonResponse({'message' : 'APPOINTMENTS_CAN_BE_CANCELLED_ONLY_AN_HOUR_PRIOR_TO_THE_SCHEDULED_TIME'}, status=400)

            if appointment.state.id == 1:
                Appointment.objects.filter(id=appointment_id).update(state_id = 2)
                return JsonResponse({'message' : 'APPOINTMENT_HAS_BEEN_CANCELED'}, status=200)
            else:
                return JsonResponse({'message' : 'ALREADY_CANCELED_OR_CLOSED_APPOINTMENT'}, status = 400)
        except KeyError:
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)
        except Appointment.DoesNotExist:
            return JsonResponse({"message" : "APPOINTMENT_DOES_NOT_EXIST"}, status=404)

class AppointmentCreationView(View):
    @login_decorator
    def post(self, request):
        try:
            patient_id          = request.user.id
            doctor_id           = int(request.POST['doctor_id'])
            appointmented_year  = int(request.POST['year'])
            appointmented_month = int(request.POST['month'])
            appointmented_day   = int(request.POST['day'])
            appointmented_time  = int(request.POST['time'])
            symptom             = request.POST['symptom']
            images              = request.FILES.getlist('image')
            selected_date       = date(appointmented_year, appointmented_month, appointmented_day)
            selected_time       = time(appointmented_time)

            if len(images) > 6:
                return JsonResponse({'message' : 'DO_NOT_ALLOW_TO_UPLOAD_IMAGES_MORE_THAN_6'}, status=400)

            with transaction.atomic():
                new_appointment = Appointment.objects.create(
                    symptom  = symptom,
                    date     = selected_date,
                    time     = selected_time,
                    state_id = 1
                )

                UserAppointment.objects.create(
                    appointment_id = new_appointment.id,
                    doctor_id      = doctor_id,
                    patient_id     = patient_id
                )
                
                AppointmentImage.objects.bulk_create([
                    AppointmentImage(
                        appointment_id = new_appointment.id,
                        wound_img      = image
                    ) for image in images
                ])
                return JsonResponse({'message' : 'YOUR_APPOINTMENT_IS_CREATED'}, status = 201)
        except KeyError:
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)