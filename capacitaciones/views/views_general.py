from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoGeneral, CursoUdemy, CursoEmpresa

import re
from django.db.models import Q
from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoGeneral,CursoEmpresa,CursoUdemy

from capacitaciones.serializers import LearningPathSerializer, LearningPathSerializerWithCourses, CursoUdemySerializer, CursoEmpresaSerializer
from capacitaciones.utils import get_udemy_courses, clean_course_detail



class CursoEmpresaCourseAPIView(APIView):

    def get(self, request):
        cursos_emp = CursoEmpresa.objects.all()
        cursos_emp_serializer = CursoEmpresaSerializer(cursos_emp, many=True)
        return Response(cursos_emp_serializer.data, status = status.HTTP_200_OK)

    def post(self, request):
        cursos_emp_serializer = CursoEmpresaSerializer(data = request.data, context = request.data)

        if cursos_emp_serializer.is_valid():
            cursos_emp = cursos_emp_serializer.save()
            return Response({'id': cursos_emp.id,
                            'message': 'Curso Empresa creado correctamente'}, status=status.HTTP_200_OK)

        return Response(cursos_emp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CursoEmpresaDetailAPIView(APIView):

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

