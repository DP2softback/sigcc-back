import json
from django.shortcuts import render
import sys
from rest_framework import status
import pprint
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from zappa.asynchronous import task
from rest_framework.exceptions import ValidationError
from django.db.models import Avg
from .models import Evaluation
from .serializers import *
from login.serializers import *
from datetime import datetime
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.db.models import F
from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models.aggregates import Sum,Count   
from django.db.models import F, ExpressionWrapper, FloatField
from collections import defaultdict
from rest_framework.permissions import AllowAny


def validate_employee_and_evaluation(employee_id, tipoEva):
    if not employee_id or not tipoEva:
        raise ValidationError("Employee's id and evaluationType are required")

    try:
        employee_id = int(employee_id)
        if employee_id <= 0:
            raise ValueError()
    except ValueError:
        raise ValidationError("Invalid value for employee_id.")

    if not isinstance(tipoEva, str) or not tipoEva.strip():
        raise ValidationError("Invalid value for tipoEva.")

def get_category_averages(evaluations):
    category_scores = EvaluationxSubCategory.objects.filter(evaluation__in=evaluations).values('subCategory__category__name').annotate(avg_score=Avg('score'))
    category_averages = {score['subCategory__category__name']: score['avg_score'] for score in category_scores}
    return category_averages
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
    def post(self, request):
        supervisor_id = request.data.get("id")
        evaluation_type = request.data.get("evaluationType")
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_final=request.data.get("fecha_final")

        validate_employee_and_evaluation(supervisor_id, evaluation_type)

        personas = Employee.objects.filter(supervisor=supervisor_id)
        evaluation_type_obj = get_object_or_404(EvaluationType, name=evaluation_type)
        evaluations = Evaluation.objects.filter(evaluated__in=personas, evaluationType=evaluation_type_obj, isActive=True, isFinished=True)
        employee_data = []
        category_scores = {}

        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                evaluations = evaluations.filter(evaluationDate__gte=fecha_inicio)
            except ValueError:
                return Response("Invalid value for fecha_inicio.", status=status.HTTP_400_BAD_REQUEST)

        if fecha_final:
            try:
                fecha_final = datetime.strptime(fecha_final, "%Y-%m-%d").date()
                evaluations = evaluations.filter(evaluationDate__lte=fecha_final)
            except ValueError:
                return Response("Invalid value for fecha_final.", status=status.HTTP_400_BAD_REQUEST)

        category_scores = defaultdict(list)
        category_averages = {}

        for evaluation in evaluations:
            responseQuery = EvaluationxSubCategory.objects.filter(evaluation=evaluation)
            dataSerialized = ContinuousEvaluationIntermediateSerializer(responseQuery, many=True)
            subcategories = dataSerialized.data
            for subcategory in subcategories:
                subcategory['evaluationDate'] = evaluation.evaluationDate
                # If this line is confusing, remember subcategory is a record of the EvaluationxSubCategory table
                category_id = subcategory['subCategory']['category']['name']
                score = subcategory['score']
                
                category_scores[category_id].append((score, evaluation.evaluationDate.year, evaluation.evaluationDate.month))  # Append the score, year, and month
                
        # Calculate average score for each category per year and month
        for category_id, scores in category_scores.items():
            category_averages[category_id] = {}
            year_month_scores = defaultdict(list)
            for score, year, month in scores:
                year_month_scores[(year, month)].append(score)
            for (year, month), scores in year_month_scores.items():
                average_score = sum(scores) / len(scores)
                category_averages[category_id][f"{year}-{month:02d}"] = average_score

        for persona in personas:
            # Get the latest evaluation for the specified evaluation type
            evaluation = Evaluation.objects.filter(evaluated=persona, evaluationType=evaluation_type_obj).order_by('-evaluationDate').first()
            
            # Calculate time since last evaluation
            time_since_last_evaluation = None
            dias = None
            if evaluation:
                time_since_last_evaluation = timezone.now().date() - evaluation.evaluationDate.date()
                dias = time_since_last_evaluation.days
            # Construct the desired employee data
            employee_data.append({
                'id': persona.id,
                'name': f"{persona.user.first_name} {persona.user.last_name}",
                'time_since_last_evaluation': dias,
                'area': {
                    'id': persona.area.id,
                    'name': persona.area.name
                },
                'position': {
                    'id': persona.position.id,
                    'name': persona.position.name
                },
                'email': persona.user.email
            })
            
        for employee in employee_data:
            employee['CategoryAverages'] = category_averages

        return Response(employee_data, status=status.HTTP_200_OK)
    
