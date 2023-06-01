# Create your views here.
import os
import uuid

import boto3
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoUdemy, EmpleadoXLearningPath
from capacitaciones.serializers import LearningPathSerializer, LearningPathSerializerWithCourses, CursoUdemySerializer, \
    BusquedaEmployeeSerializer
from capacitaciones.utils import get_udemy_courses, clean_course_detail, get_detail_udemy_course
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

        return Response({'msg': 'Se asigno a {num_empleados} con exito'.format(num_empleados)}, status=status.HTTP_200_OK)