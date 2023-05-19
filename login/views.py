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
from login.serializers import *

# Create your views here.
class UsuarioView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class RoleView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    
class EmployeeView(APIView):
    def get(self, request):
        employee = Employee.objects.all()
        employee_serializado = EmployeeSerializer(employee,many=True)
        return Response(employee_serializado.data,status=status.HTTP_200_OK)

    def post(self,request):
        
        employee_serializado = EmployeeSerializer(data = request.data)

        if employee_serializado.is_valid():
            employee_serializado.save()
            return Response(employee_serializado.data,status=status.HTTP_200_OK)
        
        return Response(employee_serializado.errors,status=status.HTTP_400_BAD_REQUEST)