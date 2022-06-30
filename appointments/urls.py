from django.urls import path

from appointments.views import AppointmentListView, DepartmentsListView, DoctorListView, WorkingDayView, WorkingTimeView

urlpatterns = [
    path('/departments', DepartmentsListView.as_view()),
    path('/departments/<int:department_id>', DoctorListView.as_view()),
    path('/doctor/<int:doctor_id>/workingday', WorkingDayView.as_view()),
    path('/doctor/<int:doctor_id>/workingtime', WorkingTimeView.as_view()),
    path('/user/<int:patient_id>', AppointmentListView.as_view())
]