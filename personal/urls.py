from django.urls import path
from .views import *

urlpatterns = [
    path('hiring-process', HiringProcessView.as_view())
]
