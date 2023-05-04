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

# Create your views here.
class UsuarioView(APIView):
    def get(self, request):
        users = User.objects.values()
        list_result = [entry for entry in users]

        response = Response(
            data={
                'title': '¡Listo!',
                'message': 'Lista de usuarios registrados:',
                'users': list_result,
                
            },
            status=status.HTTP_200_OK,
        )


        return response
