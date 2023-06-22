from django.urls import include, path
from gaps.views import *

gaps_patterns = [
    path('employeeArea', EmployeeAreaView.as_view()),

    path('competenceAreaPosition', CompetenceAreaPositionView.as_view()),
    path('competenceEmployee', CompetenceEmployeeView.as_view()),
    path('employeeTrainingNeed', TrainingNeedView.as_view()),

    path('competenceAreaPositionSearch', SearchCompetenceAreaPositionView.as_view()),
    path('competenceEmployeeSearch', SearchCompetenceEmployeeView.as_view()),
    path('employeeTrainingNeedSearch', SearchNeedView.as_view()),

    path('competenceSearch', SearchCompetenceView.as_view()),
    path('competenceConsolidateSearch', SearchCompetenceConsolidateView.as_view()),
    path('trainingNeedSearch', SearchTrainingNeedView.as_view()),
    path('competenceTypes', CompetenceTypeView.as_view()),
    path('competenceTypesSearch/<int:pk>', SearchCompetenteTypeView.as_view()),

    path('competenceScale', CompetenceScaleView.as_view()),
    path('competenceScale/<int:id>', CompetenceScaleView.as_view()),

    path('competences', CompetenceView.as_view()),
    path('competences/<int:id>', CompetenceView.as_view()),

    path('jobOfferSearch', SearchJobOfferView.as_view()),
    path('trainingNeedDemand', GenerateTrainingDemandView.as_view()),
    path('trainingNeedCourse', TrainingNeedCourseView.as_view()),
    path('trainingNeedCourseSearch', SearchTrainingNeedCourseView.as_view())
]

urlpatterns = [
    path('gaps/', include(gaps_patterns)),
]