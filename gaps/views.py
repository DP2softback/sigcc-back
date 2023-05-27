from django.shortcuts import render
from django.db.models import Q
from rest_framework import status
from rest_framework import generics
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
            # Generador de codigo de competencia
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
            # Generador de codigo de competencia
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

class BuscarCompetenciaView(APIView):
    def get(self, request):
        idComp = request.data["idCompetencia"]
        cadena = request.data["palabraClave"]
        idTipo = request.data["idTipoCompetencia"]
        activo = request.data["activo"]
        idEmp = request.data["idEmpleado"]
        if idComp is not None and idComp > 0:
            competencia = Competencia.objects.filter(id=idComp).first()
            competencias_serializer = CompetenciaSerializer(competencia)
            return Response(competencias_serializer.data, status = status.HTTP_200_OK)
        else:
            if idEmp is not None and idEmp >0:
                query1 = Q(empleado__id = idEmp)
                query2 = Q(activo = True)
                competenciasEmpleado = CompetenciaXEmpleado.objects.filter(query1 & query2).values('competencia__codigo','competencia__nombre','competencia__tipo__nombre','nivelActual', 'nivelRequerido', 'adecuacion')
                return Response(list(competenciasEmpleado), status = status.HTTP_200_OK)
            else:
                query = Q()
                subquery1 = Q()
                subquery2 = Q()
                subquery3 = Q()
                if (cadena is not None):
                    subquery1.add(Q(nombre__contains=cadena), Q.OR)
                    subquery2.add(Q(codigo__contains=cadena), Q.OR)
                    subquery3.add(Q(tipo__nombre__contains=cadena), Q.OR)
                if(idTipo is not None and idTipo > 0):
                    query.add(Q(tipo__id=idTipo), Q.AND)
                if(activo is not None):
                    if activo == 0: query.add(Q(activo=False), Q.AND)
                    if activo == 1: query.add(Q(activo=True), Q.AND)
                competencia = Competencia.objects.filter((subquery1 | subquery2 | subquery3) & query)
                competencias_serializer = CompetenciaSerializer(competencia, many=True)
                return Response(competencias_serializer.data, status = status.HTTP_200_OK)

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
    
