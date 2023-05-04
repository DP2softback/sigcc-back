from django.shortcuts import render
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from zappa.asynchronous import task
from .models import User
from login.serializers import *

# Create your views here.
class UsuarioView(APIView):
    def get(self, request):
        users = User.objects.all()
        user_serializado = UserSerializer(users,many=True)
        return Response(user_serializado.data,status=status.HTTP_200_OK)

    def post(self,request):

        user_serializado = UserSerializer(data = request.data)

        if user_serializado.is_valid():
            user_serializado.save()
            return Response(user_serializado.data,status=status.HTTP_200_OK)
        
        return Response(None,status=status.HTTP_400_BAD_REQUEST)
    
class RoleView(APIView):
    def get(self, request):
        roles = Role.objects.all()
        rol_serializado = RoleSerializer(roles,many=True)
        return Response(rol_serializado.data,status=status.HTTP_200_OK)

    def post(self,request):

        rol_serializado = RoleSerializer(data = request.data)

        if rol_serializado.is_valid():
            rol_serializado.save()
            return Response(rol_serializado.data,status=status.HTTP_200_OK)
        
        return Response(None,status=status.HTTP_400_BAD_REQUEST)
    
class EmployeeView(APIView):
    def get(self, request):
        employee = Employee.objects.all()
        employee_serializado = EmployeeSerializer(employee,many=True)
        return Response(employee_serializado.data,status=status.HTTP_200_OK)

    def post(self,request):

        employee_serializado = RoleSerializer(data = request.data)

        if employee_serializado.is_valid():
            employee_serializado.save()
            return Response(employee_serializado.data,status=status.HTTP_200_OK)
        
        return Response(None,status=status.HTTP_400_BAD_REQUEST)