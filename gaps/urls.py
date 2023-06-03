from django.urls import include, path
from gaps.views import CompetenceView, CompetenceTypeView, SearchCompetenceView, SearchTrainingNeedView, SearchCompetenceConsolidateView

gaps_patterns = [
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