from django.urls import include, path
from gaps.views import CompetenceView, CompetenceTypeView, SearchCompetenceView, SearchTrainingNeedView, SearchCompetenceConsolidateView, CompetenceAreaPositionView, CompetenceEmployeeView, TrainingNeedView, SearchCompetenceAreaPositionView, SearchCompetenceEmployeeView, SearchNeedView, EmployeeAreaView

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
    path('competences', CompetenceView.as_view()),
    path('competences/<int:id>', CompetenceView.as_view())
]

urlpatterns = [
    path('gaps/', include(gaps_patterns)),
]