# Create your views here.
from login.models import Employee
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from capacitaciones.models import AsistenciaSesionXEmpleado, LearningPath, CursoGeneralXLearningPath, CursoUdemy, Sesion, Tema
from capacitaciones.serializers import AsistenciaSesionSerializer, LearningPathSerializer, LearningPathSerializerWithCourses, CursoUdemySerializer, SesionSerializer, TemaSerializer
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


class AsistenciaSesionAPIView(APIView):
    permission_classes = [AllowAny]
    
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, sesion_id):
        try:
            sesion = Sesion.objects.get(id=sesion_id)
            asistencias = AsistenciaSesionXEmpleado.objects.filter(sesion=sesion)
            serializer = AsistenciaSesionSerializer(asistencias, many=True)

            # Obtener los datos adicionales de la sesión
            sesion_data = {
                'nombre_sesion': sesion.nombre,
                'fecha_sesion': sesion.fecha_inicio,
            }

            # Obtener los datos de las personas y su estado de asistencia
            asistencias_data = []
            for asistencia in serializer.data['empleados_asistencia']:
                empleado = Employee.objects.get(id=asistencia['empleado'])
                empleado_data = {
                    'id': empleado.id,
                    'nombre': empleado.user.first_name + ' ' + empleado.user.last_name,
                    'estado_asistencia': asistencia['estado_asistencia']
                }
                asistencias_data.append(empleado_data)

            # Combinar los datos de la sesión y las asistencias en un diccionario
            response_data = {
                'sesion': sesion_data,
                'asistencias': asistencias_data
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except Sesion.DoesNotExist:
            return Response({"message": "Sesión no encontrada."}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        sesion_id = request.data['sesion_id']
        sesion = Sesion.objects.filter(id=sesion_id).first()
        curso_empresa_id = request.data['curso_empresa_id']
        curso = CursoEmpresa.objects.filter(id=curso_empresa_id).first()

        for empleado_asistencia in request.data['empleados_asistencia']:
                
            empleado_asistencia_serializer = AsistenciaSesionSerializer(data=empleado_asistencia)
            empleado_asistencia_serializer.validated_data['sesion'] = sesion
            empleado_asistencia_serializer.validated_data['curso_empresa'] = curso

            if empleado_asistencia_serializer.is_valid():
                empleado_asistencia_serializer.save()
            else:
                return Response({"message": "No existe el empleado al que se le quiere poner asistencia en la sesion"},
                                    status=status.HTTP_400_BAD_REQUEST)
                
        return Response({'message': 'Asistencia guardada correctamente'}, status=status.HTTP_201_CREATED)

        
