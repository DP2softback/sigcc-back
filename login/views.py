from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.shortcuts import render
from login.models import User
from login.serializers import *
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from zappa.asynchronous import task


# Create your views here.
class UserView(generics.ListCreateAPIView):

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
            query.add(Q(user__username__contains=palabra_clave), Q.AND)
            ##query.add(Q(area__name__contains = palabra_clave),Q.OR)
            ##query.add(Q(area__name__contains = palabra_clave),Q.OR)
        if(puesto_id is not None):
            query.add(Q(position=puesto_id), Q.AND)
        if(area_id is not None):
            query.add(Q(area=area_id), Q.AND)
        if(estado is not None):
            query.add(Q(isActive=estado), Q.AND)

        employee = Employee.objects.filter(query)

        employee_serializado = EmployeeSerializerRead(employee, many=True)
        return Response(employee_serializado.data, status=status.HTTP_200_OK)

    def post(self, request):

        employee_serializado = EmployeeSerializerWrite(data=request.data)

        if employee_serializado.is_valid():
            employee_serializado.save()
            return Response(employee_serializado.data, status=status.HTTP_200_OK)

        return Response(employee_serializado.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        print(request)
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'message': 'invalid user', },)

        pwd_valid = check_password(password, user.password)
        print(pwd_valid)
        if not pwd_valid:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'message': 'invalid password', },)

        token, _ = Token.objects.get_or_create(user=user)
        print(token.key)

        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'login correcto',
                            'token': token.key,
                        },)


class WhoIAmView(APIView):
    def get(self, request):

        print((request.META.get('HTTP_AUTHORIZATION')))

        token = request.META.get('HTTP_AUTHORIZATION')[6:]

        print(token)

        user = User.objects.get(id=Token.objects.get(key=token).user_id)

        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': f'eres el usuario {user}',

                        },)
