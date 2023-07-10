from django.urls import path

from .views import *

urlpatterns = [
    path('hiring-processes', HiringProcessView.as_view()),
    path('hiring-processes/employees', HiringProcessView.as_view()),
    path('hiring-processes/<int:pk>', HiringProcessView.as_view()),
    path('stage-types', StageTypeView.as_view()),
    path('process-stages', ProcessStageView.as_view()),
    path('process-stages/<int:pk>', ProcessStageView.as_view()),
    path('job-offers', JobOfferView.as_view()),    
    path('positions', AllPositionView.as_view()),
    path('positions/<int:pk>', PositionView.as_view()),
    path('areaxposition', AreaxPositionView.as_view()),    
    path('functions', FunctionsView.as_view()),
    path('functions/<int:pk>', FunctionsView.as_view()),
    path('training', TrainingxLevelView.as_view()),
]
