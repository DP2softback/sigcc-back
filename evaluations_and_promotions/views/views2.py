from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Area, Category, EvaluationType

class GetAreas(APIView):
    def get(self, request):
        areas = Area.objects.values('id', 'name')
        return Response(areas)

class GetCategoriasContinuas(APIView):
    def get(self, request):
        evaluation_type = EvaluationType.objects.get(name='Evaluación Continua')
        categorias = Category.objects.filter(evaluationType=evaluation_type).values('id', 'name')
        return Response(categorias)

class GetCategoriasDesempenio(APIView):
    def get(self, request):
        evaluation_type = EvaluationType.objects.get(name='Evaluación de Desempeño')
        categorias = Category.objects.filter(evaluationType=evaluation_type).values('id', 'name')
        return Response(categorias)