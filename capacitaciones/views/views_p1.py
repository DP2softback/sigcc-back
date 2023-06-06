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

from capacitaciones.jobs import updater
from capacitaciones.jobs.tasks import upload_new_course_in_queue
from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoUdemy, EmpleadoXLearningPath
from capacitaciones.serializers import LearningPathSerializer, LearningPathSerializerWithCourses, CursoUdemySerializer, \
    BusquedaEmployeeSerializer
from capacitaciones.utils import get_udemy_courses, clean_course_detail, get_detail_udemy_course, get_gpt_form
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

            curso = CursoUdemy.objects.filter(udemy_id=request.data['udemy_id']).first()
            if curso is None:
                curso = curso_serializer.save()
                upload_new_course_in_queue(curso)

            CursoGeneralXLearningPath.objects.create(curso = curso, learning_path = lp)

            return Response({"message": "Curso agregado al Learning Path"}, status = status.HTTP_200_OK)

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


        list_asignaciones = [
            EmpleadoXLearningPath(learning_path_id=id_lp, empleado_id=emp['id'], estado='0', fecha_asignacion=timezone.now(),
                                  fecha_limite=emp['fecha_limite']) for emp in empleados
        ]

        try:
            EmpleadoXLearningPath.objects.bulk_create(list_asignaciones)
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

        cursoudemy_evaluacion = json.dumps(json.loads(cursoudemy_evaluacion['preguntas']))

        return Response({'evaluacion': json.loads(cursoudemy_evaluacion)}, status=status.HTTP_200_OK)

    def post(self, request, pk_course):

        evaluacion = request.data.get('evaluacion', None)

        if not evaluacion:
            return Response({'msg': 'No se recibió ninguna evaluacion'}, status=status.HTTP_400_BAD_REQUEST)


        evaluacion = json.dumps(evaluacion)
        #print(evaluacion)
        CursoUdemy.objects.filter(pk=pk_course).update(preguntas=evaluacion, estado='3')
        return Response({'msg': 'Se validó y actualizó el cuestionario con éxito'}, status=status.HTTP_200_OK)


class SetupScheduler(APIView):

    def get(self, request):

        updater.start()

        return Response({'msg': 'Scheduler iniciado'}, status=status.HTTP_200_OK)


