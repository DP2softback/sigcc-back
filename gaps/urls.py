from django.urls import include, path
from gaps.views import CompetenciaView, TipoCompetenciaView

brechas_patterns = [
    path('competencias', CompetenciaView.as_view()),
    path('tipoCompetencias', TipoCompetenciaView.as_view())
]

urlpatterns = [
    path('brechas/', include(brechas_patterns)),
]