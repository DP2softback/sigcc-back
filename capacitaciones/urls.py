from django.urls import path

from capacitaciones import views
from capacitaciones.views.views_p1 import GetUdemyValidCourses, GetUdemyCourseDetail, LearningPathAPIView, \
    CursoUdemyLpAPIView, CursoDetailLpApiView, UploadFilesInS3APIView, DeleteFilesInS3APIView
from capacitaciones.views.views_p2 import CursoEmpresaCourseAPIView, CursoEmpresaDetailAPIView, \
    CursoEmpresaSearchEspecialAPIView, CursoEmpresaAPIView
from capacitaciones.views.views_p3 import LearningPathCreateFromTemplateAPIView

urlpatterns = [
    path('learning_path/<int:pk>/udemy/<str:course>/<int:delete>', GetUdemyValidCourses.as_view()),
    path('udemy/detail/', GetUdemyCourseDetail.as_view()),
    path('learning_path/', LearningPathAPIView.as_view()),
    path('learning_path/<int:pk>/course/', CursoUdemyLpAPIView.as_view()),
    path('learning_path/<int:pk_lp>/course/detail/<int:pk_curso>', CursoDetailLpApiView.as_view()),
    path('learning_path/template/', LearningPathCreateFromTemplateAPIView.as_view()),
    path('course_company/', CursoEmpresaAPIView.as_view()),
    path('course_company_course/', CursoEmpresaCourseAPIView.as_view()),
    path('course_company/<int:pk>', CursoEmpresaDetailAPIView.as_view()),
    path('course_company_special', CursoEmpresaSearchEspecialAPIView.as_view()),
    path('upload_file/', UploadFilesInS3APIView.as_view()),
    path('delete_file/', DeleteFilesInS3APIView.as_view()),
]
