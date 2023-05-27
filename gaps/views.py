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
    def get(self, request,id=0):
        competencias = Competencia.objects.all()
        competencias_serializer = CompetenciaSerializer(competencias,many = True)
        return Response(competencias_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request,id=0):
        competencias_serializer = CompetenciaSerializer(data = request.data, context = request.data)
        if competencias_serializer.is_valid():
            competencias_serializer.save()
            idTipoComp = request.data["tipo"]
            tipoCompetencia = TipoCompetencia.objects.filter(id=idTipoComp).values()
            competencia = Competencia.objects.filter(id=competencias_serializer.data['id']).first()
            campos = {'codigo': tipoCompetencia[0]['abreviatura'] + str(competencias_serializer.data['id']).zfill(9)}
            competencias_serializer2 = CompetenciaSerializer(competencia, data = campos)
            if competencias_serializer2.is_valid():
                competencias_serializer2.save()
                return Response(competencias_serializer2.data,status=status.HTTP_200_OK)
            return Response(competencias_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request,id=0):
        idComp = request.data["id"]
        if request.data["tipo"] is not None:
            idTipoComp = request.data["tipo"]
            tipoCompetencia = TipoCompetencia.objects.filter(id=idTipoComp).values()
            campos = {'codigo': tipoCompetencia[0]['abreviatura'] + str(request.data["id"]).zfill(9)}
            request.data["codigo"] = campos['codigo']
        competencia = Competencia.objects.filter(id=idComp).first()
        competencias_serializer = CompetenciaSerializer(competencia, data = request.data, context = request.data)
        if competencias_serializer.is_valid():
            competencias_serializer.save()
            return Response(competencias_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id=0):
        competencia = Competencia.objects.filter(id=id).first()
        campos = {'activo': 'false'}
        competencias_serializer = CompetenciaSerializer(competencia, data = campos)
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
    
