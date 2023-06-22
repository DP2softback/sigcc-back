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
from gaps.models import Capacity, CapacityType, CapacityXEmployee, TrainingNeed, CapacityXAreaXPosition
from login.models import Employee
from personal.models import *
from personal.serializers import *
from gaps.serializers import CapacitySerializer, CapacityTypeSerializer, CapacityXEmployeeSerializer, TrainingNeedSerializer, CapacityXAreaXPositionSerializer
from login.serializers import EmployeeSerializerRead, EmployeeSerializerWrite
from gaps.serializers import AreaSerializer
import openai as ai
ai.api_key = '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'
# Create your views here.

class CapacityView(APIView):
    def get(self, request,id=0):
        competencias = Capacity.objects.all()
        competencias_serializer = CapacitySerializer(competencias,many = True)
        return Response(competencias_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request,id=0):
        competencias_serializer = CapacitySerializer(data = request.data, context = request.data)
        print(competencias_serializer)
        if competencias_serializer.is_valid():
            competencias_serializer.save()
            # Generador de codigo de competencia
            idTipoComp = request.data["type"]
            tipoCompetencia = CapacityType.objects.filter(id=idTipoComp).values()
            competencia = Capacity.objects.filter(id=competencias_serializer.data['id']).first()
            # response = ai.Completion.create(
            #                 engine='text-davinci-003',
            #                 prompt='Dame una descripción de máximo 100 caracteres de la competencia de ' + competencias_serializer.data['name'],
            #                 max_tokens=200,)
            campos = {'code': str(tipoCompetencia[0]['abbreviation'][0:3]) + str(competencias_serializer.data['name'][0:3]).upper() + str(competencias_serializer.data['id'])
            }
            #          'description': str(response.choices[0].text.strip()).replace('\n', '')}
            competencias_serializer2 = CapacitySerializer(competencia, data = campos)
            print(competencias_serializer2)
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
            tipoCompetencia = CapacityType.objects.filter(id=idTipoComp).values()
            campos = {'code': str(tipoCompetencia[0]['abbreviation'][0:3]) + str(request.data['name'][0:3]).upper() + str(request.data['id'])}
            request.data["code"] = campos['code']
        competencia = Capacity.objects.filter(id=idComp).first()
        competencias_serializer = CapacitySerializer(competencia, data = request.data, context = request.data)
        if competencias_serializer.is_valid():
            competencias_serializer.save()
            return Response(competencias_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id=0):
        competencia = Capacity.objects.filter(id=id).first()
        campos = {'active': 'false'}
        competencias_serializer = CapacitySerializer(competencia, data = campos)
        if competencias_serializer.is_valid():
            competencias_serializer.save()
            return Response(competencias_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)

class SearchCapacityView(APIView):
    def post(self, request):
        idComp = request.data["idCompetencia"]
        cadena = request.data["palabraClave"]
        idTipo = request.data["idTipoCompetencia"]
        activo = request.data["activo"]
        idEmp = request.data["idEmpleado"]
        if idComp is not None and idComp > 0:
            competencia = Capacity.objects.filter(id=idComp).first()
            competencias_serializer = CapacitySerializer(competencia)
            return Response(competencias_serializer.data, status = status.HTTP_200_OK)
        else:
            if idEmp is not None and idEmp >0:
                query = Q(employee__id = idEmp)
                subquery1 = Q()
                subquery2 = Q()
                subquery3 = Q()
                if(activo is not None):
                    if activo == 0: query.add(Q(active=False), Q.AND)
                    if activo == 1: query.add(Q(active=True), Q.AND)
                if(idTipo is not None and idTipo > 0):
                    query.add(Q(capacity__type__id=idTipo), Q.AND)
                if (cadena is not None):
                    subquery1.add(Q(capacity__name__contains=cadena), Q.OR)
                    subquery2.add(Q(capacity__code__contains=cadena), Q.OR)
                    subquery3.add(Q(capacity__type__name__contains=cadena), Q.OR)
                competenciasEmpleado = CapacityXEmployee.objects.filter((subquery1 | subquery2 | subquery3) & query).values('capacity__code','capacity__name','capacity__type__name','levelCurrent', 'levelRequired', 'likeness')
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
                competencia = Capacity.objects.filter((subquery1 | subquery2 | subquery3) & query)
                competencias_serializer = CapacitySerializer(competencia, many=True)
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
        necesidadesEmpleado = TrainingNeed.objects.filter(query).values('Capacity__code','Capacity__name','Capacity__type__name','levelCurrent', 'levelRequired', 'levelGap', 'description', 'state', 'type', 'scalePosition__id', 'scalePosition__descriptor')
        return Response(list(necesidadesEmpleado), status = status.HTTP_200_OK)

