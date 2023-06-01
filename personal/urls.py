from django.urls import path
from .views import *

urlpatterns = [
    path('hiring-processes', HiringProcessView.as_view()),
    path('stage-types', StageTypeView.as_view())
]
