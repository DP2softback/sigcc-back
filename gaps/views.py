from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from zappa.asynchronous import task
from gaps.models import Competencia, TipoCompetencia, CompetenciaXAreaXPosicion, CompetenciaXEmpleado, NecesidadCapacitacion
from gaps.serializers import CompetenciaSerializer, TipoCompetenciaSerializer, CompetenciaXAreaXPosicionSerializer, CompetenciaXEmpleadoSerializer, NecesidadCapacitacionSerializer
# Create your views here.

class CompetenciaView(APIView):
    def get(self, request):
        competencias = Competencia.objects.all()
        competencias_serializer = CompetenciaSerializer(competencias,many = True)
        return Response(competencias_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request):
        competencias_serializer = CompetenciaSerializer(data = request.data, context = request.data)
        if competencias_serializer.is_valid():
            competencias_serializer.save()
            return Response(competencias_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)
    

class TipoCompetenciaView(APIView):
    def get(self, request):
        tipoCompetencias = TipoCompetencia.objects.all()
        tipoCompetencia_serializer = TipoCompetenciaSerializer(tipoCompetencias, many = True)
        return Response(tipoCompetencia_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request):
        tipoCompetencia_serializer = TipoCompetenciaSerializer(data = request.data, context = request.data)
        if tipoCompetencia_serializer.is_valid():
            tipoCompetencia_serializer.save()
            return Response(tipoCompetencia_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)
    
