from django.urls import path

from capacitaciones import views
from capacitaciones.views.views_p1 import GetUdemyValidCourses, GetUdemyCourseDetail, LearningPathAPIView, \
    CursoUdemyLpAPIView, CursoDetailLpApiView, UploadFilesInS3APIView, DeleteFilesInS3APIView, \
    BusquedaDeEmpleadosAPIView, AsignacionEmpleadoLearningPathAPIView
from capacitaciones.views.views_p2 import AsistenciaSesionAPIView, CursoEmpresaCourseAPIView, CursoEmpresaDetailAPIView, \
    CursoEmpresaSearchEspecialAPIView, CursoEmpresaAPIView, SesionDetailAPIView
from capacitaciones.views.views_p3 import LearningPathCreateFromTemplateAPIView, SesionAPIView, CategoriaAPIView, \
    ProveedorEmpresaXCategoriaAPIView, HabilidadesXEmpresaAPIView, PersonasXHabilidadesXEmpresaAPIView

urlpatterns = [
    path('learning_path/<int:pk>/udemy/<str:course>/<int:delete>', GetUdemyValidCourses.as_view()),
    path('udemy/detail/', GetUdemyCourseDetail.as_view()),
    path('learning_path/', LearningPathAPIView.as_view()),
    path('learning_path/<int:pk>/course/', CursoUdemyLpAPIView.as_view()),
    path('learning_path/<int:pk_lp>/course/detail/<int:pk_curso>', CursoDetailLpApiView.as_view()),
    path('learning_path/template/', LearningPathCreateFromTemplateAPIView.as_view()),
    path('course_company/', CursoEmpresaAPIView.as_view()),
    path('course_company_course/', CursoEmpresaCourseAPIView.as_view()),
    path('course_company_course/<int:pk>', CursoEmpresaDetailAPIView.as_view()),
    path('course_company_special', CursoEmpresaSearchEspecialAPIView.as_view()),
    path('sesion_course_company/', SesionAPIView.as_view()),
    path('sesion_course_company/<int:pk>', SesionDetailAPIView.as_view()),
    path('upload_file/', UploadFilesInS3APIView.as_view()),
    path('delete_file/', DeleteFilesInS3APIView.as_view()),
    path('get_categoria/', CategoriaAPIView.as_view()),
    path('get_proveedores_empresa/<int:pk>/', ProveedorEmpresaXCategoriaAPIView.as_view()),
    path('get_habilidades_empresa/<int:pk>/',HabilidadesXEmpresaAPIView.as_view()),
    path('get_personas_empresa_habilidades/', PersonasXHabilidadesXEmpresaAPIView.as_view()),
    path('attendance_session/', AsistenciaSesionAPIView.as_view()),
    path('attendance_session/<int:sesion_id>', AsistenciaSesionAPIView.as_view()),
    path('learning_path/search_employee/', BusquedaDeEmpleadosAPIView.as_view()),
    path('learning_path/enroll_employess/', AsignacionEmpleadoLearningPathAPIView.as_view())
]
