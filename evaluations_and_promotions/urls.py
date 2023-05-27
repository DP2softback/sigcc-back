from django.urls import path
from evaluations_and_promotions.views import *

urlpatterns = [
    path('evaluation', EvaluationAPI.as_view()),
    path('evaluationType', EvaluationTypeGenericView.as_view()),
    path('position', PositionGenericView.as_view()),
    path('area', AreaGenericView.as_view()),
    path('category', CategoryGenericView.as_view()),
    path('subcategory', SubCategoryTypeGenericView.as_view()),
    path('employees', GetPersonasACargo.as_view()),
    path('evaluations', GetHistoricoDeEvaluaciones.as_view()),
    path('evaluationxsubcat', EvaluationXSubcatAPI.as_view()),
    
]