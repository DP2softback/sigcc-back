from django.urls import path
from login.views import *

urlpatterns = [
    path('users', UserView.as_view()),
    path('roles', RoleView.as_view()),
    path('employee', EmployeeView.as_view()),
    path('login', LoginView.as_view()),
    path('whoiam', WhoIAmView.as_view()),
    path('logout', Logout.as_view()),
]
