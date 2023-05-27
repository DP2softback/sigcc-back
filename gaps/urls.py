from django.urls import include, path
from gaps.views import CompetenciaView, TipoCompetenciaView, BuscarCompetenciaView, BuscarNecesidadView

brechas_patterns = [
    path('competencias', CompetenciaView.as_view()),
    path('competencias/<int:id>', CompetenciaView.as_view()),
    path('competenciasBuscar', BuscarCompetenciaView.as_view()),
    path('necesidadesBuscar', BuscarNecesidadView.as_view()),
    path('tipoCompetencias', TipoCompetenciaView.as_view())
]

urlpatterns = [
    path('brechas/', include(brechas_patterns)),
]