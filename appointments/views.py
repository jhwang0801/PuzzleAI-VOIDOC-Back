from django.http           import JsonResponse
from django.views          import View
from django.conf           import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from users.utils  import login_decorator
from users.models import Department, Doctor

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