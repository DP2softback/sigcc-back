from django.urls import path

from capacitaciones import views
from capacitaciones.views.views_p1 import GetUdemyValidCourses, GetUdemyCourseDetail, LearningPathAPIView, \
    CursoUdemyLpAPIView, CursoDetailLpApiView, UploadFilesInS3APIView, DeleteFilesInS3APIView, \
    BusquedaDeEmpleadosAPIView, AsignacionEmpleadoLearningPathAPIView, EmpleadosLearningPath, \
    GenerateUdemyEvaluationAPIView, CheckUdemyCourseStatusAPIView, UdemyEvaluationAPIView, SetupScheduler, \
    EvaluacionLPAPIView, CompetencesInCoursesAPIView, CursoEmpresaEvaluationAPIView

from capacitaciones.views.views_p2 import AsistenciaSesionAPIView, AsistenciaSesionInicialAPIView, CompletarCursoEmpresaView, CompletarLearningPathView, CompletarSesionCursoEmpresaView, CursoEmpresaAsignarLPApiView, CursoEmpresaCourseAPIView, CursoEmpresaCourseFreesAllAPIView, CursoEmpresaDetailAPIView, CursoEmpresaDetailBossAPIView, CursoEmpresaEmpleadoProgressPApiView, \
    CursoEmpresaSearchEspecialAPIView, CursoEmpresaAPIView, CursoLPEmpleadoIncreaseStateAPIView, CursoUdemyEmpleadoProgressPApiView, DetalleLearningPathXEmpleadoModifiedAPIView, EmployeeCursoEmpresaFreeListView, EmployeeCursoEmpresaNotFreeListView, GenerateCourseEmpresaEvaluationAPIView, LearningPathFromTemplateAPIView, LearningPathsForEmployeeAPIView, ListEmployeesGeneralAPIView, ListProgressEmployeesForLearningPathAPIView, ProgressCourseForLearningPathForEmployeesAPIView, SesionDetailAPIView
from capacitaciones.views.views_p3 import LearningPathCreateFromTemplateAPIView, SesionAPIView, CategoriaAPIView, \
    ProveedorEmpresaXCategoriaAPIView, HabilidadesXEmpresaAPIView, PersonasXHabilidadesXEmpresaAPIView, \
    CursoEmpresaEmpleadosAPIView, EmpleadoXLearningPathAPIView, DetalleLearningPathXEmpleadoAPIView, \
    EmpleadosXLearningPathAPIView, LearningPathEvaluadoXEmpleadoAPIView, ValorarCursoAPIView, \
    ValoracionLearningPathAPIView, DetalleEvaluacionEmpleadoAPIView, SubirDocumentoRespuestaAPIView

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
    path('course_company_assgine_lp/<int:pk>', CursoEmpresaAsignarLPApiView.as_view()),
    path('course_complete/', CompletarCursoEmpresaView.as_view()),
    path('learning_path_complete/', CompletarLearningPathView.as_view()),
    path('sesion_course_company/', SesionAPIView.as_view()),
    path('sesion_course_company/<int:pk>', SesionDetailAPIView.as_view()),
    path('sesion_course_company_complete/', CompletarSesionCursoEmpresaView.as_view()),
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
    path('learning_path/detalle_empleado_modified/<int:emp>/<int:leap>/', DetalleLearningPathXEmpleadoModifiedAPIView.as_view()),
    path('udemy_course/generate_evaluation/', GenerateUdemyEvaluationAPIView.as_view()),
    path('empresa_course/generate_evaluation/', GenerateCourseEmpresaEvaluationAPIView.as_view()),
    path('list_all_employees_general/', ListEmployeesGeneralAPIView.as_view()),
    path('udemy_course/check_status/<int:pk_course>/', CheckUdemyCourseStatusAPIView.as_view()),
    path('udemy_course/questionary/<int:pk_course>/', UdemyEvaluationAPIView.as_view()),
    path('setup/scheduler/', SetupScheduler.as_view()),
    path('learning_path/empleados/<int:lp>/',EmpleadosXLearningPathAPIView.as_view()),
    path('course_company_employee_advance/',CursoEmpresaEmpleadoProgressPApiView.as_view()),
    path('course_udemy_employee_advance/',CursoUdemyEmpleadoProgressPApiView.as_view()),
    path('learning_path_from_template/<int:pk>/', LearningPathFromTemplateAPIView.as_view()),
    path('learning_path/<int:pk>/evaluation/', EvaluacionLPAPIView.as_view()),
    path('course_lp_employee_advance/<int:curso_id>/<int:learning_path_id>/<int:empleado_id>/', CursoLPEmpleadoIncreaseStateAPIView.as_view()),
    path('course_lp_employee_advance/', CursoLPEmpleadoIncreaseStateAPIView.as_view()),
    path('learning_path/<int:lp>/empleado/<int:emp>/evaluacion/', LearningPathEvaluadoXEmpleadoAPIView.as_view()),
    path('learning_path/empleados_progress/<int:learning_path_id>/', ListProgressEmployeesForLearningPathAPIView.as_view()),
    path('learning_path/progress_course/employees/<int:lp_id>/<int:course_id>/', ProgressCourseForLearningPathForEmployeesAPIView.as_view()),
    path('learning_path/learning_path_for_empleado/<int:empleado_id>/', LearningPathsForEmployeeAPIView.as_view()),
    path('valorar_curso/<int:id_cr>/', ValorarCursoAPIView.as_view()),
    path('valorar_learning_path/<int:id_lp>/', ValoracionLearningPathAPIView.as_view()),
    path('learning_path/<int:id_lp>/empleado/<int:id_emp>/', DetalleEvaluacionEmpleadoAPIView.as_view()),
    path('learning_path/evaluacion/', SubirDocumentoRespuestaAPIView.as_view()),
    path('curso/<int:pk>/competencias/', CompetencesInCoursesAPIView.as_view()),
    path('curso_empresa/<int:pk>/evaluacion/', CursoEmpresaEvaluationAPIView.as_view()),
    #path('learning_path/<int:pk>/rubrica/', RubricaLPAPIView.as_view())
]