class GetHistoricoDeEvaluaciones(APIView):
    #permission_classes = [AllowAny]
    def post(self, request):
        #request: nivel, fecha_inicio,fecha_final, tipoEva, employee_id
        employee_id = request.data.get("employee_id")
        tipoEva = request.data.get("evaluationType")
        nivel = request.data.get("nivel")
        fecha_inicio = request.data.get("fecha_inicio")
        fecha_final=request.data.get("fecha_final")  
        print(request.data)
        pprint.pprint(request.__dict__, stream=sys.stderr)
        print("employee_id", employee_id)
        print("EvaType", tipoEva)
        validate_employee_and_evaluation(employee_id, tipoEva)
        
        
        evaType = get_object_or_404(EvaluationType, name=tipoEva)
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
            category_scores = {}
            for evaluation in evaluations:
                responseQuery = EvaluationxSubCategory.objects.filter(evaluation=evaluation)
                dataSerialized = ContinuousEvaluationIntermediateSerializer(responseQuery, many=True)
                subcategories = dataSerialized.data
                for subcategory in subcategories:
                    subcategory['evaluationDate'] = evaluation.evaluationDate
                    #If this line is confusing, remember subcategory is a record of the EvaluationxSubCategory table
                    category_id = subcategory['subCategory']['category']['name']
                    score = subcategory['score']
                    
                    if category_id not in category_scores:
                        category_scores[category_id] = [score]
                    else:
                        category_scores[category_id].append(score)

                # Calculate average score for each category
                category_averages = {}
                for category_id, scores in category_scores.items():
                    category_averages[category_id] = sum(scores) / len(scores)

                responseData.append({
                    'EvaluationId': evaluation.id,
                    'CategoryName': category_id,
                    'evaluationDate' : evaluation.evaluationDate,
                    'score': evaluation.finalScore
                })
             # Calculate average score for each category across all evaluations
            category_averages = {}
            for category_id, scores in category_scores.items():
                category_averages[category_id] = sum(scores) / len(scores)
            # Update responseData with category averages
            for data in responseData:
                data['CategoryAverages'] = category_averages
        #Desempeño
        elif evaType.name.casefold() == "Evaluación de Desempeño".casefold():
            serializedData = PerformanceEvaluationSerializer(evaluations,many=True)
            responseData= serializedData.data
            
        return Response(responseData, status=status.HTTP_200_OK)

class EvaluationAPI(APIView):
    def get(self, request):
        area = Evaluation.objects.all()
        area_serializado = EvaluationSerializerWrite(area,many=True)
        return Response(area_serializado.data,status=status.HTTP_200_OK, many=True)


    def post(self, request):
        area_serializado = EvaluationSerializerWrite(data = request.data)
        
        if area_serializado.is_valid():
            area_serializado.save()
            return Response(area_serializado.data,status=status.HTTP_200_OK)
        
        return Response(area_serializado.errors,status=status.HTTP_400_BAD_REQUEST)
    
class EvaluationXSubcatAPI(APIView):
    def post(self, request):
        
        area_serializado = EvaluationxSubCategorySerializer(data = request.data, many=True)
        
        if area_serializado.is_valid():
            area_serializado.save()
            return Response(area_serializado.data,status=status.HTTP_200_OK)
        
        return Response(area_serializado.errors,status=status.HTTP_400_BAD_REQUEST)
    
class EvaluationLineChart(APIView):
    def get(self,request):
        
        query = (
    EvaluationxSubCategory.objects
    .values(
        year=ExtractYear('evaluation__evaluationDate'),
        month=ExtractMonth('evaluation__evaluationDate'),
        categoria_nombre=F('subCategory__category__name'),
        final_score=ExpressionWrapper(Sum('score') / Count('evaluation__id'), output_field=FloatField())
        
    )
    .annotate(
        total_final_score=Sum('evaluation__finalScore')
    )
    .values('year', 'month', 'categoria_nombre', 'final_score')
)
        results = query.all() 
    
        return Response(results,status=status.HTTP_200_OK)