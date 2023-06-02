from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password, make_password, is_password_usable
from django.db.models import Q
from django.shortcuts import render
from login.models import User
from login.serializers import *
from django.conf import settings
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from zappa.asynchronous import task
from django.core.mail import EmailMultiAlternatives, send_mail
import uuid
import logging

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

        print(request.user)
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

class Logout(APIView):
    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
    

class WhoIAmView(APIView):
    def get(self, request):

        user = request.user
        token = Token.objects.get(user = user)

        print(token)

        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': f'eres el usuario {user}',
                        },)

class PasswordRecovery(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        
        email = request.data['email']
        recovery_code = str(uuid.uuid4())[0:8]
        subject = "Recuperación de contraseña"
        message = "Tu clave de recuperación de contraseña es:\n" \
            + f"{recovery_code}"
        
        
        try:
            user = User.objects.get(email = email)
        except Exception:
            logging.info("User doesn't exists")
            return Response(status=status.HTTP_400_BAD_REQUEST,
                data={
                    'message': 'El usuario no existe',
                },) 

        user.recovery_code = recovery_code
        user.save()

        print(recovery_code)

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return Response(status=status.HTTP_200_OK,
            data={
                'message': f'Se enviará un código de recuperación al correo {email}',
            },)


class PasswordRecoveryCodeCheck(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        
        email = request.data['email']
        recovery_code = request.data['recovery_code']
        
        try:
            user = User.objects.get(email = email)
        except Exception:
            logging.info("User doesn't exists")
            return Response(status=status.HTTP_400_BAD_REQUEST,
                data={
                    'message': 'user doesnt exists',
                },) 

        if(user.recovery_code == recovery_code):
            return Response(status=status.HTTP_200_OK,
                data={
                    f'message': 'code is valid',
                },)            

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                data={
                    'message': 'wrong code',
                },)

class PasswordChangeWithoutLogin(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        
        email = request.data['email']        
        new_password = request.data['new_password']
        recovery_code = request.data['recovery_code']

        try:
            user = User.objects.get(email = email)
        except Exception:
            logging.info("User doesn't exists")
            return Response(status=status.HTTP_400_BAD_REQUEST,
                data={
                    'message': 'user doesnt exists',
                },) 

        if(user.recovery_code != recovery_code):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                data={
                    'message': 'wrong code',
                },)
      
        if(len(new_password) < 8):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                data={
                    f'message': 'new password is too short',
                },)

        else:
            encoded_password = make_password(new_password)            
            user.password = encoded_password
            user.save()

            print(check_password(new_password, user.password))

            return Response(status=status.HTTP_200_OK,
                data={
                    f'message': 'password changed',
                },)            
        

class PasswordChangeWithLogin(APIView):

    def post(self, request, format=None):

        user = request.user
                
        old_password = request.data['old_password']
        new_password = request.data['new_password']

        pwd_valid = check_password(old_password, user.password)
        
        if not pwd_valid:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'message': 'invalid password', },)      
      
        if(len(new_password) < 8):
            return Response(status=status.HTTP_400_BAD_REQUEST,
                data={
                    f'message': 'new password is too short',
                },)
            
        else:
            user.password = make_password(new_password)
            user.save()

            return Response(status=status.HTTP_200_OK,
                data={
                    f'message': 'password changed',
                },)            
        