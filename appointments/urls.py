from django.urls import path

from appointments.views import AppointmentListView, AppointmentView, DepartmentsListView, DoctorListView, WorkingDayView, WorkingTimeView

urlpatterns = [
    path('/departments', DepartmentsListView.as_view()),
    path('/departments/<int:department_id>', DoctorListView.as_view()),
    path('/doctor/<int:doctor_id>/workingday', WorkingDayView.as_view()),
    path('/doctor/<int:doctor_id>/workingtime', WorkingTimeView.as_view()),

    # In progress tests for new appointment views:
    path('/user/<int:patient_id>', AppointmentListView.as_view()),
    path('/user/<int:patient_id>/appointment_view/<int:appointment_id>', AppointmentView.as_view()),
    #path('/doctor/<int:doctor_id>/create_appointment/user/<int:patient_id>', AppointmentView.as_view()),
    #path('/update/<int:appointment_id>', AppointmentView.as_view())
]