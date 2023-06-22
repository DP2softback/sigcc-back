# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from capacitaciones.models import CursoEmpresa, LearningPath, CursoGeneralXLearningPath, CursoUdemy, ProveedorEmpresa, \
    Habilidad, \
    ProveedorUsuario, HabilidadXProveedorUsuario, EmpleadoXCursoEmpresa, EmpleadoXLearningPath, CursoGeneral, \
    DocumentoExamen, DocumentoRespuesta, EmpleadoXCurso
from capacitaciones.serializers import CursoEmpresaSerializer, LearningPathSerializer, CursoUdemySerializer, ProveedorUsuarioSerializer, \
    SesionXReponsableSerializer, CursosEmpresaSerialiazer, EmpleadoXCursoEmpresaSerializer, \
    LearningPathSerializerWithCourses, LearningPathXEmpleadoSerializer, EmpleadoXLearningPathSerializer, \
    EmpleadosXLearningPathSerializer
from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoUdemy, Sesion, Tema, Categoria
from capacitaciones.serializers import LearningPathSerializer, CursoUdemySerializer, SesionSerializer, TemaSerializer, CategoriaSerializer, ProveedorEmpresaSerializer,HabilidadSerializer

from django.db import transaction
from rest_framework.permissions import AllowAny
from django.db.models import Q

from login.models import Employee

from datetime import datetime
from django.utils import timezone