# class CapacityScaleView(APIView):
#     def get(self, request):
#         competenciaEscala = CapacityScale.objects.all()
#         competenciaEscala_serializer = CapacityScaleSerializer(competenciaEscala, many = True)
#         return Response(competenciaEscala_serializer.data, status = status.HTTP_200_OK)

#     def post(self, request):
#         competenciaEscala_serializer = CapacityScaleSerializer(data = request.data, context = request.data)
#         if competenciaEscala_serializer.is_valid():
#             competenciaEscala_serializer.save()
#             return Response(competenciaEscala_serializer.data,status=status.HTTP_200_OK)
#         return Response(None,status=status.HTTP_400_BAD_REQUEST)
    
#     def delete(self, request, id=0):# delete logico
#         competenciaEscala = CapacityScale.objects.filter(id=id).first()
#         campos = {'active': 'false'}
#         competenciaEscala_serializer = CapacityScaleSerializer(competenciaEscala, data = campos)
#         if competenciaEscala_serializer.is_valid():
#             competenciaEscala_serializer.save()
#             return Response(competenciaEscala_serializer.data,status=status.HTTP_200_OK)
#         return Response(None,status=status.HTTP_400_BAD_REQUEST)
        
class CapacityTypeView(APIView):
    def get(self, request):
        tipoCompetencias = CapacityType.objects.all()
        tipoCompetencia_serializer = CapacityTypeSerializer(tipoCompetencias, many = True)
        return Response(tipoCompetencia_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request):
        tipoCompetencia_serializer = CapacityTypeSerializer(data = request.data, context = request.data)
        if tipoCompetencia_serializer.is_valid():
            tipoCompetencia_serializer.save()
            return Response(tipoCompetencia_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id=0):
        tipoCompetencia = CapacityType.objects.filter(id=id).first()
        campos = {'active': 'false'}
        tipoCompetencia_serializer = CapacityTypeSerializer(tipoCompetencia, data = campos)
        if tipoCompetencia_serializer.is_valid():
            tipoCompetencia_serializer.save()
            return Response(tipoCompetencia_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)

class SearchCapacityTypeView(APIView):
    def get(self,  request, pk = 0):
        if pk == 0:
            competencias = CapacityType.objects.all()
            lista_competencias = []
            for t in competencias:
                if t.get_depth() == 0:
                    lista_competencias.append(t)
        else:
            
            lista_competencias = CapacityType.objects.filter(upperType__id = pk)
        tipoCompetencia_serializer = CapacityTypeSerializer(lista_competencias, many = True)

        return Response(tipoCompetencia_serializer.data, status = status.HTTP_200_OK) 


class SearchCapacityConsolidateView(APIView):
    def post(self, request):
        idArea = request.data["idArea"]
        idPosition = request.data["idPosicion"]
        active = request.data["activo"]
        query = Q()
		
        if idArea is not None and idArea > 0:
            query.add(Q(employee__area__id=idArea), Q.AND)
        if idPosition is not None and idPosition > 0:
            query.add(Q(employee__position__id=idPosition), Q.AND)
        if(active is not None):
            if active == 0: query.add(Q(active=False), Q.AND)
            if active == 1: query.add(Q(active=True), Q.AND)
        query.add(Q(levelRequired__gte=1), Q.AND)
		
        countEmpleadoRange1 = CapacityXEmployee.objects.filter(query & Q(likeness__gte=0) & Q(likeness__lte=19.99)).count()
        countEmpleadoRange2 = CapacityXEmployee.objects.filter(query & Q(likeness__gte=20) & Q(likeness__lte=39.99)).count()
        countEmpleadoRange3 = CapacityXEmployee.objects.filter(query & Q(likeness__gte=40) & Q(likeness__lte=59.99)).count()
        countEmpleadoRange4 = CapacityXEmployee.objects.filter(query & Q(likeness__gte=60) & Q(likeness__lte=79.99)).count()
        countEmpleadoRange5 = CapacityXEmployee.objects.filter(query & Q(likeness__gte=80) & Q(likeness__lte=100)).count()
		
        countTotal = countEmpleadoRange1 + countEmpleadoRange2 + countEmpleadoRange3 + countEmpleadoRange4 + countEmpleadoRange5
        countEmpleadoRange1 = countEmpleadoRange1 / countTotal
        countEmpleadoRange2 = countEmpleadoRange2 / countTotal
        countEmpleadoRange3 = countEmpleadoRange3 / countTotal
        countEmpleadoRange4 = countEmpleadoRange4 / countTotal
        countEmpleadoRange5 = countEmpleadoRange5 / countTotal
		# Ver como lo paso, proporcion (0.5), porcentaje (50) o solo la cuenta (count)
		
        countList = {'rango1': countEmpleadoRange1,
        'rango2': countEmpleadoRange2,
        'rango3': countEmpleadoRange3,
        'rango4': countEmpleadoRange4,
        'rango5': countEmpleadoRange5,
        }
		
        return Response(countList, status = status.HTTP_200_OK)    

