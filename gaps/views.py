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
from gaps.models import Competence, CompetenceType, CompetenceXEmployee, TrainingNeed
from gaps.serializers import CompetenceSerializer, CompetenceTypeSerializer, CompetenceXEmployeeSerializer, TrainingNeedSerializer
# Create your views here.

class CompetenceView(APIView):
    def get(self, request,id=0):
        competencias = Competence.objects.all()
        competencias_serializer = CompetenceSerializer(competencias,many = True)
        return Response(competencias_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request,id=0):
        competencias_serializer = CompetenceSerializer(data = request.data, context = request.data)
        if competencias_serializer.is_valid():
            competencias_serializer.save()
            # Generador de codigo de competencia
            idTipoComp = request.data["type"]
            tipoCompetencia = CompetenceType.objects.filter(id=idTipoComp).values()
            competencia = Competence.objects.filter(id=competencias_serializer.data['id']).first()
            campos = {'code': tipoCompetencia[0]['abbreviation'] + str(competencias_serializer.data['id']).zfill(9)}
            competencias_serializer2 = CompetenceSerializer(competencia, data = campos)
            if competencias_serializer2.is_valid():
                competencias_serializer2.save()
                return Response(competencias_serializer2.data,status=status.HTTP_200_OK)
            return Response(competencias_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request,id=0):
        idComp = request.data["id"]
        if request.data["type"] is not None:
            # Generador de codigo de competencia
            idTipoComp = request.data["type"]
            tipoCompetencia = CompetenceType.objects.filter(id=idTipoComp).values()
            campos = {'code': tipoCompetencia[0]['abbreviation'] + str(request.data["id"]).zfill(9)}
            request.data["code"] = campos['code']
        competencia = Competence.objects.filter(id=idComp).first()
        competencias_serializer = CompetenceSerializer(competencia, data = request.data, context = request.data)
        if competencias_serializer.is_valid():
            competencias_serializer.save()
            return Response(competencias_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id=0):
        competencia = Competence.objects.filter(id=id).first()
        campos = {'active': 'false'}
        competencias_serializer = CompetenceSerializer(competencia, data = campos)
        if competencias_serializer.is_valid():
            competencias_serializer.save()
            return Response(competencias_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)

class SearchCompetenceView(APIView):
    def post(self, request):
        idComp = request.data["idCompetencia"]
        cadena = request.data["palabraClave"]
        idTipo = request.data["idTipoCompetencia"]
        activo = request.data["activo"]
        idEmp = request.data["idEmpleado"]
        if idComp is not None and idComp > 0:
            competencia = Competence.objects.filter(id=idComp).first()
            competencias_serializer = CompetenceSerializer(competencia)
            return Response(competencias_serializer.data, status = status.HTTP_200_OK)
        else:
            if idEmp is not None and idEmp >0:
                query = Q(employee__id = idEmp)
                if(activo is not None):
                    if activo == 0: query.add(Q(active=False), Q.AND)
                    if activo == 1: query.add(Q(active=True), Q.AND)
                competenciasEmpleado = CompetenceXEmployee.objects.filter(query).values('competence__code','competence__name','competence__type__name','levelCurrent', 'levelRequired', 'likeness')
                return Response(list(competenciasEmpleado), status = status.HTTP_200_OK)
            else:
                query = Q()
                subquery1 = Q()
                subquery2 = Q()
                subquery3 = Q()
                if (cadena is not None):
                    subquery1.add(Q(name__contains=cadena), Q.OR)
                    subquery2.add(Q(code__contains=cadena), Q.OR)
                    subquery3.add(Q(type__name__contains=cadena), Q.OR)
                if(idTipo is not None and idTipo > 0):
                    query.add(Q(type__id=idTipo), Q.AND)
                if(activo is not None):
                    if activo == 0: query.add(Q(active=False), Q.AND)
                    if activo == 1: query.add(Q(active=True), Q.AND)
                competencia = Competence.objects.filter((subquery1 | subquery2 | subquery3) & query)
                competencias_serializer = CompetenceSerializer(competencia, many=True)
                return Response(competencias_serializer.data, status = status.HTTP_200_OK)

class SearchTrainingNeedView(APIView):
    def post(self, request):
        estado = request.data["estado"]
        tipo = request.data["tipo"]
        activo = request.data["activo"]
        idEmp = request.data["idEmpleado"]
        query = Q()
        if idEmp is not None and idEmp >0:
            query.add(Q(employee__id = idEmp), Q.AND)
        if activo is not None:
            if activo == 0: query.add(Q(active=False), Q.AND)
            if activo == 1: query.add(Q(active=True), Q.AND)
        if estado is not None and estado>0:
            query.add(Q(state = estado), Q.AND)
        if tipo is not None and tipo>0:
            query.add(Q(type = tipo), Q.AND)
        necesidadesEmpleado = TrainingNeed.objects.filter(query).values('competence__code','competence__name','competence__type__name','levelCurrent', 'levelRequired', 'levelGap', 'description', 'state', 'type')
        return Response(list(necesidadesEmpleado), status = status.HTTP_200_OK)

class CompetenceTypeView(APIView):
    def get(self, request):
        tipoCompetencias = CompetenceType.objects.all()
        tipoCompetencia_serializer = CompetenceTypeSerializer(tipoCompetencias, many = True)
        return Response(tipoCompetencia_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request):
        tipoCompetencia_serializer = CompetenceTypeSerializer(data = request.data, context = request.data)
        if tipoCompetencia_serializer.is_valid():
            tipoCompetencia_serializer.save()
            return Response(tipoCompetencia_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)
    
