from django.urls import path

from capacitaciones import views

urlpatterns = [
    path('learning_path/<int:pk>/udemy/<str:course>/<int:delete>', views.get_udemy_valid_courses),
    #path('udemy/detail/', views.get_udemy_course_detail),
    #path('learning_path/', views.learning_path_api_view),
    #path('learning_path/<int:pk>/course/', views.curso_lp_api_vew),
    #path('learning_path/<int:pk_lp>/course/detail/<int:pk_curso>', views.curso_detail_lp_api_view)
]