# Create your views here.
import json
import os
import time
import uuid

import boto3
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from capacitaciones.jobs import updater
from capacitaciones.jobs.tasks import upload_new_course_in_queue
from capacitaciones.models import CursoGeneral, EmpleadoXCurso, EmpleadoXCursoEmpresa, EmpleadoXCursoXLearningPath, LearningPath, CursoGeneralXLearningPath, \
    CursoUdemy, EmpleadoXLearningPath, Parametros, DocumentoExamen, CompetenciasXCurso, CursoEmpresa, \
    CompetenciasXLearningPath
from capacitaciones.serializers import LearningPathSerializer, LearningPathSerializerWithCourses, CursoUdemySerializer, \
    BusquedaEmployeeSerializer, ParametrosSerializer, SubCategorySerializer
from capacitaciones.utils import get_udemy_courses, clean_course_detail, get_detail_udemy_course, get_gpt_form, \
    transform_gpt_quiz_output
from evaluations_and_promotions.models import SubCategory
from login.models import Employee


class GetUdemyValidCourses(APIView):

    def get(self, request, pk, course, delete=0):

        lp = LearningPath.objects.filter(pk = pk).first()

        if lp:

            list_udemy_courses = get_udemy_courses(course)
            cursos = lp.cursogeneral_set.all()
            courses_udemy_id = list(CursoUdemy.objects.filter(id__in=cursos.values_list('id', flat=True)).values_list('udemy_id', flat=True))

            if delete:
                valid_udemy_courses = [clean_course_detail(course) for course in list_udemy_courses if course['id'] not in courses_udemy_id]

            else:
                valid_udemy_courses = []

                for course in list_udemy_courses:
                    if course['id'] not in courses_udemy_id:
                        course['is_used'] = False
                    else:
                        course['is_used'] = True

                    course = clean_course_detail(course)
                    valid_udemy_courses.append(course)

            return Response(valid_udemy_courses, status = status.HTTP_200_OK)

        return Response({"message": "Learning Path no encontrado"}, status=status.HTTP_400_BAD_REQUEST)


class GetUdemyCourseDetail(APIView):

    def post(self, request):

        udemy_detail = get_detail_udemy_course(request.data['udemy_id'])

        list_chapters = []

        for item in udemy_detail:

            if item['_class'] == 'chapter':
                list_chapters.append(item['title'])

        return Response({'detail': list_chapters}, status = status.HTTP_200_OK)


