from django.urls import path

from appointments.views import DepartmentsListView, DoctorListView, WorkingDayView, WorkingTimeView, CancellationView

urlpatterns = [
    path('/departments', DepartmentsListView.as_view()),
    path('/departments/<int:department_id>', DoctorListView.as_view()),
    path('/doctor/<int:doctor_id>/workingday', WorkingDayView.as_view()),
    path('/doctor/<int:doctor_id>/workingtime', WorkingTimeView.as_view()),
    path('/<int:appointment_id>/cancellation', CancellationView.as_view()),
]