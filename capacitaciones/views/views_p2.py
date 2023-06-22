# Create your views here.
from decimal import Decimal
from login.models import Employee
from login.serializers import EmployeeSerializerRead
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from capacitaciones.models import AsistenciaSesionXEmpleado, EmpleadoXCurso, EmpleadoXCursoEmpresa, EmpleadoXCursoXLearningPath, EmpleadoXLearningPath, LearningPath, CursoGeneralXLearningPath, CursoUdemy, Sesion, Tema
from capacitaciones.serializers import AsistenciaSesionSerializer, CursoEmpresaListSerializer, CursoGeneralListSerializer, CursoSesionTemaResponsableEmpleadoListSerializer, EmpleadoXCursoEmpresaSerializer, EmpleadoXCursoEmpresaWithCourseSerializer, EmpleadoXCursoXLearningPathProgressSerializer, EmpleadoXCursoXLearningPathSerializer, EmpleadosXLearningPathSerializer, EmployeeCoursesListSerializer, LearningPathSerializer, LearningPathSerializerWithCourses, CursoUdemySerializer, LearningPathXEmpleadoSerializer, SesionSerializer, TemaSerializer
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
        valoracion = request.data.get('valoracion',0)
        comentario_valoracion = request.data.get('comentario_valoracion')
        empleado = Employee.objects.filter(id=employee_id).first()
        learning_path= LearningPath.objects.filter(id=learning_path_id).first()
        
        try:
            empleado_learning_path= EmpleadoXLearningPath.objects.filter(empleado=empleado, learning_path= learning_path).first()
            if(empleado_learning_path):
                empleado_learning_path.porcentajeProgreso = 100
                empleado_learning_path.fechaCompletado = timezone.now()
                empleado_learning_path.valoracion = valoracion
                empleado_learning_path.comentario_valoracion = comentario_valoracion
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
                'url_foto':lp.url_foto,
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
                curso_udemy = CursoUdemy.objects.filter(id=curso_lp.curso_id).first()
                curso_empresa = CursoEmpresa.objects.filter(id=curso_lp.curso_id).first()
                datos_udemy=None
                foto_curso_empresa=None
                sesiones=[]
                if(curso_empresa is not None):
                    #Si es curso Empresa se debe listar las sesiones del curso
                    tipo_curso='E'
                    foto_curso_empresa=curso_empresa.url_foto
                    sesiones= Sesion.objects.filter(cursoEmpresa=curso_empresa)
                    sesiones_serializer = SesionSerializer(sesiones, many=True)
                    sesiones= sesiones_serializer.data
                    tipo=curso_empresa.tipo
                    datos_udemy=None
                if(curso_udemy is not None):
                    tipo_curso='U'
                    sesiones=[]
                    datos_udemy=curso_udemy.course_udemy_detail
                    tipo=None
                curso_data = {
                    'id': curso_general.id,
                    'nombre': curso_general.nombre,
                    'descripcion': curso_general.descripcion,
                    'duracion':curso_general.duracion,
                    'cant_valoraciones':curso_general.cant_valoraciones,
                    'suma_valoracionees':curso_general.suma_valoracionees,
                    'nro_orden':curso_lp.nro_orden,
                    'cant_intentos_max':curso_lp.cant_intentos_max,
                    'tipo_curso':tipo_curso,
                    'datos_udemy':datos_udemy,
                    'tipo': tipo,
                    'foto_curso_empresa':foto_curso_empresa,
                    #se va a agregar las sesiones si el curso es cursoEmpresa
                    'sesiones':sesiones,
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
    
class LearningPathFromTemplateAPIView(APIView):
    permission_classes = [AllowAny]
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request,pk):
        try:
            lp = LearningPath.objects.filter(id=pk).first()
            data = {}

            learning_path_data = {
                "nombre": lp.nombre,
                "descripcion": lp.descripcion,
                "url_foto": lp.url_foto,
                "suma_valoraciones": lp.suma_valoraciones,
                "cant_valoraciones": lp.cant_valoraciones,
                "cant_empleados": lp.cant_empleados,
                "horas_duracion": lp.horas_duracion,
                "cant_intentos_cursos_max": lp.cant_intentos_cursos_max,
                "cant_intentos_evaluacion_integral_max": lp.cant_intentos_evaluacion_integral_max,
                "estado": lp.estado,
                "cantidad_cursos": lp.cantidad_cursos,
                "rubrica":lp.rubrica
            }
            data["larning_path"]=learning_path_data
            cursos=[]

            cursos_lp= CursoGeneralXLearningPath.objects.filter(learning_path=lp)
            for curso_lp in cursos_lp:
                curso_general = CursoGeneral.objects.filter(id=curso_lp.curso_id).first()
                curso_udemy = CursoUdemy.objects.filter(id=curso_lp.curso_id).first()
                curso_empresa = CursoEmpresa.objects.filter(id=curso_lp.curso_id).first()
                if(curso_empresa is not None):
                    #Esto es cuando es curso Empresa
                    tipo_curso='E'
                    udemy_id=None
                    course_udemy_detail=None
                    estado_course_udemy=None
                    tipo=curso_empresa.tipo
                    es_libre=curso_empresa.es_libre
                    url_foto=curso_empresa.url_foto
                    fecha_creacion=curso_empresa.fecha_creacion
                    fecha_primera_sesion=curso_empresa.fecha_primera_sesion
                    fecha_ultima_sesion=curso_empresa.fecha_ultima_sesion
                    cantidad_empleados=curso_empresa.cantidad_empleados
                    cantidad_sesiones=curso_empresa.cantidad_sesiones
                else:
                    tipo_curso='U'
                    udemy_id=curso_udemy.udemy_id
                    course_udemy_detail= curso_udemy.course_udemy_detail
                    estado_course_udemy=curso_udemy.estado
                    tipo=None
                    es_libre=None
                    url_foto=None
                    fecha_creacion=None
                    fecha_primera_sesion=None
                    fecha_ultima_sesion=None
                    cantidad_empleados=None
                    cantidad_sesiones=None

                curso_data = {
                    'id': curso_general.id,
                    'nombre': curso_general.nombre,
                    'descripcion': curso_general.descripcion,
                    'duracion':curso_general.duracion,
                    'cant_valoraciones':curso_general.cant_valoraciones,
                    'suma_valoracionees':curso_general.suma_valoracionees,
                    'nro_orden':curso_lp.nro_orden,
                    'cant_intentos_max':curso_lp.cant_intentos_max,
                    'tipo_curso':tipo_curso,
                    #acá ahora sí va la partición de acuerdo al tipo_curso
                    #primero ponemos los datos que son netos de Udemy
                    'udemy_id':udemy_id,
                    'course_udemy_detail':course_udemy_detail,
                    'estado':estado_course_udemy,
                    #Ahora los datos del Empresa
                    'tipo': tipo,
                    'es_libre': es_libre,
                    'url_foto':url_foto,
                    'fecha_creacion':fecha_creacion,
                    'fecha_primera_sesion':fecha_primera_sesion,
                    'fecha_ultima_sesion':fecha_ultima_sesion,
                    'cantidad_empleados':cantidad_empleados,
                    'cantidad_sesiones':cantidad_sesiones
                }
                cursos.append(curso_data)

            data["cursos"]=cursos
            return Response(data, status = status.HTTP_200_OK)
        except:
            return Response({"message": "Upss, algó pasó"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request,pk):
        datos_lp= request.data[0]
        datos_cursos=request.data[1]

        try:
            #se crea el lp
            lp=LearningPath.objects.create(
                nombre = datos_lp['nombre'],
                descripcion= datos_lp['descripcion'],
                url_foto= datos_lp['url_foto'],
                suma_valoraciones= datos_lp['suma_valoraciones'],
                cant_valoraciones= datos_lp['cant_valoraciones'],
                cant_empleados= datos_lp['cant_empleados'],
                horas_duracion= datos_lp['horas_duracion'],
                cant_intentos_cursos_max= datos_lp['cant_intentos_cursos_max'],
                cant_intentos_evaluacion_integral_max= datos_lp['cant_intentos_evaluacion_integral_max'],
                estado= datos_lp['estado'],
                rubrica=datos_lp['rubrica']
                #Esto se quita porque cada vez que se agregue un curso se le aumenta
                #cantidad_cursos= datos_lp['cantidad_cursos']
            )
            nro_orden=1
            for curso in datos_cursos:
                curso_general = CursoGeneral.objects.filter(id=curso['id']).first()
                curso_udemy = CursoUdemy.objects.filter(id=curso['id']).first()
                curso_empresa = CursoEmpresa.objects.filter(id=curso['id']).first()
                

                if curso_general is None:
                    return Response({"message": "El Curso  no se encontró"}, status=status.HTTP_400_BAD_REQUEST)   
                
                curso_guardar = CursoGeneralXLearningPath(
                                curso=curso_general,
                                learning_path=lp,
                                nro_orden=nro_orden,
                                cant_intentos_max=curso['cant_intentos_max'],
                                porcentaje_asistencia_aprobacion= curso.get('porcentaje_asistencia_aprobacion', 100)
                            )
                curso_guardar.save()
                #Para actualizar la cantidad de cursos de un LP
                cantidad_cursos= lp.cantidad_cursos
                learning_path = LearningPath.objects.filter(id=lp.id).update(cantidad_cursos= cantidad_cursos+1)
                nro_orden=nro_orden+1
            mensaje= "Se creó el learning path con el id "+str(lp.id)
            return Response({"message": mensaje}, status = status.HTTP_200_OK)
        except:
            return Response({"message": "Ups, ocurrió un error:"}, status = status.HTTP_200_OK)
        
        
    

class CursoLPEmpleadoIncreaseStateAPIView(APIView):
    permission_classes = [AllowAny]
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request,curso_id,learning_path_id,empleado_id):
        curso_general = CursoGeneral.objects.filter(id=curso_id).first()
        learning_path = LearningPath.objects.filter(id=learning_path_id).first()
        empleado = Employee.objects.filter(id=empleado_id).first()
        empleado_curso_empres_lp = EmpleadoXCursoXLearningPath.objects.filter(empleado=empleado, curso=curso_general,learning_path=learning_path).first()
        if empleado_curso_empres_lp is not None:
            empleado_curso_empres_lp_serializer = EmpleadoXCursoXLearningPathSerializer(empleado_curso_empres_lp)
            return Response(empleado_curso_empres_lp_serializer.data, status = status.HTTP_200_OK) 
        else:
            return Response({"message": "No se encontró información con la data solicitada"}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request,curso_id,learning_path_id,empleado_id):
        curso_general = CursoGeneral.objects.filter(id=curso_id).first()
        learning_path = LearningPath.objects.filter(id=learning_path_id).first()
        empleado = Employee.objects.filter(id=empleado_id).first()

        empleado_curso_learning_path = EmpleadoXCursoXLearningPath.objects.filter(empleado=empleado, curso=curso_general, learning_path=learning_path).first()
        if empleado_curso_learning_path is not None:
            variable=empleado_curso_learning_path.estado 
            variable=int(variable)+1
            if variable==5:
                variable=4
            empleado_curso_learning_path.estado = str(variable)
            empleado_curso_learning_path.save()
            mensaje= "Se actualizó el estado del curso "+str(curso_id)+" a estado "+ str(variable)
            return Response({"message": mensaje}, status = status.HTTP_200_OK)
        return Response({"message": "En proceso aún"}, status = status.HTTP_200_OK)
    


class ListProgressEmployeesForLearningPathAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request,learning_path_id):
        empleados_learning_path = EmpleadoXLearningPath.objects.filter(learning_path_id= learning_path_id)
        cursos_emp_serializer = EmpleadosXLearningPathSerializer(empleados_learning_path, many=True)
        return Response(cursos_emp_serializer.data, status = status.HTTP_200_OK)
        

class LearningPathsForEmployeeAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request,empleado_id):
        learnings_path = EmpleadoXLearningPath.objects.filter(empleado_id= empleado_id)
        learnings_path_serializer = EmpleadosXLearningPathSerializer(learnings_path, many=True)
        return Response(learnings_path_serializer.data, status = status.HTTP_200_OK)
        
class ProgressCourseForLearningPathForEmployeesAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request,lp_id,course_id):
        curso=CursoGeneral.objects.filter(id=course_id).first()
        employees_course_learning_path = EmpleadoXCursoXLearningPath.objects.filter(learning_path_id= lp_id,curso_id=course_id)
        learnings_path_serializer = EmpleadoXCursoXLearningPathProgressSerializer(employees_course_learning_path, many=True)
        data = []
        curso_data = {
            'id': curso.id,
            'nombre': curso.nombre,
            'descripcion': curso.descripcion,
            'duracion':curso.duracion,
            'cant_valoraciones':curso.cant_valoraciones,
            'suma_valoracionees':curso.suma_valoracionees,
        }
        data.append(curso_data)
        data.append(learnings_path_serializer.data)
        return Response(data, status = status.HTTP_200_OK)
