from django.urls import path

from users.views import SignUpView, LoginView,CheckDuplicateEmailView

urlpatterns = [
    path('/signup', SignUpView.as_view()),
    path('/login', LoginView.as_view()),
    path('/check_duplicate', CheckDuplicateEmailView.as_view()),

]