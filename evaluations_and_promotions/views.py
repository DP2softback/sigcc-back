from django.shortcuts import render
from rest_framework import status
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from zappa.asynchronous import task
from rest_framework.exceptions import ValidationError
from .models import Evaluation
from .serializers import *
from login.serializers import *
from datetime import datetime

# Create your views here.
class EvaluationView(generics.ListCreateAPIView):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    
class PositionGenericView(generics.ListCreateAPIView):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

class AreaGenericView(APIView):
    def get(self, request):
        area = Area.objects.all()
        area_serializado = AreaSerializer(area,many=True)
        return Response(area_serializado.data,status=status.HTTP_200_OK)

    def post(self,request):
        area_serializado = AreaSerializer(data = request.data)

        if area_serializado.is_valid():
            area_serializado.save()
            return Response(area_serializado.data,status=status.HTTP_200_OK)
        
        return Response(None,status=status.HTTP_400_BAD_REQUEST)

class CategoryGenericView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class EvaluationTypeGenericView(generics.ListCreateAPIView):
    queryset = EvaluationType.objects.all()
    serializer_class = EvaluationTypeSerializer

class SubCategoryTypeGenericView(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

class GetPersonasACargo(APIView):
    def get(self, request):
        supervisor_id = request.GET.get("id")
        if(supervisor_id is None):
            supervisor_id = 0
            
        personas = Employee.objects.filter(supervisor = supervisor_id)
        employee_serializado = EmployeeSerializer(personas,many=True)
        return Response(employee_serializado.data,status=status.HTTP_200_OK)
    
class GetHistoricoDeEvaluaciones(APIView):
    def get(self, request):
        #request: nivel, fecha_inicio,fecha_final, tipoEva, employee_id
        employee_id = request.data.get("employee_id")
        tipoEva = request.data.get("evaluationType")
        nivel = request.data.get("nivel")
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_final=request.data.get("fecha_final")
        if not employee_id or not tipoEva:
            raise ValidationError("Employee's id and evaluationType are required")
        try:
            employee_id = int(employee_id)
            if employee_id <= 0:
                raise ValueError()
        except ValueError:
            return Response("Invalid value for employee_id.", status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if not isinstance(tipoEva, str) or not tipoEva.strip():
                raise ValueError()

        except ValueError:
            return Response("Invalid value for tipoEva.", status=status.HTTP_400_BAD_REQUEST)
        
        evaType = EvaluationType.objects.get(name = tipoEva)
        query = Evaluation.objects.filter(evaluated_id=employee_id, evaluationType=evaType, isActive=True, isFinished=True)
        
        if nivel:
            query = query.filter(finalScore=nivel)

        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                query = query.filter(evaluationDate__gte=fecha_inicio)
            except ValueError:
                return Response("Invalid value for fecha_inicio.", status=status.HTTP_400_BAD_REQUEST)

        if fecha_final:
            try:
                fecha_final = datetime.strptime(fecha_final, "%Y-%m-%d").date()
                query = query.filter(evaluationDate__lte=fecha_final)
            except ValueError:
                return Response("Invalid value for fecha_final.", status=status.HTTP_400_BAD_REQUEST)

        evaluations = query.all()
        responseData = []
        #Continua
        if evaType.name.casefold() == "Evaluación Continua".casefold():
            for evaluation in evaluations:
                responseQuery = EvaluationxSubCategory.objects.filter(evaluation=evaluation)
                dataSerialized = ContinuousEvaluationIntermediateSerializer(responseQuery, many=True)
                subcategories = dataSerialized.data
                for subcategory in subcategories:
                    subcategory['evaluationDate'] = evaluation.evaluationDate
                responseData.append({
                    'Subcategories': subcategories,
                })
        
        #Desempeño
        elif evaType.name.casefold() == "Evaluación de Desempeño".casefold():
            serializedData = PerformanceEvaluationSerializer(evaluations,many=True)
            responseData= serializedData.data
            
        return Response(responseData, status=status.HTTP_200_OK)