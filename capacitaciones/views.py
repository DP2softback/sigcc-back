from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoGeneral, CursoUdemy
from capacitaciones.serializers import LearningPathSerializer, LearningPathSerializerWithCourses, CursoUdemySerializer
from capacitaciones.utils import get_udemy_courses, clean_course_detail


@api_view(['GET'])
def get_udemy_valid_courses(request, pk, course, delete=0):

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


@api_view(['POST'])
def get_udemy_course_detail(request):

    if request.method == 'POST':
        options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--disable-extensions")
        options.add_argument('--headless=new')
        options.add_argument('--disable-stack-profiler')

        browser = webdriver.Chrome(options=options)
        browser.get('https://www.udemy.com{}'.format(request.data['url']))

        togglers = WebDriverWait(driver=browser, timeout=10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'ud-accordion-panel-toggler')))

        for toggle, i in enumerate(range(1, len(togglers))):
            togglers[i].click()

        modules = WebDriverWait(driver=browser, timeout=10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[class^="accordion-panel-module--panel"]')))

        course_contents = []
        for module in modules:
            course_module = {}
            course_module['title'] = module.find_element(By.CSS_SELECTOR, '[class^="section--section-title"]').text
            topics = module.find_elements(By.CSS_SELECTOR, '[class^="section--row"]')
            course_module['topics'] = []
            for topic in topics:
                course_module['topics'].append(topic.text)
            course_contents.append(course_module)

        return Response(course_contents, status = status.HTTP_200_OK)

    return Response({"message": "Not supported method"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
def learning_path_api_view(request):

    if request.method == 'GET':
        lps = LearningPath.objects.all()
        lp_serializer = LearningPathSerializer(lps, many=True)
        return Response(lp_serializer.data, status = status.HTTP_200_OK)

    elif request.method == 'POST':
        lp_serializer = LearningPathSerializer(data = request.data, context = request.data)

        if lp_serializer.is_valid():
            lp = lp_serializer.save()
            return Response({'id': lp.id,
                            'message': 'Learning Path creado correctamente'}, status=status.HTTP_200_OK)

        return Response(lp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Not supported method"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
def curso_udemy_lp_api_vew(request, pk):

    if request.method == 'GET':
        lp = LearningPath.objects.filter(pk = pk).first()

        if lp is None:
            return Response({"message": "Learning Path no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        lp_serializer = LearningPathSerializerWithCourses(lp)

        return Response(lp_serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':

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


@api_view(['DELETE'])
def curso_detail_lp_api_view(request, pk_lp, pk_curso):

    if request.method == 'DELETE':
        curso_x_lp = CursoGeneralXLearningPath.objects.filter(curso_id = pk_curso, learning_path_id = pk_lp).first()
        if curso_x_lp:
            curso_x_lp.delete()
            return Response({"message": "Se eliminó el curso"}, status= status.HTTP_200_OK)
        return Response({"message": "No existe el curso en el learning seleccionado"}, status=status.HTTP_400_BAD_REQUEST)
