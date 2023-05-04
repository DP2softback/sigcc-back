from django.urls import path
from login.views import *

urlpatterns = [
    path('users', UsuarioView.as_view()),
    ##path('roles', RoleView.as_view()),
    ##path('employee', EmployeeView.as_view()),
]