class LearningPathCreateFromTemplateAPIView(APIView):

    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        lp_serializer = LearningPathSerializer(data=request.data,context=request.data)

        if lp_serializer.is_valid():
            lp = lp_serializer.save()

            for curso_lp in request.data['cursos']:
                print(curso_lp)
                curso_serializer = CursoUdemySerializer(data=curso_lp)

                if curso_serializer.is_valid():
                    curso = CursoUdemy.objects.filter(udemy_id=curso_lp['udemy_id']).first()
                    if curso is None:
                        curso = curso_serializer.save()

                    CursoGeneralXLearningPath.objects.create(curso=curso, learning_path=lp)
                else:
                    return Response({"message": "No se pudo crear el curso {}".format(curso_lp['nombre'])}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Se ha creado el learning path con exito"}, status=status.HTTP_200_OK)

        else:
            return Response({"message": "No se pudo crear el learning path"}, status=status.HTTP_400_BAD_REQUEST)


class CategoriaAPIView(APIView):

    def get(self, request):
        categorias = Categoria.objects.all()
        categorias_serializer = CategoriaSerializer(categorias, many=True)

        return Response(categorias_serializer.data, status = status.HTTP_200_OK)


class ProveedorEmpresaXCategoriaAPIView(APIView):

    def get(self, request, pk):
        proveedor_empresas = ProveedorEmpresa.objects.filter(categoria=pk).all()
        proveedor_serializer = ProveedorEmpresaSerializer(proveedor_empresas, many=True)

        return Response(proveedor_serializer.data, status=status.HTTP_200_OK)


class HabilidadesXEmpresaAPIView(APIView):

    def get(self, request, pk):
        usuarios = ProveedorUsuario.objects.filter(empresa=pk).all()
        habilidades_id = HabilidadXProveedorUsuario.objects.filter(proveedor_usuario__in=usuarios).values_list('habilidad_id', flat=True)
        habilidades = Habilidad.objects.filter(id__in=habilidades_id)
        habilidades_serializer = HabilidadSerializer(habilidades, many=True)

        return Response(habilidades_serializer.data, status=status.HTTP_200_OK)


class PersonasXHabilidadesXEmpresaAPIView(APIView):

    def post(self, request):
        id_proveedor = request.data.get('id_proveedor',None)
        id_habilidades = request.data.get('habilidades', None)
        usuarios_proveedor = ProveedorUsuario.objects.filter(Q(habilidad_x_proveedor_usuario__in=id_habilidades) & Q(empresa=id_proveedor)).distinct()
        usuarios_proveedor_serializer = ProveedorUsuarioSerializer(usuarios_proveedor, many=True)

        return Response(usuarios_proveedor_serializer.data, status=status.HTTP_200_OK)


class SesionAPIView(APIView):

    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        sesiones_emp = Sesion.objects.all()
        sesiones_emp_serializer = SesionSerializer(sesiones_emp, many=True)
        return Response(sesiones_emp_serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
            sesiones_emp_serializer = SesionSerializer(data=request.data, context=request.data)

            if sesiones_emp_serializer.is_valid():
                curso_empresa_id = request.data['curso_empresa_id']

                sesiones_emp = sesiones_emp_serializer.save(cursoEmpresa_id=curso_empresa_id)

                for tema_sesion in request.data['temas']:
                    print(tema_sesion)
                    tema_serializer = TemaSerializer(data=tema_sesion)

                    if tema_serializer.is_valid():
                        tema = tema_serializer.save(sesion_id=sesiones_emp.id)
                    else:
                        return Response({"message": "No se pudo crear el tema {}".format(tema_sesion['nombre'])},
                                        status=status.HTTP_400_BAD_REQUEST)
                
                # Crear responsables para cada sesión
                for responsable_data in request.data['responsables'] :
                    responsable_id = responsable_data.get('id')
                    sesion_responsable_serializer = SesionXReponsableSerializer(data={
                        'responsable': responsable_id,
                        'clase': sesiones_emp.id
                    })

                    if sesion_responsable_serializer.is_valid():
                        sesion_responsable_serializer.save()
                    else:
                        return Response({"message": "No se pudo asignar el responsable a la sesión"},
                                        status=status.HTTP_400_BAD_REQUEST)

                
                #Esto es para actualizar la fecha_primera_sesion del curso
                sesiones = Sesion.objects.filter(cursoEmpresa_id=curso_empresa_id)
                if sesiones.exists():
                    min_fecha_sesion = min(sesiones, key=lambda x: x.fecha_inicio).fecha_inicio
                    CursoEmpresa.objects.filter(id=curso_empresa_id).update(fecha_primera_sesion=min_fecha_sesion)
                    max_fecha_sesion = max(sesiones, key=lambda x: x.fecha_inicio).fecha_inicio
                    CursoEmpresa.objects.filter(id=curso_empresa_id).update(fecha_ultima_sesion=max_fecha_sesion)

                #Para actualizar la cantidad de sesiones de un curso
                cursos_emp = CursoEmpresa.objects.filter(id=curso_empresa_id).first()
                cantidad_sesiones= cursos_emp.cantidad_sesiones
                cursos_emp = CursoEmpresa.objects.filter(id=curso_empresa_id).update(cantidad_sesiones= cantidad_sesiones+1)

                return Response({'id': sesiones_emp.id,
                                'message': 'La sesion se ha con sus temas creado correctamente'},
                                status=status.HTTP_200_OK)

            return Response(sesiones_emp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#ya no va
class CursosEmpresaAPIView(APIView):

    def get(self, request, es_libre):
        cursos = CursoEmpresa.objects.filter(es_libre=es_libre).all()
        cursos_serializer = CursosEmpresaAPIView(cursos, many=True)

        return Response(cursos_serializer.data, status=status.HTTP_200_OK)


class CursoEmpresaEmpleadosAPIView(APIView):

    def post(self, request):
        id_curso = request.data.get('id_curso', None)
        tipo_curso = CursoEmpresa.objects.filter(id=id_curso).values('tipo').first()
        curso_empresa = CursoEmpresa.objects.filter(id=id_curso).first()
        cantidad_sesiones_curso=curso_empresa.cantidad_sesiones
        porcentaje_asistencia_aprobacion = request.data.get('porcentaje_asistencia_aprobacion', None)

        fecha_req = request.data.get('fecha_limite', None)
        fecha_limite = fecha_req

        empleados = request.data.get('empleados', [])
        num_empleados = len(empleados)

        if num_empleados == 0:
            return Response({'msg': 'No se recibieron empleados'}, status=status.HTTP_400_BAD_REQUEST)

        if not porcentaje_asistencia_aprobacion:
            porcentaje_asistencia_aprobacion = curso_empresa.porcentaje_asistencia_aprobacion

        if not tipo_curso:
            return Response({"message": "Curso no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        empleados_curso_empresa = [
            EmpleadoXCursoEmpresa(
                empleado_id = empleado,
                cursoEmpresa_id = id_curso,
                porcentajeProgreso = 0,
                fechaAsignacion = timezone.now(),
                fechaLimite = None if tipo_curso in ['P', 'S'] else fecha_limite,
                fechaCompletado = None,
                apreciacion = None,
                cantidad_sesiones = cantidad_sesiones_curso,
                porcentaje_asistencia_aprobacion = porcentaje_asistencia_aprobacion)
            for empleado in empleados
        ]

        EmpleadoXCursoEmpresa.objects.bulk_create(empleados_curso_empresa)

        empleado_curso_empresa_serializer = EmpleadoXCursoEmpresaSerializer(empleados_curso_empresa, many=True)

        curso_empresa.cantidad_empleados = curso_empresa.cantidad_empleados + num_empleados
        curso_empresa.save()

        return Response(empleado_curso_empresa_serializer.data, status=status.HTTP_200_OK)


class EmpleadoXLearningPathAPIView(APIView):

    def get(self, request, pk):
        empleado = Employee.objects.filter(id=pk).first()

        if not empleado:
            return Response({"message": "Empleado no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        lps = EmpleadoXLearningPath.objects.filter(empleado=pk)

        lps_serializer = EmpleadoXLearningPathSerializer(lps, many=True)

        return Response(lps_serializer.data, status=status.HTTP_200_OK)


class DetalleLearningPathXEmpleadoAPIView(APIView):

    def get(self, request, emp, lp):
        detalle_lp = EmpleadoXLearningPath.objects.filter(Q(id=emp) & Q(learning_path=lp))

        lp = LearningPath.objects.filter(id=lp).first()
        lp_serializer = LearningPathXEmpleadoSerializer(lp)

        return Response(lp_serializer.data, status=status.HTTP_200_OK)


class EmpleadosXLearningPathAPIView(APIView):

    def get(self, request, lp):

        lp = EmpleadoXLearningPath.objects.filter(learning_path=lp).all()
        empleadosXlpserializer = EmpleadosXLearningPathSerializer(lp, many=True)

        return Response(empleadosXlpserializer.data, status=status.HTTP_200_OK)


class LearningPathEvaluadoXEmpleadoAPIView(APIView):

    def get(self, request, lp, emp):
        learningpath = LearningPath.objects.filter(id=lp).first()
        data = {}

        archivo_eval = DocumentoExamen.objects.filter(learning_path=lp)

        learning_path_data = {
            "nombre": learningpath.nombre,
            "descripcion": learningpath.descripcion,
            "url_foto": learningpath.url_foto,
            "descripcion_evaluacion": learningpath.descripcion_evaluacion,
            "archivo_eval": None if not archivo_eval else archivo_eval,
            "rubrica": learningpath.rubrica
        }
        data["datos_learning_path"] = learning_path_data
        cursos = []

        cursos_lp = CursoGeneralXLearningPath.objects.filter(learning_path=lp)

        for curso_lp in cursos_lp:
            curso_general = CursoGeneral.objects.filter(id=curso_lp.curso_id).first()

            curso_data = {
                'id': curso_general.id,
                'nombre': curso_general.nombre,
                'descripcion': curso_general.descripcion,
                'nro_orden': curso_lp.nro_orden,
            }
            cursos.append(curso_data)

        data["cursos"] = cursos

        id_empXlp = EmpleadoXLearningPath.objects.filter(Q(learning_path=lp) & Q(empleado=emp)).values('id').first()
        archivo_emp = DocumentoRespuesta.objects.filter(empleado_learning_path_id=id_empXlp['id']).values('url_documento')
        data["archivo_emp"] = None if not archivo_emp else archivo_emp
        print(archivo_emp)
        return Response(data, status=status.HTTP_200_OK)


class ValorarCursoAPIView(APIView):

    def post(self, request):
        id_curso = request.data.get('curso', None)
        id_empleado = request.data.get('empleado', None)
        valoracion = request.data.get('valoracion', None)
        comentario = request.data.get('comentario', None)

        curso_asignado = EmpleadoXCurso.objects.filter(Q(curso=id_curso) & Q(empleado=id_empleado)).first()
        empleado = Employee.objects.filter(id=id_empleado).first()
        curso = CursoGeneral.objects.filter(id=id_curso).first()

        if curso_asignado:
            EmpleadoXCurso.objects.create( curso = curso, empleado=empleado, valoracion=valoracion, comentario=comentario)
            return Response({'msg': 'Se insertó con éxito'}, status=status.HTTP_200_OK)

        return Response({'msg': 'No se encontro el curso asignado a ese empleaado'}, status=status.HTTP_400_BAD_REQUEST)


class ValoracionLearningPathAPIView(APIView):

    def post(self, request):
        id_lp = request.data.get('learning_path', None)
        id_empleado = request.data.get('empleado', None)
        valoracion = request.data.get('valoracion', None)
        comentario = request.data.get('comentario', None)

        lp_asignado = EmpleadoXLearningPath.objects.filter(Q(learning_path=id_lp) & Q(empleado=id_empleado)).first()
        empleado = Employee.objects.filter(id=id_empleado).first()
        lp = LearningPath.objects.filter(id=id_lp).first()

        if lp_asignado:
            EmpleadoXLearningPath.objects.create( learning_path = lp, empleado=empleado, valoracion=valoracion, comentario_valoracion=comentario)
            return Response({'msg': 'Se insertó con éxito'}, status=status.HTTP_200_OK)

        return Response({'msg': 'No se encontro el learning path asignado a ese empleaado'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self,request,id_lp):
        lp = LearningPath.objects.filter(id=id_lp).values('nombre','descripcion','suma_valoraciones','cant_valoraciones','cant_empleados').first()

        if lp is None:
            return Response({"message": "Learning Path no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        data = {}
        data["datos_learning_path"] = lp
        valoraciones = EmpleadoXLearningPath.objects.filter(learning_path=id_lp).values('valoracion','comentario_valoracion')

        data["valoraciones"] = valoraciones

        return Response(data, status=status.HTTP_200_OK)