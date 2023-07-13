# Create your views here.
from evaluations_and_promotions.models import CompetencessXEmployeeXLearningPath, SubCategory
from login.models import Employee, User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from capacitaciones.models import CursoEmpresa, LearningPath, CursoGeneralXLearningPath, CursoUdemy, ProveedorEmpresa, \
    Habilidad, \
    ProveedorUsuario, HabilidadXProveedorUsuario, EmpleadoXCursoEmpresa, EmpleadoXLearningPath, CursoGeneral, \
    DocumentoExamen, DocumentoRespuesta, EmpleadoXCurso, Parametros, CompetenciasXCurso, CompetenciasXLearningPath
from capacitaciones.serializers import CursoEmpresaSerializer, LearningPathSerializer, CursoUdemySerializer, \
    ProveedorUsuarioSerializer, \
    SesionXReponsableSerializer, CursosEmpresaSerialiazer, EmpleadoXCursoEmpresaSerializer, \
    LearningPathSerializerWithCourses, LearningPathXEmpleadoSerializer, EmpleadoXLearningPathSerializer, \
    EmpleadosXLearningPathSerializer, SubCategorySerializer
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
            return Response({'message': 'No se recibieron empleados'}, status=status.HTTP_400_BAD_REQUEST)

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

        archivo_eval = DocumentoExamen.objects.filter(learning_path_id=lp).values('url_documento').first()

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

    def post(self, request,id_cr):
        id_curso = id_cr
        id_empleado = request.data.get('empleado', None)
        valoracion = request.data.get('valoracion', None)
        comentario = request.data.get('comentario', None)

        curso_asignado = EmpleadoXCurso.objects.filter(Q(curso=id_curso) & Q(empleado=id_empleado)).first()
        empleado = Employee.objects.filter(id=id_empleado).first()
        curso = CursoGeneral.objects.filter(id=id_curso).first()

        if curso_asignado:
            EmpleadoXCurso.objects.create( curso = curso, empleado=empleado, valoracion=valoracion, comentario=comentario)
            curso.cant_valoraciones = curso.cant_valoraciones + valoracion
            curso.suma_valoracionees = curso.suma_valoracionees + 1

            curso.save()

            return Response({'message': 'Se insertó con éxito'}, status=status.HTTP_200_OK)

        return Response({'message': 'No se encontro el curso asignado a ese empleaado'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self,request,id_cr):

        curso = CursoGeneral.objects.filter(id=id_cr).values('nombre','descripcion','suma_valoracionees','cant_valoraciones').first()

        if curso is None:
            return Response({"message": "Curso no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        data = {}
        data["datos_curso"] = curso
        valoraciones = EmpleadoXCurso.objects.filter(curso=id_cr).values('valoracion','comentario')

        if valoraciones:
            data["valoraciones"] = [] if not valoraciones[0]['valoracion'] else valoraciones
        else:
            data["valoraciones"] = []
        return Response(data, status=status.HTTP_200_OK)


class ValoracionLearningPathAPIView(APIView):

    def post(self, request,id_lp):
        #id_lp = request.data.get('learning_path', None)
        id_empleado = request.data.get('empleado', None)
        valoracion = request.data.get('valoracion', None)
        comentario = request.data.get('comentario', None)

        lp_asignado = EmpleadoXLearningPath.objects.filter(Q(learning_path=id_lp) & Q(empleado=id_empleado)).first()
        empleado = Employee.objects.filter(id=id_empleado).first()
        lp = LearningPath.objects.filter(id=id_lp).first()

        if lp_asignado:
            EmpleadoXLearningPath.objects.create( learning_path = lp, empleado=empleado, valoracion=valoracion, comentario_valoracion=comentario)
            lp.suma_valoraciones = lp.suma_valoraciones + valoracion
            lp.cant_valoraciones = lp.cant_valoraciones + 1
            lp.cant_empleados = lp.cant_empleados + 1

            lp.save()
            return Response({'message': 'Se insertó con éxito'}, status=status.HTTP_200_OK)

        return Response({'message': 'No se encontro el learning path asignado a ese empleaado'}, status=status.HTTP_400_BAD_REQUEST)


    def get(self,request,id_lp):
        lp = LearningPath.objects.filter(id=id_lp).values('nombre','descripcion','suma_valoraciones','cant_valoraciones','cant_empleados').first()

        if lp is None:
            return Response({"message": "Learning Path no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        data = {}
        data["datos_learning_path"] = lp
        valoraciones = EmpleadoXLearningPath.objects.filter(learning_path=id_lp).values('valoracion','comentario_valoracion')
        if valoraciones:
            data["valoraciones"] = [] if not valoraciones[0]['valoracion'] else valoraciones
        else:
            data["valoraciones"] = []
        return Response(data, status=status.HTTP_200_OK)


class DetalleEvaluacionEmpleadoAPIView(APIView):

    def get(self, request, id_lp, id_user):

        id_emp = Employee.objects.filter(user_id=id_user).values('id').first()
        id_emp = id_emp['id']
        registro = EmpleadoXLearningPath.objects.filter(Q(learning_path=id_lp) & Q(empleado=id_emp)).values('id','rubrica_calificada_evaluacion','comentario_evaluacion').first()
        lp = LearningPath.objects.filter(id=id_lp).first()
        if registro:
            data = {}
            empleado = User.objects.filter(id=id_user).values('first_name', 'last_name', 'email').first()
            data['empleado']= empleado['first_name'] + " "+ empleado['last_name']
            data['rubrica_calificada']= lp.rubrica if not registro['rubrica_calificada_evaluacion'] else lp.rubrica
            data['nombre_lp'] = lp.nombre
            data['descripcion_lp'] = lp.descripcion
            data['descripcion_evaluacion']= lp.descripcion_evaluacion
            data['comentario_evaluacion']= registro['comentario_evaluacion']
            archivo_emp = DocumentoRespuesta.objects.filter(empleado_learning_path_id=registro['id']).values(
                'url_documento')
            data["archivo_emp"] = None if not archivo_emp else archivo_emp
            archivo_eval = DocumentoExamen.objects.filter(learning_path_id=id_lp).values('url_documento').first()
            data["archivo_eval"] = None if not archivo_eval else archivo_eval
            return Response(data, status=status.HTTP_200_OK)

        return Response({"message": "Registro no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, id_lp, id_emp):
        rubrica_calificada = request.data.get('rubrica_calificada', None)
        comentario_evaluacion = request.data.get('comentario_evaluacion', None)

        registro = EmpleadoXLearningPath.objects.filter(Q(learning_path=id_lp) & Q(empleado=id_emp)).first()

        if registro:
            lp = LearningPath.objects.filter(id=id_lp).first()
            empleado = Employee.objects.filter(id=id_emp).first()
            registro.rubrica_calificada_evaluacion = rubrica_calificada
            registro.comentario_evaluacion = comentario_evaluacion
            registro.save()
            #EmpleadoXLearningPath.objects.create( learning_path = lp, empleado=empleado, rubrica_calificada_evaluacion=rubrica_calificada, comentario_evaluacion=comentario_evaluacion)

            return Response({"message": "Se registró con exito"}, status=status.HTTP_200_OK)

        return Response({"message": "Registro no encontrado"}, status=status.HTTP_400_BAD_REQUEST)


class SubirDocumentoRespuestaAPIView(APIView):

    def post(self, request):
        id_lp = request.data.get('learning_path', None)
        id_emp = request.data.get('empleado', None)
        archivo_emp = request.data.get('archivo_emp', None)

        id_registro = EmpleadoXLearningPath.objects.filter(Q(learning_path=id_lp) & Q(empleado=id_emp)).values('id').first()

        if id_registro:
            doc_respuesta = DocumentoRespuesta()
            doc_respuesta.url_documento = archivo_emp
            doc_respuesta.empleado_learning_path_id = id_registro['id']

            doc_respuesta.save()

            return Response({"message": "Se guardó con exito"}, status=status.HTTP_200_OK)

        return Response({"message": "Registro no encontrado"}, status=status.HTTP_400_BAD_REQUEST)


class ValoracionesCursosAPIVIEW(APIView):

    def get(self,request,id_cr):
        curso = CursoGeneral.objects.filter(id=id_cr).values('nombre','descripcion','suma_valoraciones','cant_valoraciones').first()

        if curso is None:
            return Response({"message": "Curso no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        data = {}
        data["datos_curso"] = curso
        valoraciones = EmpleadoXCurso.objects.filter(curso=id_cr).values('valoracion','comentario')

        data["valoraciones"] = valoraciones

        return Response(data, status=status.HTTP_200_OK)


class RendirFormularioAPIVIEW(APIView):

    def get(self, request,id_curso,id_empleado):
        curso = CursoGeneral.objects.filter(id=id_curso).first()

        try:
            rpta = EmpleadoXCursoEmpresa.objects.filter(Q(empleado_id=id_empleado) & Q(curso_id=id_curso)).values("respuestas").first()
            form = CursoEmpresa.objects.filter(id=id_curso).values('preguntas').first()

        except Exception:
            rpta = EmpleadoXCurso.objects.filter(Q(empleado_id=id_empleado) & Q(curso_id=id_curso)).values("respuestas").first()
            form = CursoUdemy.objects.filter(id=id_curso).values('preguntas').first()

        if rpta == None:
            return Response({"form": form}, status=status.HTTP_200_OK)

        resultado=[]
        print(form)
        for pregunta in form['preguntas']:
            id_pregunta = pregunta["id_pregunta"]
            respuesta = rpta["respuestas"].get(str(id_pregunta))
            if respuesta is not None:
                opciones = pregunta["opciones"]
                opcion_elegida = next((opcion for opcion in opciones if opcion["id_opcion"] == respuesta), None)
                if opcion_elegida is not None:
                    resultado.append({
                        "opciones": [
                            {
                                "opcion": opcion["opcion"],
                                "id_opcion": opcion["id_opcion"],
                                "opcion_elegida": opcion["id_opcion"] == opcion_elegida["id_opcion"]
                            }
                            for opcion in opciones
                        ],
                        "pregunta": pregunta["pregunta"],
                        "id_pregunta": pregunta["id_pregunta"]
                    })

        return Response({"form": resultado}, status=status.HTTP_200_OK)

    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self,request,id_curso,id_empleado):
        print("ENTRO AL POST")
        tipo = -1
        try:
            form = CursoUdemy.objects.filter(id=id_curso).values('preguntas').first()
            tipo = 0
        except Exception:
            form = CursoEmpresa.objects.filter(id=id_curso).values('preguntas').first()
            tipo = 1
        print(form)
        print("PASO EL FORM")
        respuestas_persona = request.data.get('respuestas', None)
        puntaje = 0
        print("EMPIEZA A CALIFICAR")
        for pregunta in form['preguntas']:
            print(pregunta)
            id_pregunta = pregunta['id_pregunta']
            opciones = pregunta['opciones']

            respuesta_correcta = None

            for opcion in opciones:
                print(opcion['es_correcta'])
                if opcion['es_correcta']:
                    respuesta_correcta = opcion['id_opcion']
                    print(respuesta_correcta)
                    break

            if respuesta_correcta is not None:
                print('rpta correcta',respuesta_correcta)
                print(id_pregunta)
                print(respuestas_persona[str(id_pregunta)])
                respuesta_persona = respuestas_persona[str(id_pregunta)]

                if respuesta_persona == respuesta_correcta:
                    puntaje += 1
        aprobo = -1
        if puntaje >= 5:
            aprobo = 1
        else:
            aprobo = 0

        if tipo ==0:
            registro = EmpleadoXCurso.objects.get(Q(empleado_id=id_empleado) & Q(curso_id=id_curso))
            registro.respuestas = respuestas_persona

        elif tipo ==1:
            registro = EmpleadoXCursoEmpresa.objects.get(Q(empleado_id=id_empleado) & Q(curso_id=id_curso))
            registro.respuestas = respuestas_persona

        registro.save()

        competencias = CompetenciasXCurso.objects.filter(curso_id=id_curso).values_list('competencia', flat=True)

        for competencia in competencias:
            registro_competencia = CompetencessXEmployeeXLearningPath.objects.filter(Q(employee_id=empleado) & Q(curso_id=id_curso) & Q(competence_id=competencia))
            registro_competencia.score = 100*aprobo
            registro_competencia.save()

        return Response({"puntaje": puntaje}, status=status.HTTP_200_OK)


class RubricaAPIVIEW(APIView):

    def post(self, request,id_lp,id_empleado):
        criterias = request.data.get('criterias', None)
        registro_lp_x_emp = EmpleadoXLearningPath.objects.get(Q(empleado_id=id_empleado) & Q(learning_path_id=id_lp))
        registro_lp_x_emp.rubrica_calificada_evaluacion = criterias
        registro_lp_x_emp.save()
        for criterio in criterias:
            id_competencia = criterio['id']
            score = criterio['score']
            registro_competencia = CompetencessXEmployeeXLearningPath.objects.get(Q(employee_id=id_empleado) & Q(learning_path_id=id_lp) & Q(competence_id=id_competencia))
            registro_competencia.score = score
            registro_competencia.scale = int(score/2) - 1
            registro_competencia.save()
            return Response({"message": "Se inserto con exito"}, status=status.HTTP_200_OK)

    def get(self, request, id_lp,id_empleado):
        rubrica_calificada = EmpleadoXLearningPath.objects.filter(Q(empleado_id=id_empleado) & Q(learning_path_id=id_lp)).values('rubrica_calificada_evaluacion')

        if rubrica_calificada==None: #no la han calificado aun
            competencias_id = CompetenciasXLearningPath.objects.filter(learning_path_id=pk).values_list('competencia',flat=True)
            competencias = SubCategory.objects.filter(id__in=competencias_id)
            competencia_serializer = SubCategorySerializer(competencias, many=True)

            return Response({"criterias": competencia_serializer.data}, status=status.HTTP_200_OK)

        return Response({"criterias": rubrica_calificada}, status=status.HTTP_200_OK)
