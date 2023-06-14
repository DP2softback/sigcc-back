# Create your views here.
from decimal import Decimal
from login.models import Employee
from login.serializers import EmployeeSerializerRead
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from capacitaciones.models import AsistenciaSesionXEmpleado, EmpleadoXCurso, EmpleadoXCursoEmpresa, EmpleadoXCursoXLearningPath, EmpleadoXLearningPath, LearningPath, CursoGeneralXLearningPath, CursoUdemy, Sesion, Tema
from capacitaciones.serializers import AsistenciaSesionSerializer, CursoEmpresaListSerializer, CursoGeneralListSerializer, CursoSesionTemaResponsableEmpleadoListSerializer, EmpleadoXCursoEmpresaSerializer, EmpleadoXCursoEmpresaWithCourseSerializer, EmpleadoXCursoXLearningPathSerializer, EmployeeCoursesListSerializer, LearningPathSerializer, LearningPathSerializerWithCourses, CursoUdemySerializer, LearningPathXEmpleadoSerializer, SesionSerializer, TemaSerializer
from capacitaciones.utils import get_udemy_courses, clean_course_detail

from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoGeneral, CursoUdemy, CursoEmpresa
from django.utils import timezone
import re
from django.db.models import Q
from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoGeneral,CursoEmpresa,CursoUdemy

from capacitaciones.serializers import LearningPathSerializer, LearningPathSerializerWithCourses, CursoUdemySerializer, CursoEmpresaSerializer
from capacitaciones.utils import get_udemy_courses, clean_course_detail
from rest_framework.permissions import AllowAny
from django.db import transaction

class CursoEmpresaCourseAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        cursos_emp = CursoEmpresa.objects.all()
        cursos_emp_serializer = CursoGeneralListSerializer(cursos_emp, many=True)
        return Response(cursos_emp_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request):
        '''
        # Genera el enlace al servidor EC2
        enlace_ec2 = f'http://tu_ec2_public_ip/media/{request.data.nombre}'
        request.data.enlace_ec2 = enlace_ec2
        '''

        cursos_emp_serializer = CursoEmpresaSerializer(data = request.data, context = request.data)

        if cursos_emp_serializer.is_valid():
            cursos_emp = cursos_emp_serializer.save()
            return Response({'id': cursos_emp.id,
                            'message': 'Curso Empresa creado correctamente'}, status=status.HTTP_200_OK)

        return Response(cursos_emp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CursoEmpresaCourseFreesAllAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        cursos_emp = CursoEmpresa.objects.filter(es_libre=True)
        cursos_emp_serializer = CursoGeneralListSerializer(cursos_emp, many=True)
        return Response(cursos_emp_serializer.data, status = status.HTTP_200_OK)
    


class CursoEmpresaDetailAPIView(APIView):
    permission_classes = [AllowAny]
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, pk):
        cursos_emp = CursoEmpresa.objects.filter(id=pk).first()
        cursos_emp_serializer = CursoEmpresaSerializer(cursos_emp)
        return Response(cursos_emp_serializer.data, status = status.HTTP_200_OK)

    def put(self, request, pk):
        cursos_emp = CursoEmpresa.objects.filter(id=pk).first()
        #this is to update a curso empresa
        cursos_emp_serializer = CursoEmpresaSerializer(cursos_emp,data = request.data,context= request.data)

        if cursos_emp_serializer.is_valid():
            cursos_emp_serializer.save()
            return Response({
                            'message': 'Se actualizó el curso empresa satisfactoriamente'}, status=status.HTTP_200_OK)
    
        return Response(cursos_emp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        cursos_emp = CursoEmpresa.objects.filter(id=pk).first()
        cursos_emp.delete()
        return Response({"message": "Curso eliminado"}, status=status.HTTP_200_OK)

class CursoEmpresaDetailBossAPIView(APIView):
    permission_classes = [AllowAny]
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, pk):
        cursos_emp = CursoEmpresa.objects.filter(id=pk).first()
        cursos_emp_serializer = CursoSesionTemaResponsableEmpleadoListSerializer(cursos_emp)
        return Response(cursos_emp_serializer.data, status = status.HTTP_200_OK)


class EmployeeCursoEmpresaFreeListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request,pk_empleado):
        empleados_cursos_empresas = EmpleadoXCursoEmpresa.objects.filter(empleado_id=pk_empleado,cursoEmpresa__es_libre=True)
        serializer = EmpleadoXCursoEmpresaWithCourseSerializer(empleados_cursos_empresas, many=True)
        return Response(serializer.data)


class EmployeeCursoEmpresaNotFreeListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request,pk_empleado):
        empleados_cursos_empresas = EmpleadoXCursoEmpresa.objects.filter(empleado_id=pk_empleado,cursoEmpresa__es_libre=False)
        serializer = EmpleadoXCursoEmpresaWithCourseSerializer(empleados_cursos_empresas, many=True)
        return Response(serializer.data)

   
class SesionDetailAPIView(APIView):
    #permission_classes = [AllowAny]
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, pk):
        curso_empresa = CursoEmpresa.objects.filter(id=pk).first()
        if not curso_empresa:
            return Response("Curso empresa no encontrado", status=status.HTTP_404_NOT_FOUND)

        sesiones_emp = Sesion.objects.filter(cursoEmpresa=curso_empresa)
        sesiones_emp_serializer = SesionSerializer(sesiones_emp, many=True)
        return Response(sesiones_emp_serializer.data, status=status.HTTP_200_OK)


#acá iría la api para la búsqueda especial de Rodrigo
class CursoEmpresaSearchEspecialAPIView(APIView):
    
    def get(self, request):
        fecha_ini = request.GET.get('fecha_ini')
        fecha_fin = request.GET.get('fecha_fin')
        tipo = request.GET.get('tipo')

        cursos_emp = CursoEmpresa.objects.filter( Q(fecha__gte=fecha_ini) & Q(fecha__lte=fecha_fin) & Q(tipo=tipo)).first()
        cursos_emp_serializer = CursoEmpresaSerializer(cursos_emp)
        return Response(cursos_emp_serializer.data, status = status.HTTP_200_OK)

