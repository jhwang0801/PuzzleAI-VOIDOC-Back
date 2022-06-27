from django.http                import JsonResponse
from django.views               import View
from django.conf                import settings
from django.core.paginator      import Paginator, PageNotAnInteger, EmptyPage
from django.db.models           import CharField, Value as V
from django.db.models.functions import Concat

from users.utils  import login_decorator
from users.models import Department, Doctor

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