class LearningPathAPIView(APIView):

    def get(self, request):

        lps = LearningPath.objects.all()
        lp_serializer = LearningPathSerializer(lps, many=True)

        return Response(lp_serializer.data, status = status.HTTP_200_OK)

    def post(self, request):

        lp_serializer = LearningPathSerializer(data = request.data, context = request.data)

        if lp_serializer.is_valid():

            lp = lp_serializer.save()

            return Response({'id': lp.id,
                            'message': 'Learning Path creado correctamente'}, status=status.HTTP_200_OK)

        return Response(lp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CursoUdemyLpAPIView(APIView):

    def get(self, request, pk):
        lp = LearningPath.objects.filter(pk = pk).first()

        if lp is None:
            return Response({"message": "Learning Path no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        lp_serializer = LearningPathSerializerWithCourses(lp)

        return Response(lp_serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):

        lp = LearningPath.objects.filter(pk=pk).first()

        if lp is None:
            return Response({"message": "Learning Path no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        curso_serializer = CursoUdemySerializer(data=request.data)

        if curso_serializer.is_valid():

            new_course = False
            curso = CursoUdemy.objects.filter(udemy_id=request.data['udemy_id']).first()
            if curso is None:
                curso = curso_serializer.save()
                new_course = True
                upload_new_course_in_queue(curso)

            CursoGeneralXLearningPath.objects.create(curso = curso, learning_path = lp)
            cantidad_cursos= lp.cantidad_cursos
            lp = LearningPath.objects.filter(pk=pk).update(cantidad_cursos= cantidad_cursos+1)
            return Response({"message": "Curso agregado al Learning Path",
                             "data": {
                                 "es_nuevo": new_course,
                                 "id_curso": curso.id
                             }
                             }, status = status.HTTP_200_OK)

        return Response(curso_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CursoDetailLpApiView(APIView):

    def delete(self, request, pk_lp, pk_curso):

        curso_x_lp = CursoGeneralXLearningPath.objects.filter(curso_id = pk_curso, learning_path_id = pk_lp).first()

        if curso_x_lp:
            curso_x_lp.delete()
            return Response({"message": "Se eliminó el curso"}, status= status.HTTP_200_OK)

        return Response({"message": "No existe el curso en el learning seleccionado"}, status=status.HTTP_400_BAD_REQUEST)


class UploadFilesInS3APIView(APIView):

    def post(self, request):

        obj_file = request.FILES.get('file')

        if obj_file:

            s3 = boto3.client('s3',
                              aws_access_key_id=os.getenv('aws_access_key_id'),
                              aws_secret_access_key=os.getenv('aws_secret_access_key'))

            bucket_name = 'dp2-bucket-dev'
            subfolder = 'capacitaciones'

            base_name, ext = os.path.splitext(obj_file.name)
            object_name = "{}/{}_{}{}".format(subfolder, base_name, str(uuid.uuid4()), ext)

            try:
                s3.upload_fileobj(obj_file, bucket_name, object_name)
                url_file = "https://{bucket_name}.s3.amazonaws.com/{object_name}".format(bucket_name=bucket_name, object_name=object_name)
                return Response({'url': url_file}, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'msg': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'msg': 'Archivo no recibido'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteFilesInS3APIView(APIView):

    def post(self, request):

        url = request.data.get('url')

        if url:
            s3 = boto3.client('s3',
                              aws_access_key_id=os.getenv('aws_access_key_id'),
                              aws_secret_access_key=os.getenv('aws_secret_access_key')
                              )
            bucket_name = 'dp2-bucket-dev'
            url_base = "https://{bucket_name}.s3.amazonaws.com/".format(bucket_name=bucket_name)
            obj_key = url.replace(url_base, '')

            try:
                s3.delete_object(Bucket=bucket_name, Key=obj_key)
                return Response({'msg': 'Archivo eliminado exitosamente'}, status.HTTP_200_OK)
            except Exception as e:
                return Response({'msg': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'msg': 'Url no recibida'}, status=status.HTTP_400_BAD_REQUEST)


class BusquedaDeEmpleadosAPIView(APIView):
    
    def post(self, request):

        email = request.data.get('email', None)

        if not email:
            return Response({'msg': 'Correo electronico no recibido'}, status=status.HTTP_400_BAD_REQUEST)

        employee = Employee.objects.filter(user__email = email).select_related('user').first()

        if not employee:
            return Response({'msg': 'Correo electronico no existente'}, status=status.HTTP_400_BAD_REQUEST)

        employee_serializer = BusquedaEmployeeSerializer(employee)

        return Response(employee_serializer.data, status=status.HTTP_200_OK)


class AsignacionEmpleadoLearningPathAPIView(APIView):
    permission_classes = [AllowAny]
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):

        empleados = request.data.get('empleados', [])
        num_empleados = len(empleados)

        if num_empleados == 0:
            return Response({'msg': 'No se recibieron empleados'}, status=status.HTTP_400_BAD_REQUEST)

        id_lp = request.data.get('id_lp', None)

        if not id_lp:
            return Response({'msg': 'No se recibió el LP'}, status=status.HTTP_400_BAD_REQUEST)

        #fecha_limite = request.data.get('fecha_limite', None)

        #if not fecha_limite:
        #    return Response({'msg': 'No se recibió la fecha limite'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lp = LearningPath.objects.filter(id=id_lp).first()
            cant_curso=lp.cantidad_cursos
            list_asignaciones = [
                EmpleadoXLearningPath(learning_path_id=id_lp, empleado_id=emp['id'], estado='0', fecha_asignacion=timezone.now(),
                                    fecha_limite=emp['fecha_limite'],cantidad_cursos=cant_curso) for emp in empleados
            ]
            EmpleadoXLearningPath.objects.bulk_create(list_asignaciones)
            lp = LearningPath.objects.filter(id=id_lp).first()
            cursos_lp= CursoGeneralXLearningPath.objects.filter(learning_path_id=id_lp)
            print("Los cursos del LP son: ",cursos_lp)
            for emp in empleados:
                print("En el bucle del trabajador: ",emp)
                for curso_lp in cursos_lp:
                        print("En el bucle del curso: ",curso_lp.curso_id)
                        empleado = Employee.objects.filter(id=emp['id']).first()
                        curso_general = CursoGeneral.objects.filter(id=curso_lp.curso_id).first()
                        curso_udemy = CursoUdemy.objects.filter(id=curso_lp.curso_id).first()
                        curso_empresa = CursoEmpresa.objects.filter(id=curso_lp.curso_id).first()
                        #Vemos si el empelado ya ha completado ese curso antes:
                        empleado_curso_anteriores= EmpleadoXCursoXLearningPath.objects.filter(curso=curso_general,empleado=empleado)
                        print("Los empleadosxcursoxlearningpath son: ",empleado_curso_anteriores)
                        #creamos una variable aparte:
                        estado_curso='0'
                        for curso_anterior in empleado_curso_anteriores:
                            if curso_anterior.estado=='3':
                                estado_curso='3'
                                progreso=curso_anterior.progreso
                                nota_final=curso_anterior.nota_final
                                cant_intentos= curso_anterior.cant_intentos
                                fecha_evaluacion= curso_anterior.fecha_evaluacion
                                ultima_evaluacion=curso_anterior.ultima_evaluacion
                                porcentajeProgreso=curso_anterior.porcentajeProgreso
                                cantidad_sesiones=curso_anterior.cantidad_sesiones

                        print("El estado a guardar del curso es: ",estado_curso)
                        if estado_curso == '0':
                            curso_empleado_lp_guardar = EmpleadoXCursoXLearningPath(
                                empleado=empleado,
                                curso=curso_general,
                                learning_path=lp,
                                estado=estado_curso
                            )

                        if estado_curso == '3':
                            curso_empleado_lp_guardar = EmpleadoXCursoXLearningPath(
                                empleado=empleado,
                                curso=curso_general,
                                learning_path=lp,
                                estado=estado_curso,
                                progreso= progreso,
                                nota_final=nota_final,
                                cant_intentos=cant_intentos,
                                fecha_evaluacion=fecha_evaluacion,
                                ultima_evaluacion=ultima_evaluacion,
                                porcentajeProgreso=porcentajeProgreso,
                                cantidad_sesiones= cantidad_sesiones
                            )
                        
                        curso_empleado_lp_guardar.save()
                        if(curso_empresa is not None):
                            #esto es si es curso Empresa
                            empleado_cursoempresa_anteriores= EmpleadoXCursoEmpresa.objects.filter(cursoEmpresa=curso_empresa,empleado=empleado).first()
                            if empleado_cursoempresa_anteriores is None:
                                empleado_curso_empresa_guardar = EmpleadoXCursoEmpresa(
                                    empleado=empleado,
                                    cursoEmpresa=curso_empresa,
                                    cantidad_sesiones= curso_empresa.cantidad_sesiones,
                                    fechaAsignacion= timezone.now()
                                )
                                empleado_curso_empresa_guardar.save()
                        else:
                            #esto es si es curso Udemy
                            empleado_cursoudemy_anteriores= EmpleadoXCurso.objects.filter(curso=curso_general,empleado=empleado).first()
                            if empleado_cursoudemy_anteriores is None:
                                empleado_curso_guardar = EmpleadoXCurso(
                                    empleado=empleado,
                                    curso=curso_general
                                )
                                empleado_curso_guardar.save()
                            

            cantidad_empleados_nuevo=len(empleados)
            cantidad_empleados_nuevo=cantidad_empleados_nuevo+lp.cant_empleados
            LearningPath.objects.filter(id=id_lp).update(cant_empleados=cantidad_empleados_nuevo)
        except Exception as e:
            return Response({'msg': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({'msg': 'Se asigno a {} con exito'.format(num_empleados)}, status=status.HTTP_200_OK)


class EmpleadosLearningPath(APIView):

    def get(self, request, pk):

        list_empleados_id = EmpleadoXLearningPath.objects.filter(learning_path_id=pk).values_list('empleado_id', flat=True)

        list_empleados = Employee.objects.filter(id__in=list(list_empleados_id)).select_related('user')

        employee_serializer = BusquedaEmployeeSerializer(list_empleados, many=True)

        return Response(employee_serializer.data, status=status.HTTP_200_OK)


class GenerateUdemyEvaluationAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        id_course = request.data.get('id_course', None)

        if not id_course:
            return Response({'msg': 'No se recibió el nombre del curso'}, status=status.HTTP_400_BAD_REQUEST)

        course_detail = CursoUdemy.objects.filter(pk=id_course).values('course_udemy_detail').first()
        course_name = course_detail['course_udemy_detail']['title'] + ' ' + course_detail['course_udemy_detail']['headline']

        try:
            udemy_form = get_gpt_form(course_name)
        except Exception as e:
            CursoUdemy.objects.filter(pk=id_course).update(estado='2')
            return Response({'msg': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        CursoUdemy.objects.filter(pk=id_course).update(preguntas=udemy_form, estado='1')

        return Response({'msg': 'Se creó la evaluacion con exito'}, status=status.HTTP_200_OK)


class CheckUdemyCourseStatusAPIView(APIView):

    def get(self, request, pk_course):

        estado_curso = CursoUdemy.objects.filter(pk=pk_course).values('estado').first()

        if not estado_curso:
            Response({'msg': 'El curso solicitado no existe'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(estado_curso, status=status.HTTP_200_OK)


class UdemyEvaluationAPIView(APIView):

    def get(self, request, pk_course):

        cursoudemy_evaluacion = CursoUdemy.objects.filter(pk=pk_course).values('preguntas').first()

        if not cursoudemy_evaluacion:
            return Response({'msg': 'El curso solicitado no existe'}, status=status.HTTP_400_BAD_REQUEST)

        cursoudemy_evaluacion = cursoudemy_evaluacion['preguntas']

        return Response({'evaluacion': cursoudemy_evaluacion}, status=status.HTTP_200_OK)

    def post(self, request, pk_course):

        evaluacion = request.data.get('evaluacion', None)

        if not evaluacion:
            return Response({'msg': 'No se recibió ninguna evaluacion'}, status=status.HTTP_400_BAD_REQUEST)

        CursoUdemy.objects.filter(pk=pk_course).update(preguntas=evaluacion, estado='3')
        return Response({'msg': 'Se validó y actualizó el cuestionario con éxito'}, status=status.HTTP_200_OK)


class SetupScheduler(APIView):

    def get(self, request):

        updater.start()

        return Response({'msg': 'Scheduler iniciado'}, status=status.HTTP_200_OK)


class ParametrosAPIView(APIView):

    def get(self, request):

        parametros = Parametros.objects.all().first()

        if not parametros:
            return Response({'msg': 'No existe parametros establecidos'}, status=status.HTTP_200_OK)

        parametro_serializer = ParametrosSerializer(parametros)

        return Response(parametro_serializer.data, status=status.HTTP_200_OK)

'''
class RubricaLPAPIView(APIView):

    def get(self, request, pk):

        lp = LearningPath.objects.filter(pk=pk).values('rubrica').first()

        return Response({
            'rubrica': lp.rubrica
        })

    def post(self, request, pk):

        rubrica = request.data.get('rubrica', None)

        if not rubrica:
            return Response({'msg': 'No se envió una rubrica'}, status=status.HTTP_200_OK)

        LearningPath.objects.filter(pk=pk).update(rubrica=rubrica)

        return Response({
            'msg': 'Evaluacion actualizada con exito'
        })
'''

class EvaluacionLPAPIView(APIView):

    def get(self, request, pk):

        lp = LearningPath.objects.filter(pk=pk).values('rubrica', 'descripcion_evaluacion').first()

        documentos = DocumentoExamen.objects.filter(learning_path_id=pk).values_list('url_documento', flat=True)

        return Response({
            'descripcion_evaluacion': lp['descripcion_evaluacion'],
            'rubrica': lp['rubrica'],
            'documentos': documentos
        }, status=status.HTTP_200_OK)


    def post(self, request, pk):

        descripcion = request.data.get('descripcion_evaluacion', None)
        rubrica = request.data.get('rubrica', None)
        documentos = request.data.get('documentos', [])

        if not descripcion:
            return Response({'msg': 'No se envió una descripcion para la evaluacion del learning path'}, status=status.HTTP_200_OK)

        if not len(documentos)!=0:
            return Response({'msg': 'No se envió documentos'}, status=status.HTTP_200_OK)

        LearningPath.objects.filter(pk=pk).update(descripcion_evaluacion=descripcion, rubrica=rubrica)

        documentos_examen = [DocumentoExamen(learning_path_id=pk, url_documento=url) for url in documentos]

        DocumentoExamen.objects.bulk_create(documentos_examen)

        return Response({'msg': 'Evaluacion creada con exito'}, status=status.HTTP_200_OK)


class CompetencesInCoursesAPIView(APIView):

    def get(self, request, pk):

        competencias_id = CompetenciasXCurso.objects.filter(curso_id = pk).values_list('competencia', flat=True)
        competencias = SubCategory.objects.filter(id__in=competencias_id)
        competencia_serializer = SubCategorySerializer(competencias, many=True)

        return Response(competencia_serializer.data, status=status.HTTP_200_OK)


    def post(self, request, pk):

        competencias_id = request.data.get("competencias")

        if not competencias_id:
            return Response({'msg': "No se enviaron competencias"}, status=status.HTTP_400_BAD_REQUEST)

        competencias = [CompetenciasXCurso(curso_id=pk, competencia_id = i) for i in competencias_id]

        CompetenciasXCurso.objects.bulk_create(competencias)

        return Response({'msg': "Se asigno las competencias con exito"}, status=status.HTTP_200_OK)


class CursoEmpresaEvaluationAPIView(APIView):

    def get(self, request, pk):

        evaluacion = CursoEmpresa.objects.filter(pk = pk).values('preguntas').first()

        return Response(evaluacion, status=status.HTTP_200_OK)

    def post(self, request, pk):

        evaluacion = request.data.get('evaluacion')

        if not evaluacion:
            return Response({'msg': 'No se envió ninguna evaluación'}, status=status.HTTP_400_BAD_REQUEST)

        CursoEmpresa.objects.filter(pk=pk).update(preguntas=evaluacion)

        return Response({'msg': 'Se agrego la evaluacion al curso con éxito'}, status=status.HTTP_200_OK)


class CompetencesInLPAPIView(APIView):

    def get(self, request, pk):
        descripcion = LearningPath.objects.filter(id=pk).values('descripcion')
        print(descripcion)
        documentos = DocumentoExamen.objects.filter(learning_path_id=pk).values_list('url_documento',flat=True)
        competencias_id = CompetenciasXLearningPath.objects.filter(learning_path_id = pk).values_list('competencia', flat=True)
        competencias = SubCategory.objects.filter(id__in=competencias_id)
        competencia_serializer = SubCategorySerializer(competencias, many=True)
        respuesta = {}
        respuesta["descripcion_evaluacion"] = descripcion[0]['descripcion']
        respuesta["documentos"] = documentos
        respuesta["criterias"] = competencia_serializer.data

        return Response(respuesta, status=status.HTTP_200_OK)


    def post(self, request, pk):

        descripcion = request.data.get('descripcion_evaluacion', None)
        competencias_id = request.data.get("criterias")
        documentos = request.data.get('documentos', [])
        print(documentos)
        if not competencias_id:
            return Response({'msg': "No se enviaron competencias"}, status=status.HTTP_400_BAD_REQUEST)

        if not descripcion:
            return Response({'msg': 'No se envió una descripcion para la evaluacion del learning path'}, status=status.HTTP_200_OK)

        if not len(documentos)!=0:
            return Response({'msg': 'No se envió documentos'}, status=status.HTTP_200_OK)

        LearningPath.objects.filter(pk=pk).update(descripcion_evaluacion=descripcion)

        competencias = [CompetenciasXLearningPath(learning_path_id=pk, competencia_id = i['id']) for i in competencias_id]
        documentos_examen = [DocumentoExamen(learning_path_id=pk, url_documento=url) for url in documentos]

        CompetenciasXLearningPath.objects.bulk_create(competencias)
        DocumentoExamen.objects.bulk_create(documentos_examen)

        return Response({'msg': "Se asigno las competencias con exito"}, status=status.HTTP_200_OK)