class CursoEmpresaAPIView(APIView):
    
    def get(self, request):
        if request.GET.get('tipo')!='A':
            return Response({"message": "No es del tipo virtual asincrono"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        curso_empresa = CursoEmpresaSerializer(data=request.data)

        if curso_empresa.is_valid():
            curso_empresa_nuevo = curso_empresa.save()

            return Response ({},status=status.HTTP_200_OK)


class AsistenciaSesionInicialAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, curso_id):
        cursos_emp = CursoEmpresa.objects.filter(id=curso_id).first()
        cursos_emp_serializer = EmployeeCoursesListSerializer(cursos_emp)
        asistencias_data = []
        for asistencia in cursos_emp_serializer.data['empleados']:
            empleado = Employee.objects.get(id=asistencia['id'])
            empleado_data = {
                'empleado': empleado.id,
                'nombre': empleado.user.first_name + ' ' + empleado.user.last_name,
                'estado_asistencia': None
            }
            asistencias_data.append(empleado_data)

        return Response(asistencias_data, status = status.HTTP_200_OK)


class AsistenciaSesionAPIView(APIView):
    permission_classes = [AllowAny]
    
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, sesion_id):
        try:
            sesion = Sesion.objects.get(id=sesion_id)
            asistencias = AsistenciaSesionXEmpleado.objects.filter(sesion=sesion)
            serializer = AsistenciaSesionSerializer(asistencias, many=True)
            print("El data del serializer del AsistenciaSesionSerializer es:", serializer.data)
            # Obtener los datos adicionales de la sesión
            sesion_data = {
                'nombre_sesion': sesion.nombre,
                'fecha_sesion': sesion.fecha_inicio,
            }

            # Obtener los datos de las personas y su estado de asistencia
            asistencias_data = []
            for asistencia in serializer.data:
                empleado = Employee.objects.get(id=asistencia['empleado'])
                empleado_data = {
                    'empleado': empleado.id,
                    'nombre': empleado.user.first_name + ' ' + empleado.user.last_name,
                    'estado_asistencia': asistencia['estado_asistencia']
                }
                asistencias_data.append(empleado_data)

            # Combinar los datos de la sesión y las asistencias en un diccionario
            response_data = {
                'sesion': sesion_data,
                'asistencias': asistencias_data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Sesion.DoesNotExist:
            return Response({"message": "Sesión no encontrada."}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request,sesion_id):
        sesion_id = request.data['sesion_id']
        sesion = Sesion.objects.filter(id=sesion_id).first()
        curso_empresa_id = request.data['curso_empresa_id']
        curso = CursoEmpresa.objects.filter(id=curso_empresa_id).first()
        learning_path_id = request.data.get('learning_path_id', 0)
        sesion = Sesion.objects.filter(id=sesion_id).first()
        asistencias = AsistenciaSesionXEmpleado.objects.filter(sesion=sesion)
        
        for empleado_asistencia in request.data['empleados_asistencia']:
                
            #empleado_asistencia_serializer = AsistenciaSesionSerializer(data=empleado_asistencia)
            #print("El empleado_asistencia_serializer es: ",empleado_asistencia_serializer)
            empleado_id = empleado_asistencia.get('empleado')
            estado_asistencia = empleado_asistencia.get('estado_asistencia')
            # Buscar la asistencia existente por empleado y sesión
            asistencia = asistencias.filter(empleado_id=empleado_id).first()

            if empleado_id is not None and estado_asistencia is not None:
                empleado_exists = Employee.objects.filter(id=empleado_id).exists()
                if empleado_exists:
                    if asistencia:
                        # Actualizar el estado de asistencia
                        asistencia.estado_asistencia = estado_asistencia
                        asistencia.save()
                    else:
                        # Crear una nueva asistencia si no existe
                        AsistenciaSesionXEmpleado.objects.create(
                            sesion=sesion,
                            empleado_id=empleado_id,
                            estado_asistencia=estado_asistencia,
                            curso_empresa_id=curso_empresa_id
                        )

                    #Si la asistencia fue true entonces actualizamos el porcentaje de asistencia del trabajador (progreso)
                    if estado_asistencia:
                        #se diferencia si se pasó el id del LP o no
                        if learning_path_id==0:
                            #Si LP es 0, significa que el curso es libre entonces se actualiza en la tabla EmpleadoXCursoEmpresa
                            empleado_curso_empresa = EmpleadoXCursoEmpresa.objects.filter(empleado_id=empleado_id, cursoEmpresa_id=curso_empresa_id).first()
                            porcentajeProgreso=empleado_curso_empresa.porcentajeProgreso
                            cantidad_sesiones=empleado_curso_empresa.cantidad_sesiones
                            porcentajeProgreso+= Decimal(100)/cantidad_sesiones
                            empleado_curso_empresa = EmpleadoXCursoEmpresa.objects.filter(empleado_id=empleado_id, cursoEmpresa_id=curso_empresa_id).update(porcentajeProgreso= porcentajeProgreso)
                        else:
                            #Si el LP es distinto a 0 es que hay un LP asociado y que hay que actualizar en la tabla EmpleadoXCursoXLP
                            empleado_curso_learning_path = EmpleadoXCursoXLearningPath.objects.filter(empleado_id=empleado_id, curso_id=curso_empresa_id, learning_path_id=learning_path_id).first()
                            porcentajeProgreso=empleado_curso_learning_path.progreso
                            cantidad_sesiones=empleado_curso_learning_path.cantidad_sesiones
                            porcentajeProgreso+= Decimal(100)/cantidad_sesiones
                            empleado_curso_learning_path = EmpleadoXCursoXLearningPath.objects.filter(empleado_id=empleado_id, curso_id=curso_empresa_id, learning_path_id=learning_path_id).update(progreso= porcentajeProgreso)
                else:
                    # Lanzar una excepción Http404 si el empleado no existe
                    return Response(
                        {"message": "No existe el empleado con el ID proporcionado."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {"message": "Datos de asistencia incompletos."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response({'message': 'Asistencia guardada correctamente'}, status=status.HTTP_201_CREATED)    
    def put(self, request, sesion_id):
        try:            
            sesion = Sesion.objects.filter(id=sesion_id).first()
            asistencias = AsistenciaSesionXEmpleado.objects.filter(sesion=sesion)

            for empleado_asistencia in request.data['asistencias']:
                empleado_id = empleado_asistencia['empleado']
                estado_asistencia = empleado_asistencia['estado_asistencia']
                
                # Buscar la asistencia existente por empleado y sesión
                asistencia = asistencias.filter(empleado_id=empleado_id).first()

                if asistencia:
                    # Actualizar el estado de asistencia
                    asistencia.estado_asistencia = estado_asistencia
                    asistencia.save()
                else:
                    # Crear una nueva asistencia si no existe
                    AsistenciaSesionXEmpleado.objects.create(
                        sesion=sesion,
                        empleado_id=empleado_id,
                        estado_asistencia=estado_asistencia
                    )

            return Response({'message': 'Asistencia actualizada correctamente'}, status=status.HTTP_200_OK)
        except Sesion.DoesNotExist:
            return Response({"message": "Sesión no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        
class ListEmployeesGeneralAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        empleados = Employee.objects.all()
        empleados_serializer = EmployeeSerializerRead(empleados, many=True)
        return Response(empleados_serializer.data, status = status.HTTP_200_OK)


class CompletarSesionCursoEmpresaView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            empleado_id = request.data['empleado_id']
            curso_empresa_id = request.data['curso_empresa_id']
            empleado_curso_empresa = EmpleadoXCursoEmpresa.objects.filter(empleado_id=empleado_id, cursoEmpresa_id=curso_empresa_id).first()
            porcentajeProgreso=empleado_curso_empresa.porcentajeProgreso
            cantidad_sesiones=empleado_curso_empresa.cantidad_sesiones
            porcentajeProgreso+= Decimal(100)/cantidad_sesiones
            empleado_curso_empresa = EmpleadoXCursoEmpresa.objects.filter(empleado_id=empleado_id, cursoEmpresa_id=curso_empresa_id).update(porcentajeProgreso= porcentajeProgreso)
            return Response({'message': 'Se actualizó el progreso del curso'}, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'Algo pasó'}, status=status.HTTP_404_NOT_FOUND)

class CompletarCursoEmpresaView(APIView):
    permission_classes = [AllowAny]
    def put(self, request):
        employee_id = request.data.get('employee_id')
        curso_id = request.data.get('curso_id')
        learning_path_id = request.data.get('learning_path_id', 0)
        valoracion = request.data.get('valoracion')
        apreciacion = request.data.get('apreciacion')
        empleado = Employee.objects.filter(id=employee_id).first()
        curso_empresa = CursoEmpresa.objects.filter(id=curso_id).first()
        curso_general = CursoGeneral.objects.filter(id=curso_id).first()
        
        try:
            if learning_path_id == 0:
                if(curso_empresa.es_libre):
                    empleado_curso_empresa = EmpleadoXCursoEmpresa.objects.filter(empleado=empleado, cursoEmpresa=curso_empresa).first()
                    if empleado_curso_empresa is None:
                        EmpleadoXCursoEmpresa.objects.create(empleado = empleado, cursoEmpresa = curso_empresa)
                        empleado_curso_empresa = EmpleadoXCursoEmpresa.objects.filter(empleado=empleado, cursoEmpresa=curso_empresa).first()
                        
                    empleado_curso_empresa.porcentajeProgreso = 100
                    empleado_curso_empresa.fechaCompletado = timezone.now()
                    empleado_curso_empresa.apreciacion = apreciacion
                    empleado_curso_empresa.save()

                    empleado_curso = EmpleadoXCurso.objects.filter(empleado=empleado, curso=curso_general).first()
                    if(empleado_curso is None):
                        EmpleadoXCurso.objects.create(empleado = empleado, curso = curso_general,valoracion=0)
                        empleado_curso = EmpleadoXCurso.objects.filter(empleado=empleado, curso=curso_general).first()
                    
                    empleado_curso.valoracion = valoracion
                    empleado_curso.save()
                    curso_general.suma_valoracionees=curso_general.suma_valoracionees+valoracion
                    curso_general.cant_valoraciones=curso_general.cant_valoraciones+1
                    curso_general.save()
                    return Response({'message': 'Se guardó el curso como completado'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Como no se ha pasado el id del LP y el curso no es libre, no se puede asignar'}, status=status.HTTP_200_OK)
            else:
                learning_path = LearningPath.objects.filter(id=learning_path_id).first()
                empleado_curso_learning_path = EmpleadoXCursoXLearningPath.objects.filter(empleado=empleado, curso=curso_general, learning_path=learning_path).first()
                if( empleado_curso_learning_path is None):
                    EmpleadoXCursoXLearningPath.objects.create(empleado = empleado, curso = curso_general,learning_path=learning_path,estado= '0')
                    empleado_curso_learning_path = EmpleadoXCursoXLearningPath.objects.filter(empleado=empleado, curso=curso_general, learning_path=learning_path).first()
                empleado_curso_learning_path.progreso = 100
                empleado_curso_learning_path.estado = '2'
                empleado_curso_learning_path.save()

                empleado_curso = EmpleadoXCurso.objects.filter(empleado=empleado, curso=curso_general).first()
                if(empleado_curso is None):
                    EmpleadoXCurso.objects.create(empleado = empleado, curso = curso_general,valoracion=0)
                    empleado_curso = EmpleadoXCurso.objects.filter(empleado=empleado, curso=curso_general).first()

                empleado_curso.valoracion = valoracion
                empleado_curso.save()
                curso_general.suma_valoracionees=curso_general.suma_valoracionees+valoracion
                curso_general.cant_valoraciones=curso_general.cant_valoraciones+1
                curso_general.save()

                #Para actualizar el progreso del LP del empleado (EmpleadoXLearningPath)
                empleado_learning_path = EmpleadoXLearningPath.objects.filter(empleado_id=employee_id, learning_path_id= learning_path_id).first()
                cantidad_cursos_lp=empleado_learning_path.cantidad_cursos
                if cantidad_cursos_lp==0:
                    cantidad_cursos_lp=1
                progreso_actual=empleado_learning_path.porcentaje_progreso
                progreso_actual+=Decimal(100)/cantidad_cursos_lp
                empleado_learning_path = EmpleadoXLearningPath.objects.filter(empleado_id=employee_id, learning_path_id= learning_path_id).update(porcentaje_progreso= progreso_actual)

                return Response({'message': 'Se guardó el curso como completado'}, status=status.HTTP_200_OK)
        except:
            return Response({"message": "Ocurrió un error"}, status=status.HTTP_404_NOT_FOUND)
        

class CompletarLearningPathView(APIView):
    permission_classes = [AllowAny]
    def put(self, request):
        employee_id = request.data.get('employee_id')
        learning_path_id = request.data.get('learning_path_id')
        apreciacion = request.data.get('apreciacion')
        empleado = Employee.objects.filter(id=employee_id).first()
        learning_path= LearningPath.objects.filter(id=learning_path_id).first()
        
        try:
            empleado_learning_path= EmpleadoXLearningPath.objects.filter(empleado=empleado, learning_path= learning_path).first()
            if(empleado_learning_path):
                empleado_learning_path.porcentajeProgreso = 100
                empleado_learning_path.fechaCompletado = timezone.now()
                empleado_learning_path.apreciacion = apreciacion
                empleado_learning_path.estado='2'
                empleado_learning_path.save()
                return Response({'message': 'Se guardó el learning path como completado'}, status=status.HTTP_200_OK)
            return Response({'message': 'No existen los registros, pero no es un error'}, status=status.HTTP_200_OK)
        except :
            return Response({"message": "Hubo un error con la información brindada"}, status=status.HTTP_404_NOT_FOUND)
        
class CursoEmpresaAsignarLPApiView(APIView):
    permission_classes = [AllowAny]
    def post(self, request,pk):
        curso_empresa_id_passed = request.data.get('curso_id')
        
        lp = LearningPath.objects.filter(pk=pk).first()

        if lp is None:
            return Response({"message": "Learning Path no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        curso = CursoEmpresa.objects.filter(id=curso_empresa_id_passed).first()

        if curso is None:
            return Response({"message": "El Curso Empresa no se encontró"}, status=status.HTTP_400_BAD_REQUEST)   
        
        curso_guardar = CursoGeneralXLearningPath(
                        curso=curso,
                        learning_path=lp,
                        nro_orden=request.data.get('nro_orden'),
                        cant_intentos_max=request.data.get('cant_intentos_max'),
                        porcentaje_asistencia_aprobacion= request.data.get('porcentaje_asistencia_aprobacion',100)
                    )
        curso_guardar.save()
        #Para actualizar la cantidad de cursos de un LP
        cantidad_cursos= lp.cantidad_cursos
        lp = LearningPath.objects.filter(pk=pk).update(cantidad_cursos= cantidad_cursos+1)
        return Response({"message": "Curso agregado al Learning Path"}, status = status.HTTP_200_OK)

class CursoEmpresaEmpleadoProgressPApiView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        employee_id = request.data.get('employee_id')
        curso_id = request.data.get('curso_id')
        learning_path_id = request.data.get('learning_path_id', 0)
        empleado = Employee.objects.filter(id=employee_id).first()
        curso_empresa = CursoEmpresa.objects.filter(id=curso_id).first()
        curso_general = CursoGeneral.objects.filter(id=curso_id).first()
        lp = LearningPath.objects.filter(id=learning_path_id).first()
        try:
            if( learning_path_id==0):
                #Cuando es de EmpleadoXCursoEmpresa
                empleado_curso_empresa = EmpleadoXCursoEmpresa.objects.filter(empleado=empleado, cursoEmpresa=curso_empresa).first()
                empleado_curso_empresa_serializer = EmpleadoXCursoEmpresaSerializer(empleado_curso_empresa)
                return Response(empleado_curso_empresa_serializer.data, status = status.HTTP_200_OK) 
            else:
                #Cuando es de Empleado x Curso x LearningPath
                empleado_curso_empres_lp = EmpleadoXCursoXLearningPath.objects.filter(empleado=empleado, curso=curso_general,learning_path=lp).first()
                empleado_curso_empres_lp_serializer = EmpleadoXCursoXLearningPathSerializer(empleado_curso_empres_lp)
                return Response(empleado_curso_empres_lp_serializer.data, status = status.HTTP_200_OK) 
        except:
            return Response({"message": "Upss, algó pasó"}, status=status.HTTP_404_NOT_FOUND)
        

class CursoUdemyEmpleadoProgressPApiView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        employee_id = request.data.get('employee_id')
        curso_id = request.data.get('curso_id')
        learning_path_id = request.data.get('learning_path_id', 0)
        empleado = Employee.objects.filter(id=employee_id).first()
        curso_empresa = CursoEmpresa.objects.filter(id=curso_id).first()
        curso_general = CursoGeneral.objects.filter(id=curso_id).first()
        lp = LearningPath.objects.filter(id=learning_path_id).first()
        try:
            #Cuando es de Empleado x Curso x LearningPath
            empleado_curso_empres_lp = EmpleadoXCursoXLearningPath.objects.filter(empleado=empleado, curso=curso_general,learning_path=lp).first()
            empleado_curso_empres_lp_serializer = EmpleadoXCursoXLearningPathSerializer(empleado_curso_empres_lp)
            return Response(empleado_curso_empres_lp_serializer.data, status = status.HTTP_200_OK) 
        except:
            return Response({"message": "Upss, algó pasó"}, status=status.HTTP_404_NOT_FOUND)

#Probando cambio al de Gianella
class DetalleLearningPathXEmpleadoModifiedAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, emp, leap):
        empleado = Employee.objects.filter(id=emp).first()
        lp = LearningPath.objects.filter(id=leap).first()

        data = []
        if leap:
            cursos_lp= CursoGeneralXLearningPath.objects.filter(learning_path=lp)
            learning_path_data = {
                'id': lp.id,
                'nombre': lp.nombre,
                'descripcion': lp.descripcion,
                'estado':lp.estado,
                'horas_duracion':lp.horas_duracion,
                'suma_valoraciones':lp.suma_valoraciones,
                'cant_empleados': lp.cant_empleados,
                'cant_intentos_cursos_max': lp.cant_intentos_cursos_max,
                'cant_intentos_evaluacion_integral_max': lp.cant_intentos_evaluacion_integral_max,
                'cant_valoraciones': lp.cant_valoraciones,
                'cantidad_cursos': lp.cantidad_cursos,
                # Otros campos del LearningPath que deseas incluir
                'cursos': []
            }
            for curso_lp in cursos_lp:
                curso_general = CursoGeneral.objects.filter(id=curso_lp.curso_id).first()
                curso_data = {
                    'id': curso_general.id,
                    'nombre': curso_general.nombre,
                    'descripcion': curso_general.descripcion,
                    'duracion':curso_general.duracion,
                    'cant_valoraciones':curso_general.cant_valoraciones,
                    'suma_valoracionees':curso_general.suma_valoracionees,
                    'nro_orden':curso_lp.nro_orden,
                    'cant_intentos_max':curso_lp.cant_intentos_max,
                    # Otros campos del CursoGeneral que deseas incluir
                    'datos_extras': []
                }

                empleado_curso_empres_lp = EmpleadoXCursoXLearningPath.objects.filter(empleado=empleado, curso=curso_general,learning_path=lp).first()
                if empleado_curso_empres_lp is not None:
                    curso_lp_empleado={
                        'progreso':empleado_curso_empres_lp.progreso,
                        'estado':empleado_curso_empres_lp.estado,
                        'nota_final':empleado_curso_empres_lp.nota_final,
                        'cant_intentos':empleado_curso_empres_lp.cant_intentos,
                        'fecha_evaluacion':empleado_curso_empres_lp.fecha_evaluacion,
                        'ultima_evaluacion':empleado_curso_empres_lp.ultima_evaluacion,
                        'porcentajeProgreso':empleado_curso_empres_lp.porcentajeProgreso,
                        'cantidad_sesiones':empleado_curso_empres_lp.cantidad_sesiones
                    }
                    curso_data['datos_extras'].append(curso_lp_empleado)
                learning_path_data['cursos'].append(curso_data)

            data.append(learning_path_data)
            return Response(data, status=status.HTTP_200_OK)
        
        return Response({"message": "Upss, algó pasó"}, status=status.HTTP_404_NOT_FOUND)
