from django.urls import path
from appointments.models import UserAppointment

from appointments.views import DepartmentsListView, DoctorListView

urlpatterns = [
    path('/departments', DepartmentsListView.as_view()),
    path('/departments/<int:department_id>', DoctorListView.as_view()),
    # path('/doctor/<int:doctor_id>', CalendarView.asview()),
    # path('/calendar/time_slot', TimeSlotsView.as_view()),
    # path('/appointments/<int:appointment_id>', UserAppointment.as_view()),
    # path('/appointments/<int:appointment_id>/details', AppointmentView.as_view()),
]