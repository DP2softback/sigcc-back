from django.urls import include, path
from gaps.views import CompetenciaView

brechas_patterns = [
    path('competencias', CompetenciaView.as_view()),
]

urlpatterns = [
    path('brechas/', include(brechas_patterns)),
]