# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoUdemy, Sesion, Tema
from capacitaciones.serializers import LearningPathSerializer, LearningPathSerializerWithCourses, CursoUdemySerializer, SesionSerializer, TemaSerializer
from capacitaciones.utils import get_udemy_courses, clean_course_detail

from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoGeneral, CursoUdemy, CursoEmpresa

import re
from django.db.models import Q
from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoGeneral,CursoEmpresa,CursoUdemy

from capacitaciones.serializers import LearningPathSerializer, LearningPathSerializerWithCourses, CursoUdemySerializer, CursoEmpresaSerializer
from capacitaciones.utils import get_udemy_courses, clean_course_detail
from rest_framework.permissions import AllowAny
from django.db import transaction

class CursoEmpresaCourseAPIView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        cursos_emp = CursoEmpresa.objects.all()
        cursos_emp_serializer = CursoEmpresaSerializer(cursos_emp, many=True)
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

class SesionAPIView(APIView):
    permission_classes = [AllowAny]
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        sesiones_emp = Sesion.objects.all()
        sesiones_emp_serializer = SesionSerializer(sesiones_emp, many=True)
        return Response(sesiones_emp_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request):

        sesiones_emp_serializer = SesionSerializer(data = request.data, context = request.data)

        if sesiones_emp_serializer.is_valid():
            curso_empresa_id= request.data['curso_empresa_id']
            sesiones_emp = sesiones_emp_serializer.save(cursoEmpresa_id=curso_empresa_id)

            for tema_sesion in request.data['temas']:
                print(tema_sesion)
                tema_serializer = TemaSerializer(data=tema_sesion)

                if tema_serializer.is_valid():
                    tema_serializer.validated_data['sesion']= sesiones_emp
                    tema = Tema.objects.filter(nombre=tema_serializer.validated_data['nombre']).first()
                    if tema is None:
                        tema = tema_serializer.save()
                else:
                    return Response({"message": "No se pudo crear el tema {}".format(tema_sesion['nombre'])}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'id': sesiones_emp.id,
                            'message': 'La sesion se ha con sus temas creado correctamente'}, status=status.HTTP_200_OK)

        return Response(sesiones_emp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SesionDetailAPIView(APIView):
    permission_classes = [AllowAny]
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, pk):
        sesiones_emp = Sesion.objects.filter(id=pk).first()
        sesiones_emp_serializer = SesionSerializer(sesiones_emp)
        return Response(sesiones_emp_serializer.data, status = status.HTTP_200_OK)


#acá iría la api para la búsqueda especial de Rodrigo
class CursoEmpresaSearchEspecialAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        fecha_ini = request.GET.get('fecha_ini')
        fecha_fin = request.GET.get('fecha_fin')
        tipo = request.GET.get('tipo')

        cursos_emp = CursoEmpresa.objects.filter( Q(fecha__gte=fecha_ini) & Q(fecha__lte=fecha_fin) & Q(tipo=tipo)).first()
        cursos_emp_serializer = CursoEmpresaSerializer(cursos_emp)
        return Response(cursos_emp_serializer.data, status = status.HTTP_200_OK)

class CursoEmpresaAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        if request.GET.get('tipo')!='A':
            return Response({"message": "No es del tipo virtual asincrono"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        curso_empresa = CursoEmpresaSerializer(data=request.data)

        if curso_empresa.is_valid():
            curso_empresa_nuevo = curso_empresa.save()

            return Response ({},status=status.HTTP_200_OK)

