from django.urls import path
from .views import *

urlpatterns = [
    path('hiring-processes', HiringProcessView.as_view()),
    path('hiring-processes/employees', HiringProcessView.as_view()),
    path('hiring-processes/<int:pk>', HiringProcessView.as_view()),
    path('stage-types', StageTypeView.as_view()),
    path('process-stages', ProcessStageView.as_view()),
]
