from django.urls import path

from appointments.views import DepartmentsListView, DoctorListView

urlpatterns = [
    path('/departments', DepartmentsListView.as_view()),
    path('/departments/<int:department_id>', DoctorListView.as_view()),
]