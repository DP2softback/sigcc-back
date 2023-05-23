from django.shortcuts import render
from django.shortcuts import render
from rest_framework import status
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from zappa.asynchronous import task
from .models import User
from django.db.models import Q
from login.serializers import *

# Create your views here.
class UsuarioView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializerRead
    
class RoleView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializerRead
    
class EmployeeView(APIView):
    def get(self, request):

        query = Q()

        palabra_clave = request.GET.get("palabra_clave")  
        puesto_id = request.GET.get("puesto")
        area_id = request.GET.get("area")
        estado = request.GET.get("estado")

        if(palabra_clave is not None):
            query.add(Q(user__username__contains = palabra_clave),Q.AND)
            ##query.add(Q(area__name__contains = palabra_clave),Q.OR)
            ##query.add(Q(area__name__contains = palabra_clave),Q.OR)
        if(puesto_id is not None):
            query.add(Q(position=puesto_id),Q.AND)
        if(area_id is not None):
            query.add(Q(area=area_id),Q.AND)
        if(estado is not None):
            query.add(Q(isActive=estado),Q.AND)
        
        employee = Employee.objects.filter(query)

        employee_serializado = EmployeeSerializerRead(employee,many=True)
        return Response(employee_serializado.data,status=status.HTTP_200_OK)

    def post(self,request):
        
        employee_serializado = EmployeeSerializerWrite(data = request.data)

        if employee_serializado.is_valid():
            employee_serializado.save()
            return Response(employee_serializado.data,status=status.HTTP_200_OK)
        
        return Response(employee_serializado.errors,status=status.HTTP_400_BAD_REQUEST)