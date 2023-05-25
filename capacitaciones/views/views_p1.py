# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoUdemy
from capacitaciones.serializers import LearningPathSerializer, LearningPathSerializerWithCourses, CursoUdemySerializer
from capacitaciones.utils import get_udemy_courses, clean_course_detail


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



        get_detail_udemy_course(course)

        return Response({}, status = status.HTTP_200_OK)


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