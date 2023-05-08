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
from django.db.models import Q
from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoGeneral,CursoEmpresa
from capacitaciones.serializers import LearningPathSerializer, LearningPathSerializerWithCourses, CursoUdemySerializer, CursoEmpresaSerializer
from capacitaciones.utils import get_udemy_courses, clean_course_detail


@api_view(['GET'])
def get_udemy_valid_courses(request, pk, course, delete=0):

    list_udemy_courses = get_udemy_courses(course)

    lp = LearningPath.objects.filter(pk = pk).first()

    if lp:
        courses_udemy_id = lp.cursogeneral_set.values_list('udemy_id', flat=True)
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

'''
@api_view(['POST'])
def get_udemy_course_detail(request):

    if request.method == 'POST':
        options = webdriver.EdgeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--disable-extensions")
        options.add_argument('--headless=new')
        options.add_argument('--disable-stack-profiler')

        browser = webdriver.Edge(options=options)
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
def curso_lp_api_vew(request, pk):

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

        curso_serializer = CursoSerializer(data=request.data)

        if curso_serializer.is_valid():

            curso = Curso.objects.filter(udemy_id=request.data['udemy_id']).first()
            if curso is None:
                curso = curso_serializer.save()

            CursoXLearningPath.objects.create(curso = curso, learning_path = lp)

            return Response({"message": "Curso agregado al Learning Path"}, status = status.HTTP_200_OK)

        return Response(curso_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def curso_detail_lp_api_view(request, pk_lp, pk_curso):

    if request.method == 'DELETE':
        curso_x_lp = CursoXLearningPath.objects.filter(curso_id = pk_curso, learning_path_id = pk_lp).first()
        if curso_x_lp:
            curso_x_lp.delete()
            return Response({"message": "Se eliminó el curso"}, status= status.HTTP_200_OK)
        return Response({"message": "No existe el curso en el learning seleccionado"}, status=status.HTTP_400_BAD_REQUEST)
'''

@api_view(['GET', 'POST'])
def curso_empresa_api_view(request):

    if request.method == 'GET':
        cursos_emp = CursoEmpresa.objects.all()
        cursos_emp_serializer = CursoEmpresaSerializer(cursos_emp, many=True)
        return Response(cursos_emp_serializer.data, status = status.HTTP_200_OK)

    elif request.method == 'POST':
        cursos_emp_serializer = CursoEmpresaSerializer(data = request.data, context = request.data)

        if cursos_emp_serializer.is_valid():
            cursos_emp = cursos_emp_serializer.save()
            return Response({'id': cursos_emp.id,
                            'message': 'Curso Empresa creado correctamente'}, status=status.HTTP_200_OK)

        return Response(cursos_emp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Not supported method"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'PUT','DELETE'])
def curso_empresa_detail_api_view(request,pk=None):

    if request.method == 'GET':
        cursos_emp = CursoEmpresa.objects.filter(id=pk).first()
        cursos_emp_serializer = CursoEmpresaSerializer(cursos_emp)
        return Response(cursos_emp_serializer.data, status = status.HTTP_200_OK)

    elif request.method == 'PUT':
        cursos_emp = CursoEmpresa.objects.filter(id=pk).first()
        #this is to update a curso empresa
        cursos_emp_serializer = CursoEmpresaSerializer(cursos_emp,data = request.data)

        if cursos_emp_serializer.is_valid():
            cursos_emp_serializer.save()
            return Response({
                            'message': 'Se actualizó el curso empresa satisfactoriamente'}, status=status.HTTP_200_OK)
    
        return Response(cursos_emp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        cursos_emp = CursoEmpresa.objects.filter(id=pk).first()
        cursos_emp.delete()
        return Response({"message": "Curso eliminado"}, status=status.HTTP_200_OK)

    return Response({"message": "Not supported method"}, status=status.HTTP_404_NOT_FOUND)

#acá iría la api para la búsqueda especial de Rodrigo
@api_view(['GET'])
def curso_empresa_search_especial_api_view(request):

    if request.method == 'GET':
        fecha_ini = request.GET.get('fecha_ini')
        fecha_fin = request.GET.get('fecha_fin')
        tipo = request.GET.get('tipo')

        cursos_emp = CursoEmpresa.objects.filter( Q(fecha__gte=fecha_ini) & Q(fecha__lte=fecha_fin) & Q(tipo=tipo)).first()
        cursos_emp_serializer = CursoEmpresaSerializer(cursos_emp)
        return Response(cursos_emp_serializer.data, status = status.HTTP_200_OK)
    return Response({"message": "Not supported method"}, status=status.HTTP_404_NOT_FOUND)
