from django.urls import path
from login.views import UsuarioView

urlpatterns = [
    path('users', UsuarioView.as_view()),
]