class CapacityAreaPositionView(APIView):
    def get(self, request,id=0):
        Capacitys = CapacityXAreaXPosition.objects.all()
        Capacitys_serializer = CapacityXAreaXPositionSerializer(Capacitys,many = True)
        return Response(Capacitys_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request,id=0):
        CapacityList = request.data["competencias"]
        # desactivar las activas
        CapacityXAreaXPosition.objects.filter(Q(area__id = request.data["idArea"]) & Q(position__id = request.data["idPosicion"])).update(active=False)
        # reactivar y agregar las nuevas
        for CapacityItem in CapacityList:
            if CapacityXAreaXPosition.objects.filter(Q(area__id = request.data["idArea"]) & Q(position__id = request.data["idPosicion"]) & Q(Capacity__id = CapacityItem['idCompetencia'])& Q(scalePosition__id = CapacityItem['idEscala'])).count() > 0 :
                register = CapacityXAreaXPosition.objects.filter(Q(area__id = request.data["idArea"]) & Q(position__id = request.data["idPosicion"]) & Q(Capacity__id = CapacityItem['idCompetencia'])& Q(scalePosition__id = CapacityItem['idEscala'])).first()
                fields = {'levelRequired': CapacityItem['nivelRequerido'], 'active': True}
                CapacitysAreaPosition_serializer = CapacityXAreaXPositionSerializer(register, data = fields)
                if CapacitysAreaPosition_serializer.is_valid():
                    CapacitysAreaPosition_serializer.save()
            else:
                fields = {'Capacity': CapacityItem['idCompetencia'], 'scalePosition': CapacityItem['idEscala'],'position': request.data["idPosicion"], 'area': request.data["idArea"], 'levelRequired': CapacityItem['nivelRequerido'], 'active': True}
                CapacitysAreaPosition_serializer = CapacityXAreaXPositionSerializer(data = fields)
                if CapacitysAreaPosition_serializer.is_valid():
                    CapacitysAreaPosition_serializer.save()
        
        # Se puede hacer como Trigger :
        employees = Employee.objects.filter(Q(area__id=request.data["idArea"]) & Q(position__id= request.data["idPosicion"])).values()
        if employees.count() > 0:
            for employee in  employees:
                # nivel requerido en 0
                CapacityXEmployee.objects.filter(Q(employee__id=employee['id'])).update(levelRequired=0, levelGap=0,likeness=0.0, requiredForPosition=False)
                # iterar en la lista de competencias: Por cada competencia gregarle o crearle su competenciaXempleado y necesidadCapacitacion para esa competencia
                for CapacityItem in CapacityList:
                    if CapacityXEmployee.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id = CapacityItem['idCompetencia'])& Q(scalePosition__id = CapacityItem['idEscala'])).count() > 0:
                        register = CapacityXEmployee.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id = CapacityItem['idCompetencia'])& Q(scalePosition__id = CapacityItem['idEscala'])).first()
                        registerVal = CapacityXEmployee.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id = CapacityItem['idCompetencia']) & Q(scalePosition__id = CapacityItem['idEscala'])).values().first()
                        if registerVal['levelCurrent'] >= CapacityItem['nivelRequerido']: 
                            fields = {'levelRequired': CapacityItem['nivelRequerido'], 'levelGap': 0,'likeness':100.00, 'requiredForPosition': True}
                        else : 
                            fields = {'levelRequired': CapacityItem['nivelRequerido'], 'levelGap': CapacityItem['nivelRequerido'] - registerVal['levelCurrent'],'likeness': 100*(registerVal['levelCurrent'] / CapacityItem['nivelRequerido']), 'requiredForPosition': True}
                            

                            # necesidades - ver si normal que se haga aca
                            level = CapacityItem['nivelRequerido'] - registerVal['levelCurrent']
                            needFields = {'description': 'Necesita capacitacion de nivel ' + str(level), 
                                              'levelCurrent': registerVal['levelCurrent'],
                                              'levelRequired': CapacityItem['nivelRequerido'],
                                              'levelGap': CapacityItem['nivelRequerido'] - registerVal['levelCurrent'],
                                              'type': 2,
                                              'state': 1,
                                              'active': True}
                            if TrainingNeed.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id = CapacityItem['idCompetencia']) & Q(scalePosition__id = CapacityItem['idEscala']) & Q(state=2)).count() == 0:
                                if TrainingNeed.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id = CapacityItem['idCompetencia']) & Q(scalePosition__id = CapacityItem['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).count() > 0:
                                    registerNeed = TrainingNeed.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id = CapacityItem['idCompetencia']) & Q(scalePosition__id = CapacityItem['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).first()
                                    trainingNeed_serializer = TrainingNeedSerializer(registerNeed,data=needFields)
                                    if trainingNeed_serializer.is_valid():
                                        trainingNeed_serializer.save()
                                else:
                                    needFields['Capacity'] =  CapacityItem['idCompetencia']
                                    needFields['scalePosition'] =  CapacityItem['idEscala']
                                    needFields['employee'] = employee['id']
                                    trainingNeed_serializer = TrainingNeedSerializer(data=needFields)
                                    if trainingNeed_serializer.is_valid():
                                        trainingNeed_serializer.save()


                        CapacitysEmployee_serializer = CapacityXEmployeeSerializer(register, data = fields)
                        if CapacitysEmployee_serializer.is_valid():
                            CapacitysEmployee_serializer.save()
                    else:
                        fields = {
                            'Capacity':  CapacityItem['idCompetencia'],
                            'scalePosition': CapacityItem['idEscala'],
                            'employee': employee['id'],
                            'levelCurrent': 0,
                            'levelRequired': CapacityItem['nivelRequerido'],
                            'levelGap': CapacityItem['nivelRequerido'],
                            'likeness': 0.0,
                            'hasCertificate': False,
                            'registerByEmployee': False,
                            'requiredForPosition': True,
                            'active': True
                        }
                        CapacitysEmployee_serializer = CapacityXEmployeeSerializer(data = fields)
                        if CapacitysEmployee_serializer.is_valid():
                            CapacitysEmployee_serializer.save()						
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'competencias cargadas correctamente',
                        },)	
    def put(self, request,id=0):
        register = CapacityXAreaXPosition.objects.filter(Q(area__id = request.data["idArea"]) & Q(position__id = request.data["idPosicion"]) & Q(Capacity__id = request.data['idCompetencia']) & Q(scalePosition__id = request.data['idEscala'])).first()
        if register is not None:
            fields = {'levelRequired': request.data["nivelRequerido"], 'active': True}
            CapacitysAreaPosition_serializer = CapacityXAreaXPositionSerializer(register, data = fields)
            if CapacitysAreaPosition_serializer.is_valid():
                CapacitysAreaPosition_serializer.save()

            employees = Employee.objects.filter(Q(area__id=request.data["idArea"]) & Q(position__id= request.data["idPosicion"])).values()
            if employees.count() > 0:
                for employee in  employees:
                    if CapacityXEmployee.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id =  request.data['idCompetencia'])& Q(scalePosition__id = request.data['idEscala'])).count() > 0:
                        registerEmp = CapacityXEmployee.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id =  request.data['idCompetencia'])& Q(scalePosition__id = request.data['idEscala'])).first()
                        registerVal = CapacityXEmployee.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id =  request.data['idCompetencia'])& Q(scalePosition__id = request.data['idEscala'])).values().first()
                        empFields ={'levelRequired': request.data["nivelRequerido"],
                                    'levelGap': request.data["nivelRequerido"] - registerVal['levelCurrent'] if registerVal['levelCurrent'] < request.data["nivelRequerido"] else 0,
                                    'likeness': 100*(registerVal['levelCurrent'] / request.data["nivelRequerido"]) if  registerVal['levelCurrent'] < request.data["nivelRequerido"] else 100.00,
                                    'requiredForPosition': True
                        }
                        CapacitysEmployee_serializer = CapacityXEmployeeSerializer(registerEmp, data = empFields)
                        if CapacitysEmployee_serializer.is_valid():
                            CapacitysEmployee_serializer.save()

                        # necesidades
                        if registerVal['levelCurrent'] < request.data["nivelRequerido"]:
                            level =  request.data["nivelRequerido"] - registerVal['levelCurrent']
                            needFields = {'description': 'Necesita capacitacion de nivel ' + str(level), 
                                                'levelCurrent': registerVal['levelCurrent'],
                                                'levelRequired': request.data["nivelRequerido"],
                                                'levelGap': request.data["nivelRequerido"] - registerVal['levelCurrent'],
                                                'type': 2,
                                                'state': 1,
                                                'active': True}
                            if TrainingNeed.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id = request.data['idCompetencia'])& Q(scalePosition__id = request.data['idEscala']) & Q(state=2)).count() == 0:
                                if TrainingNeed.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id = request.data['idCompetencia']) & Q(scalePosition__id = request.data['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).count() > 0:
                                    registerNeed = TrainingNeed.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id = request.data['idCompetencia']) & Q(scalePosition__id = request.data['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).first()
                                    trainingNeed_serializer = TrainingNeedSerializer(registerNeed,data=needFields)
                                    if trainingNeed_serializer.is_valid():
                                        trainingNeed_serializer.save()
                                else:
                                    needFields['Capacity'] =  request.data['idCompetencia']
                                    needFields['scalePosition'] =  request.data['idEscala']
                                    needFields['employee'] = employee['id']
                                    trainingNeed_serializer = TrainingNeedSerializer(data=needFields)
                                    if trainingNeed_serializer.is_valid():
                                        trainingNeed_serializer.save()
                    else:
                        empFields = {
                            'Capacity':  request.data['idCompetencia'],
                            'scalePosition' :  request.data['idEscala'],
                            'employee': employee['id'],
                            'levelCurrent': 0,
                            'levelRequired': request.data["nivelRequerido"],
                            'levelGap': request.data["nivelRequerido"],
                            'likeness': 0.0,
                            'hasCertificate': False,
                            'registerByEmployee': False,
                            'requiredForPosition': True,
                            'active': True
                        }
                        CapacitysEmployee_serializer = CapacityXEmployeeSerializer(data = empFields)
                        if CapacitysEmployee_serializer.is_valid():
                            CapacitysEmployee_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'competencias cargadas correctamente',
                        },)	
		
class CapacityEmployeeView(APIView):
    def get(self, request,id=0):
        Capacitys = CapacityXEmployee.objects.all()
        Capacitys_serializer = CapacityXEmployeeSerializer(Capacitys,many = True)
        return Response(Capacitys_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request,id=0):
        CapacityList = request.data["competencias"]
        # poner en no requeridas las actuales
        CapacityXEmployee.objects.filter(Q(employee__id = request.data["idEmpleado"])).update(levelRequired=0, levelGap=0, likeness=0.0,requiredForPosition=False)
        # reactivar y agregar las nuevas
        for CapacityItem in CapacityList:
            fields = {
                    'levelCurrent': CapacityItem['nivelActual'],
                    'levelRequired': CapacityItem['nivelRequerido'], 
                    'levelGap': CapacityItem['nivelRequerido'] - CapacityItem['nivelActual'] if CapacityItem['nivelRequerido'] > CapacityItem['nivelActual'] else 0,
                    'likeness': 100*(CapacityItem['nivelActual'] / CapacityItem['nivelRequerido']) if CapacityItem['nivelRequerido'] > CapacityItem['nivelActual'] else 100.00,
                    'hasCertificate': CapacityItem['tieneCertificado'],
                    'requiredForPosition': CapacityItem['requeridoParaPuesto'],
                    'active': True}
            if CapacityXEmployee.objects.filter(Q(employee__id = request.data["idEmpleado"]) & Q(Capacity__id = CapacityItem['idCompetencia'])& Q(scalePosition__id =CapacityItem['idEscala'])).count() > 0 :
                register = CapacityXEmployee.objects.filter(Q(employee__id = request.data["idEmpleado"]) & Q(Capacity__id = CapacityItem['idCompetencia'])& Q(scalePosition__id = CapacityItem['idEscala'])).first()
                CapacitysEmployee_serializer = CapacityXEmployeeSerializer(register, data = fields)
                if CapacitysEmployee_serializer.is_valid():
                    CapacitysEmployee_serializer.save()
            else:
                fields['Capacity'] = CapacityItem['idCompetencia']
                fields['scalePosition'] = CapacityItem['idEscala']
                fields['employee'] = request.data["idEmpleado"]
                fields['registerByEmployee'] = CapacityItem['registradoPorEmpleado']
                CapacitysEmployee_serializer = CapacityXEmployeeSerializer(data = fields)
                if CapacitysEmployee_serializer.is_valid():
                    CapacitysEmployee_serializer.save()
            
            #necesidades
            if CapacityItem['nivelRequerido'] > CapacityItem['nivelActual']:
                level = CapacityItem['nivelRequerido'] - CapacityItem['nivelActual']
                needFields = {'description': 'Necesita capacitacion de nivel ' + str(level), 
                                              'levelCurrent': CapacityItem['nivelActual'],
                                              'levelRequired': CapacityItem['nivelRequerido'],
                                              'levelGap': CapacityItem['nivelRequerido'] - CapacityItem['nivelActual'],
                                              'type': 1 if request.data["esNuevo"] ==  1 else 2,
                                                'state': 1,
                                              'active': True}
                if TrainingNeed.objects.filter(Q(employee__id=request.data["idEmpleado"]) & Q(Capacity__id = CapacityItem['idCompetencia']) & Q(scalePosition__id =CapacityItem['idEscala']) & Q(state=2)).count() == 0:
                    if TrainingNeed.objects.filter(Q(employee__id=request.data["idEmpleado"]) & Q(Capacity__id = CapacityItem['idCompetencia']) & Q(scalePosition__id =CapacityItem['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).count() > 0:
                        registerNeed = TrainingNeed.objects.filter(Q(employee__id=request.data["idEmpleado"]) & Q(Capacity__id = CapacityItem['idCompetencia']) & Q(scalePosition__id =CapacityItem['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).first()
                        trainingNeed_serializer = TrainingNeedSerializer(registerNeed,data=needFields)
                        if trainingNeed_serializer.is_valid():
                                        trainingNeed_serializer.save()
                    else:
                        needFields['Capacity'] = CapacityItem['idCompetencia']
                        needFields['scalePosition'] = CapacityItem['idEscala']
                        needFields['employee'] = request.data["idEmpleado"]
                        trainingNeed_serializer = TrainingNeedSerializer(data=needFields)
                        if trainingNeed_serializer.is_valid():
                            trainingNeed_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'competencias cargadas correctamente',
                        },)	
    def put(self, request,id=0):
        register = CapacityXEmployee.objects.filter(Q(employee__id = request.data["idEmpleado"]) & Q(Capacity__id = request.data['idCompetencia']) & Q(scalePosition__id =request.data['idEscala'])).first()
        if register is not None:        
            registerValues = CapacityXEmployee.objects.filter(Q(employee__id = request.data["idEmpleado"]) & Q(Capacity__id = request.data['idCompetencia']) & Q(scalePosition__id =request.data['idEscala'])).values().first()
            fields = {'levelCurrent': request.data["nivelActual"], 
                    'levelGap': registerValues['levelRequired'] - request.data["nivelActual"] if registerValues['levelRequired'] > request.data["nivelActual"] else 0,
                    'likeness':100*(request.data["nivelActual"] / registerValues['levelRequired']) if registerValues['levelRequired'] > request.data["nivelActual"] else 100.00,
                          'active': True
                          }
            CapacitysEmployee_serializer = CapacityXEmployeeSerializer(register, data = fields)
            if CapacitysEmployee_serializer.is_valid():
                CapacitysEmployee_serializer.save()
            # necesidades
            if registerValues['levelRequired'] > request.data["nivelActual"]:
                level = registerValues['levelRequired'] - request.data["nivelActual"]
                needFields = {'description': 'Necesita capacitacion de nivel ' + str(level), 
                                              'levelCurrent': request.data["nivelActual"],
                                              'levelRequired': registerValues['levelRequired'],
                                              'levelGap': registerValues['levelRequired'] - request.data["nivelActual"],
                                              'type': 2,
                                                'state': 1,
                                              'active': True}
                if TrainingNeed.objects.filter(Q(employee__id=request.data["idEmpleado"]) & Q(Capacity__id = request.data['idCompetencia']) & Q(scalePosition__id =request.data['idEscala']) & Q(state=2)).count() == 0:
                    if TrainingNeed.objects.filter(Q(employee__id=request.data["idEmpleado"]) & Q(Capacity__id = request.data['idCompetencia']) & Q(scalePosition__id =request.data['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).count() > 0:
                        registerNeed = TrainingNeed.objects.filter(Q(employee__id=request.data["idEmpleado"]) & Q(Capacity__id = request.data['idCompetencia']) & Q(scalePosition__id =request.data['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).first()
                        trainingNeed_serializer = TrainingNeedSerializer(registerNeed,data=needFields)
                        if trainingNeed_serializer.is_valid():
                                        trainingNeed_serializer.save()
                    else:
                        needFields['Capacity'] = request.data['idCompetencia']
                        needFields['scalePosition'] = request.data['idEscala']
                        needFields['employee'] = request.data["idEmpleado"]
                        trainingNeed_serializer = TrainingNeedSerializer(data=needFields)
                        if trainingNeed_serializer.is_valid():
                            trainingNeed_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'competencias cargadas correctamente',
                        },)	

class TrainingNeedView(APIView):
    def put(self, request,id=0):
        register = TrainingNeed.objects.filter(Q(id = request.data["necesidad"])).first()
        if register is not None:
            fields = {'state': request.data["estado"]}        
            trainingNeed_serializer = TrainingNeedSerializer(register, data = fields)
            if trainingNeed_serializer.is_valid():
                trainingNeed_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'necesidad actualizada correctamente',
                        },)	
    
class SearchCapacityAreaPositionView(APIView):
    def post(self, request):
        area = request.data["area"]
        position = request.data["posicion"]
        query = Q()
        query.add(Q(active=True), Q.AND)
        if area is not None and area>0:
            query.add(Q(area__id = area), Q.AND)
        if position is not None and position>0:
            query.add(Q(position__id = position), Q.AND)
        areaPositionCapacity = CapacityXAreaXPosition.objects.filter(query).values('id','capacity__id','capacity__name','area__id','area__name','position__id','position__name','levelRequired', 'active')
        return Response(list(areaPositionCapacity), status = status.HTTP_200_OK)
    
class SearchCapacityEmployeeView(APIView):
    def post(self, request):
        employee = request.data["empleado"]
        query = Q()
        query.add(Q(active=True), Q.AND)
        if employee is not None and employee>0:
            query.add(Q(employee__id = employee), Q.AND)
        employeeCapacity = CapacityXEmployee.objects.filter(query).values('id','capacity__id','capacity__name','employee__id','levelCurrent','levelRequired','levelGap','likeness', 'hasCertificate', 'registerByEmployee','requiredForPosition', 'active', 'score')
        return Response(list(employeeCapacity), status = status.HTTP_200_OK)
    
class SearchNeedView(APIView):
    def post(self, request):
        employee = request.data["empleado"]
        query = Q()
        query.add(Q(active=True), Q.AND)
        if employee is not None and employee>0:
            query.add(Q(employee__id = employee), Q.AND)
        necesidades = TrainingNeed.objects.filter(query).values('id','capacity__id','capacity__name','employee__id','description','state','levelCurrent','levelRequired','levelGap','type','active','score')
        return Response(list(necesidades), status = status.HTTP_200_OK)
    
class EmployeeAreaView(APIView):
    def get(self, request):
        areas = Area .objects.filter(isActive=True).values('id','name')
        return Response(list(areas), status = status.HTTP_200_OK)
    def post(self, request):
        area = request.data["area"]
        position = request.data["posicion"]
        query = Q()
        # query.add(Q(active=True), Q.AND)
        if area is not None and area>0:
            query.add(Q(area__id = area), Q.AND)
        if position is not None and position>0:
            query.add(Q(position__id = position), Q.AND)
        employees = Employee.objects.filter(query).values('id','user__first_name','user__last_name','position__name','area__name','user__email','user__is_active')
        return Response(list(employees), status = status.HTTP_200_OK)

class SearchJobOfferView(APIView):
    def post(self, request):
        position = request.data["posicion"]
        area = request.data["area"]
        query = Q()
        query.add(Q(is_active = True), Q.AND)
        if position is not None and position > 0:
            query.add(Q(hiring_process__position__id = position), Q.AND)
            
        areaPositionCapacity = JobOffer.objects.filter(query).values('id','hiring_process','introduction','offer_introduction','responsabilities_introduction','is_active','photo_url','location', 'salary_range')
        return Response(list(areaPositionCapacity), status = status.HTTP_200_OK)
      
def GetUniqueDictionaries(listofDicts):
    """Get a List unique dictionaries
    List to contain unique dictionaries"""
    listOfUniqueDicts = []
    # A set object
    setOfValues = set()
    # iterate over all dictionaries in list
    for dictObj in listofDicts:
        list_Of_tuples = []
        # For each dictionary, iterate over all key
        # and append that to a list as tuples
        for key, value in dictObj.items():
            list_Of_tuples.append( (key, value))
        strValue = ""
        # convert list of tuples to a string
        for key, value in sorted(list_Of_tuples):
            # sort list of tuples, and iterate over them
            # append each pair to string
            strValue += str(key) + "_" + str(value) + "_"
        # Add string to set if not already exist in set
        if strValue not in setOfValues:
            # If string is not in set, then it means
            # this dictionary is unique
            setOfValues.add(strValue)
            listOfUniqueDicts.append (dictObj)
    
    return listOfUniqueDicts

class GenerateTrainingDemandView(APIView):
    def post(self, request):
        area = request.data["area"]
        position = request.data["posicion"]
        employee = request.data["empleado"]
        query = Q()
		
        if employee is not None and employee > 0:
            query.add(Q(id=employee), Q.AND)
        else:
            if area is not None and area > 0:
                query.add(Q(area__id=area), Q.AND)
            if position is not None and position > 0:
                query.add(Q(position__id=position), Q.AND)
		
        employees = Employee.objects.filter(query).values('id')
        ids = []
        for item in employees:
            ids.append(item['id'])
		
        needs = TrainingNeed.objects.filter(Q(employee__id__in =ids) & Q(state=1)).values('capacity__id')
        needsUnique = GetUniqueDictionaries(needs)
		
        resultList = []
		
        for need in needsUnique:
            count = TrainingNeed.objects.filter(Q(employee__id__in =ids) & Q(state=1) & Q(capacity__id = need['capacity__id']) ).count()
            fields = {'competencia': need['capacity__id'], 'cantidad': count}
            resultList.append(fields)
			
        return Response(resultList, status = status.HTTP_200_OK)    
    
class TrainingNeedCourseView(APIView):
    def post(self, request):
        area = request.data["area"]
        position = request.data["posicion"]
        employee = request.data["empleado"]
        query = Q()
		
        courses = request.data["cursos"]
		
        if employee is not None and employee > 0:
            query.add(Q(id=employee), Q.AND)
        else:
            if area is not None and area > 0:
                query.add(Q(area__id=area), Q.AND)
            if position is not None and position > 0:
                query.add(Q(position__id=position), Q.AND)
		
        employees = Employee.objects.filter(query).values('id')
        ids = []
        for item in employees:
            ids.append(item['id'])
		
        for course in courses :
            TrainingNeed.objects.filter(Q(employee__id__in =ids) & Q(state=1) & Q(capacity__id= course['competencia'])).update(course=course['curso'])
        
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'cursos cargados correctamente',
                        },)	
    
class SearchTrainingNeedCourseView(APIView):
    def post(self, request):
        area = request.data["area"]
        position = request.data["posicion"]
        employee = request.data["empleado"]
        query = Q()
		
        if employee is not None and employee > 0:
            query.add(Q(id=employee), Q.AND)
        else:
            if area is not None and area > 0:
                query.add(Q(area__id=area), Q.AND)
            if position is not None and position > 0:
                query.add(Q(position__id=position), Q.AND)
		
        employees = Employee.objects.filter(query).values('id')
        returnList = []
		
        for employee in employees:
            employeeFields = {"empleado": employee['id'], "cursos": []}
            needs = TrainingNeed.objects.filter(Q(employee__id = employee['id']) & Q(state=1)).values('capacity__id','capacity__name', 'score', 'course__id')
            for need in needs :
                course = {'cursoId': need['capacity__id'], 'cursoNombre': need['capacity__name'], 'cursoId': need['course__id']}
                employeeFields['cursos'].append(course)
            returnList.append(employeeFields)
					
        return Response(returnList, status = status.HTTP_200_OK)  

class SaveShortlistedEmployeexJobOffer(APIView):
	def post(self, request):
		offer = request.data['oferta']
		empleados = [e['empleado'] for e in request.data['empleados']]

		for id in empleados:
			json_data = {}
			json_data['job_offer'] = offer 
			json_data['employee'] = id
			try:
				serializer = JobOfferNotificationSerializer(data = json_data)
				serializer.is_valid(raise_exception = True)
				serializer.save()
			except Exception as e:
				return Response(str(e),status=status.HTTP_400_BAD_REQUEST)
		return Response("Se registraron correctamente los empleados",status=status.HTTP_200_OK)


class SearchJobOfferxEmployeePreRegistered(APIView):
        
    def post(self, request):
        employee = request.data['empleado']
        query = Q()

        if employee is not None and employee > 0:
            query.add(Q(employee__id = employee))
            
        notifications = JobOfferNotification.objects.filter(query).values("job_offer__id, job_offer__hiring_process, job_offer__introduction, job_offer__offer_introduction, job_offer__responsabilities_introduction, job_offer__is_active, job_offer__photo_url, job_offer__location, job_offer__salary_range")
        return Response(list(notifications), status = status.HTTP_200_OK)

            
