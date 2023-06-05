from django.urls import path

from capacitaciones import views
from capacitaciones.views.views_p1 import GetUdemyValidCourses, GetUdemyCourseDetail, LearningPathAPIView, \
    CursoUdemyLpAPIView, CursoDetailLpApiView, UploadFilesInS3APIView, DeleteFilesInS3APIView, \
    BusquedaDeEmpleadosAPIView, AsignacionEmpleadoLearningPathAPIView, EmpleadosLearningPath, \
    GenerateUdemyEvaluationAPIView, CheckUdemyCourseStatusAPIView

from capacitaciones.views.views_p2 import AsistenciaSesionAPIView, AsistenciaSesionInicialAPIView, CursoEmpresaCourseAPIView, CursoEmpresaCourseFreesAllAPIView, CursoEmpresaDetailAPIView, CursoEmpresaDetailBossAPIView, \
    CursoEmpresaSearchEspecialAPIView, CursoEmpresaAPIView, EmployeeCursoEmpresaFreeListView, EmployeeCursoEmpresaNotFreeListView, ListEmployeesGeneralAPIView, SesionDetailAPIView
from capacitaciones.views.views_p3 import LearningPathCreateFromTemplateAPIView, SesionAPIView, CategoriaAPIView, \
    ProveedorEmpresaXCategoriaAPIView, HabilidadesXEmpresaAPIView, PersonasXHabilidadesXEmpresaAPIView, \
    CursoEmpresaEmpleadosAPIView, EmpleadoXLearningPathAPIView, DetalleLearningPathXEmpleadoAPIView

urlpatterns = [
    path('learning_path/<int:pk>/udemy/<str:course>/<int:delete>', GetUdemyValidCourses.as_view()),
    path('udemy/detail/', GetUdemyCourseDetail.as_view()),
    path('learning_path/', LearningPathAPIView.as_view()),
    path('learning_path/<int:pk>/course/', CursoUdemyLpAPIView.as_view()),
    path('learning_path/<int:pk_lp>/course/detail/<int:pk_curso>', CursoDetailLpApiView.as_view()),
    path('learning_path/template/', LearningPathCreateFromTemplateAPIView.as_view()),
    path('course_company/', CursoEmpresaAPIView.as_view()),
    path('course_company_course/', CursoEmpresaCourseAPIView.as_view()),
    path('course_company_course_frees_all/', CursoEmpresaCourseFreesAllAPIView.as_view()),
    path('course_company_course_free/<int:pk_empleado>', EmployeeCursoEmpresaFreeListView.as_view()),
    path('course_company_course_not_free/<int:pk_empleado>', EmployeeCursoEmpresaNotFreeListView.as_view()),
    path('course_company_course/<int:pk>', CursoEmpresaDetailAPIView.as_view()),
    path('course_company_course_boss/<int:pk>', CursoEmpresaDetailBossAPIView.as_view()),
    path('course_company_course_list_empployees/<int:curso_id>', AsistenciaSesionInicialAPIView.as_view()),
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
    path('curso_empresa_empleados/',CursoEmpresaEmpleadosAPIView.as_view()),
    path('learning_path/enroll_employess/', AsignacionEmpleadoLearningPathAPIView.as_view()),
    path('learning_path/<int:pk>/employees/', EmpleadosLearningPath.as_view()),
    path('learning_path/empleado/<int:pk>/', EmpleadoXLearningPathAPIView.as_view()),
    path('learning_path/detalle_empleado/<int:emp>/<int:lp>/', DetalleLearningPathXEmpleadoAPIView.as_view()),
    path('udemy_course/generate_evaluation/', GenerateUdemyEvaluationAPIView.as_view()),
    path('list_all_employees_general/', ListEmployeesGeneralAPIView.as_view()),
    path('udemy_course/check_status/<int:pk_course>/', CheckUdemyCourseStatusAPIView.as_view())
]
