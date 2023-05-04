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
        
        return Response(user_serializado.data,status=status.HTTP_400_BAD_REQUEST)