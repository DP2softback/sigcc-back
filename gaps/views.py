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
from gaps.models import Competence, CompetenceScale, CompetenceType, CompetenceXEmployee, TrainingNeed, CompetenceXAreaXPosition
from login.models import Employee
from personal.models import Area, Position
from gaps.serializers import CompetenceSerializer, CompetenceTypeSerializer,CompetenceScaleSerializer, CompetenceXEmployeeSerializer, TrainingNeedSerializer, CompetenceXAreaXPositionSerializer
from login.serializers import EmployeeSerializerRead, EmployeeSerializerWrite
from gaps.serializers import AreaSerializer
# Create your views here.

class CompetenceView(APIView):
    def get(self, request,id=0):
        competencias = Competence.objects.all()
        competencias_serializer = CompetenceSerializer(competencias,many = True)
        return Response(competencias_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request,id=0):
        competencias_serializer = CompetenceSerializer(data = request.data, context = request.data)
        print(competencias_serializer)
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
                subquery1 = Q()
                subquery2 = Q()
                subquery3 = Q()
                if(activo is not None):
                    if activo == 0: query.add(Q(active=False), Q.AND)
                    if activo == 1: query.add(Q(active=True), Q.AND)
                if(idTipo is not None and idTipo > 0):
                    query.add(Q(competence__type__id=idTipo), Q.AND)
                if (cadena is not None):
                    subquery1.add(Q(competence__name__contains=cadena), Q.OR)
                    subquery2.add(Q(competence__code__contains=cadena), Q.OR)
                    subquery3.add(Q(competence__type__name__contains=cadena), Q.OR)
                competenciasEmpleado = CompetenceXEmployee.objects.filter((subquery1 | subquery2 | subquery3) & query).values('competence__code','competence__name','competence__type__name','levelCurrent', 'levelRequired', 'likeness', 'scalePosition__id', 'scalePosition__descriptor')
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
        necesidadesEmpleado = TrainingNeed.objects.filter(query).values('competence__code','competence__name','competence__type__name','levelCurrent', 'levelRequired', 'levelGap', 'description', 'state', 'type', 'scalePosition__id', 'scalePosition__descriptor')
        return Response(list(necesidadesEmpleado), status = status.HTTP_200_OK)

class CompetenceScaleView(APIView):
    def get(self, request):
        competenciaEscala = CompetenceScale.objects.all()
        competenciaEscala_serializer = CompetenceScaleSerializer(competenciaEscala, many = True)
        return Response(competenciaEscala_serializer.data, status = status.HTTP_200_OK)

    def post(self, request):
        competenciaEscala_serializer = CompetenceScaleSerializer(data = request.data, context = request.data)
        if competenciaEscala_serializer.is_valid():
            competenciaEscala_serializer.save()
            return Response(competenciaEscala_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id=0):# delete logico
        competenciaEscala = CompetenceScale.objects.filter(id=id).first()
        campos = {'active': 'false'}
        competenciaEscala_serializer = CompetenceScaleSerializer(competenciaEscala, data = campos)
        if competenciaEscala_serializer.is_valid():
            competenciaEscala_serializer.save()
            return Response(competenciaEscala_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)
        
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
    
    def delete(self, request, id=0):
        tipoCompetencia = CompetenceType.objects.filter(id=id).first()
        campos = {'active': 'false'}
        tipoCompetencia_serializer = CompetenceTypeSerializer(tipoCompetencia, data = campos)
        if tipoCompetencia_serializer.is_valid():
            tipoCompetencia_serializer.save()
            return Response(tipoCompetencia_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)

class SearchCompetenteTypeView(APIView):
    def get(self,  request, pk = 0):
        if pk == 0:
            competencias = CompetenceType.objects.all()
            lista_competencias = []
            for t in competencias:
                if t.get_depth() == 0:
                    lista_competencias.append(t)
        else:
            
            lista_competencias = CompetenceType.objects.filter(upperType__id = pk)
        tipoCompetencia_serializer = CompetenceTypeSerializer(lista_competencias, many = True)

        return Response(tipoCompetencia_serializer.data, status = status.HTTP_200_OK) 


class SearchCompetenceConsolidateView(APIView):
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
		
        countEmpleadoRange1 = CompetenceXEmployee.objects.filter(query & Q(likeness__gte=0) & Q(likeness__lte=19.99)).count()
        countEmpleadoRange2 = CompetenceXEmployee.objects.filter(query & Q(likeness__gte=20) & Q(likeness__lte=39.99)).count()
        countEmpleadoRange3 = CompetenceXEmployee.objects.filter(query & Q(likeness__gte=40) & Q(likeness__lte=59.99)).count()
        countEmpleadoRange4 = CompetenceXEmployee.objects.filter(query & Q(likeness__gte=60) & Q(likeness__lte=79.99)).count()
        countEmpleadoRange5 = CompetenceXEmployee.objects.filter(query & Q(likeness__gte=80) & Q(likeness__lte=100)).count()
		
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

class CompetenceAreaPositionView(APIView):
    def get(self, request,id=0):
        competences = CompetenceXAreaXPosition.objects.all()
        competences_serializer = CompetenceXAreaXPositionSerializer(competences,many = True)
        return Response(competences_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request,id=0):
        competenceList = request.data["competencias"]
        # desactivar las activas
        CompetenceXAreaXPosition.objects.filter(Q(area__id = request.data["idArea"]) & Q(position__id = request.data["idPosicion"])).update(active=False)
        # reactivar y agregar las nuevas
        for competenceItem in competenceList:
            if CompetenceXAreaXPosition.objects.filter(Q(area__id = request.data["idArea"]) & Q(position__id = request.data["idPosicion"]) & Q(competence__id = competenceItem['idCompetencia'])& Q(scalePosition__id = competenceItem['idEscala'])).count() > 0 :
                register = CompetenceXAreaXPosition.objects.filter(Q(area__id = request.data["idArea"]) & Q(position__id = request.data["idPosicion"]) & Q(competence__id = competenceItem['idCompetencia'])& Q(scalePosition__id = competenceItem['idEscala'])).first()
                fields = {'levelRequired': competenceItem['nivelRequerido'], 'active': True}
                competencesAreaPosition_serializer = CompetenceXAreaXPositionSerializer(register, data = fields)
                if competencesAreaPosition_serializer.is_valid():
                    competencesAreaPosition_serializer.save()
            else:
                fields = {'competence': competenceItem['idCompetencia'], 'scalePosition': competenceItem['idEscala'],'position': request.data["idPosicion"], 'area': request.data["idArea"], 'levelRequired': competenceItem['nivelRequerido'], 'active': True}
                competencesAreaPosition_serializer = CompetenceXAreaXPositionSerializer(data = fields)
                if competencesAreaPosition_serializer.is_valid():
                    competencesAreaPosition_serializer.save()
        
        # Se puede hacer como Trigger :
        employees = Employee.objects.filter(Q(area__id=request.data["idArea"]) & Q(position__id= request.data["idPosicion"])).values()
        if employees.count() > 0:
            for employee in  employees:
                # nivel requerido en 0
                CompetenceXEmployee.objects.filter(Q(employee__id=employee['id'])).update(levelRequired=0, levelGap=0,likeness=0.0, requiredForPosition=False)
                # iterar en la lista de competencias: Por cada competencia gregarle o crearle su competenciaXempleado y necesidadCapacitacion para esa competencia
                for competenceItem in competenceList:
                    if CompetenceXEmployee.objects.filter(Q(employee__id=employee['id']) & Q(competence__id = competenceItem['idCompetencia'])& Q(scalePosition__id = competenceItem['idEscala'])).count() > 0:
                        register = CompetenceXEmployee.objects.filter(Q(employee__id=employee['id']) & Q(competence__id = competenceItem['idCompetencia'])& Q(scalePosition__id = competenceItem['idEscala'])).first()
                        registerVal = CompetenceXEmployee.objects.filter(Q(employee__id=employee['id']) & Q(competence__id = competenceItem['idCompetencia']) & Q(scalePosition__id = competenceItem['idEscala'])).values().first()
                        if registerVal['levelCurrent'] >= competenceItem['nivelRequerido']: 
                            fields = {'levelRequired': competenceItem['nivelRequerido'], 'levelGap': 0,'likeness':100.00, 'requiredForPosition': True}
                        else : 
                            fields = {'levelRequired': competenceItem['nivelRequerido'], 'levelGap': competenceItem['nivelRequerido'] - registerVal['levelCurrent'],'likeness': 100*(registerVal['levelCurrent'] / competenceItem['nivelRequerido']), 'requiredForPosition': True}
                            

                            # necesidades - ver si normal que se haga aca
                            level = competenceItem['nivelRequerido'] - registerVal['levelCurrent']
                            needFields = {'description': 'Necesita capacitacion de nivel ' + str(level), 
                                              'levelCurrent': registerVal['levelCurrent'],
                                              'levelRequired': competenceItem['nivelRequerido'],
                                              'levelGap': competenceItem['nivelRequerido'] - registerVal['levelCurrent'],
                                              'type': 2,
                                              'state': 1,
                                              'active': True}
                            if TrainingNeed.objects.filter(Q(employee__id=employee['id']) & Q(competence__id = competenceItem['idCompetencia']) & Q(scalePosition__id = competenceItem['idEscala']) & Q(state=2)).count() == 0:
                                if TrainingNeed.objects.filter(Q(employee__id=employee['id']) & Q(competence__id = competenceItem['idCompetencia']) & Q(scalePosition__id = competenceItem['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).count() > 0:
                                    registerNeed = TrainingNeed.objects.filter(Q(employee__id=employee['id']) & Q(competence__id = competenceItem['idCompetencia']) & Q(scalePosition__id = competenceItem['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).first()
                                    trainingNeed_serializer = TrainingNeedSerializer(registerNeed,data=needFields)
                                    if trainingNeed_serializer.is_valid():
                                        trainingNeed_serializer.save()
                                else:
                                    needFields['competence'] =  competenceItem['idCompetencia']
                                    needFields['scalePosition'] =  competenceItem['idEscala']
                                    needFields['employee'] = employee['id']
                                    trainingNeed_serializer = TrainingNeedSerializer(data=needFields)
                                    if trainingNeed_serializer.is_valid():
                                        trainingNeed_serializer.save()


                        competencesEmployee_serializer = CompetenceXEmployeeSerializer(register, data = fields)
                        if competencesEmployee_serializer.is_valid():
                            competencesEmployee_serializer.save()
                    else:
                        fields = {
                            'competence':  competenceItem['idCompetencia'],
                            'scalePosition': competenceItem['idEscala'],
                            'employee': employee['id'],
                            'levelCurrent': 0,
                            'levelRequired': competenceItem['nivelRequerido'],
                            'levelGap': competenceItem['nivelRequerido'],
                            'likeness': 0.0,
                            'hasCertificate': False,
                            'registerByEmployee': False,
                            'requiredForPosition': True,
                            'active': True
                        }
                        competencesEmployee_serializer = CompetenceXEmployeeSerializer(data = fields)
                        if competencesEmployee_serializer.is_valid():
                            competencesEmployee_serializer.save()						
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'competencias cargadas correctamente',
                        },)	
    def put(self, request,id=0):
        register = CompetenceXAreaXPosition.objects.filter(Q(area__id = request.data["idArea"]) & Q(position__id = request.data["idPosicion"]) & Q(competence__id = request.data['idCompetencia']) & Q(scalePosition__id = request.data['idEscala'])).first()
        if register is not None:
            fields = {'levelRequired': request.data["nivelRequerido"], 'active': True}
            competencesAreaPosition_serializer = CompetenceXAreaXPositionSerializer(register, data = fields)
            if competencesAreaPosition_serializer.is_valid():
                competencesAreaPosition_serializer.save()

            employees = Employee.objects.filter(Q(area__id=request.data["idArea"]) & Q(position__id= request.data["idPosicion"])).values()
            if employees.count() > 0:
                for employee in  employees:
                    if CompetenceXEmployee.objects.filter(Q(employee__id=employee['id']) & Q(competence__id =  request.data['idCompetencia'])& Q(scalePosition__id = request.data['idEscala'])).count() > 0:
                        registerEmp = CompetenceXEmployee.objects.filter(Q(employee__id=employee['id']) & Q(competence__id =  request.data['idCompetencia'])& Q(scalePosition__id = request.data['idEscala'])).first()
                        registerVal = CompetenceXEmployee.objects.filter(Q(employee__id=employee['id']) & Q(competence__id =  request.data['idCompetencia'])& Q(scalePosition__id = request.data['idEscala'])).values().first()
                        empFields ={'levelRequired': request.data["nivelRequerido"],
                                    'levelGap': request.data["nivelRequerido"] - registerVal['levelCurrent'] if registerVal['levelCurrent'] < request.data["nivelRequerido"] else 0,
                                    'likeness': 100*(registerVal['levelCurrent'] / request.data["nivelRequerido"]) if  registerVal['levelCurrent'] < request.data["nivelRequerido"] else 100.00,
                                    'requiredForPosition': True
                        }
                        competencesEmployee_serializer = CompetenceXEmployeeSerializer(registerEmp, data = empFields)
                        if competencesEmployee_serializer.is_valid():
                            competencesEmployee_serializer.save()

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
                            if TrainingNeed.objects.filter(Q(employee__id=employee['id']) & Q(competence__id = request.data['idCompetencia'])& Q(scalePosition__id = request.data['idEscala']) & Q(state=2)).count() == 0:
                                if TrainingNeed.objects.filter(Q(employee__id=employee['id']) & Q(competence__id = request.data['idCompetencia']) & Q(scalePosition__id = request.data['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).count() > 0:
                                    registerNeed = TrainingNeed.objects.filter(Q(employee__id=employee['id']) & Q(competence__id = request.data['idCompetencia']) & Q(scalePosition__id = request.data['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).first()
                                    trainingNeed_serializer = TrainingNeedSerializer(registerNeed,data=needFields)
                                    if trainingNeed_serializer.is_valid():
                                        trainingNeed_serializer.save()
                                else:
                                    needFields['competence'] =  request.data['idCompetencia']
                                    needFields['scalePosition'] =  request.data['idEscala']
                                    needFields['employee'] = employee['id']
                                    trainingNeed_serializer = TrainingNeedSerializer(data=needFields)
                                    if trainingNeed_serializer.is_valid():
                                        trainingNeed_serializer.save()
                    else:
                        empFields = {
                            'competence':  request.data['idCompetencia'],
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
                        competencesEmployee_serializer = CompetenceXEmployeeSerializer(data = empFields)
                        if competencesEmployee_serializer.is_valid():
                            competencesEmployee_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'competencias cargadas correctamente',
                        },)	
		
class CompetenceEmployeeView(APIView):
    def get(self, request,id=0):
        competences = CompetenceXEmployee.objects.all()
        competences_serializer = CompetenceXEmployeeSerializer(competences,many = True)
        return Response(competences_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request,id=0):
        competenceList = request.data["competencias"]
        # poner en no requeridas las actuales
        CompetenceXEmployee.objects.filter(Q(employee__id = request.data["idEmpleado"])).update(levelRequired=0, levelGap=0, likeness=0.0,requiredForPosition=False)
        # reactivar y agregar las nuevas
        for competenceItem in competenceList:
            fields = {
                    'levelCurrent': competenceItem['nivelActual'],
                    'levelRequired': competenceItem['nivelRequerido'], 
                    'levelGap': competenceItem['nivelRequerido'] - competenceItem['nivelActual'] if competenceItem['nivelRequerido'] > competenceItem['nivelActual'] else 0,
                    'likeness': 100*(competenceItem['nivelActual'] / competenceItem['nivelRequerido']) if competenceItem['nivelRequerido'] > competenceItem['nivelActual'] else 100.00,
                    'hasCertificate': competenceItem['tieneCertificado'],
                    'requiredForPosition': competenceItem['requeridoParaPuesto'],
                    'active': True}
            if CompetenceXEmployee.objects.filter(Q(employee__id = request.data["idEmpleado"]) & Q(competence__id = competenceItem['idCompetencia'])& Q(scalePosition__id =competenceItem['idEscala'])).count() > 0 :
                register = CompetenceXEmployee.objects.filter(Q(employee__id = request.data["idEmpleado"]) & Q(competence__id = competenceItem['idCompetencia'])& Q(scalePosition__id = competenceItem['idEscala'])).first()
                competencesEmployee_serializer = CompetenceXEmployeeSerializer(register, data = fields)
                if competencesEmployee_serializer.is_valid():
                    competencesEmployee_serializer.save()
            else:
                fields['competence'] = competenceItem['idCompetencia']
                fields['scalePosition'] = competenceItem['idEscala']
                fields['employee'] = request.data["idEmpleado"]
                fields['registerByEmployee'] = competenceItem['registradoPorEmpleado']
                competencesEmployee_serializer = CompetenceXEmployeeSerializer(data = fields)
                if competencesEmployee_serializer.is_valid():
                    competencesEmployee_serializer.save()
            
            #necesidades
            if competenceItem['nivelRequerido'] > competenceItem['nivelActual']:
                level = competenceItem['nivelRequerido'] - competenceItem['nivelActual']
                needFields = {'description': 'Necesita capacitacion de nivel ' + str(level), 
                                              'levelCurrent': competenceItem['nivelActual'],
                                              'levelRequired': competenceItem['nivelRequerido'],
                                              'levelGap': competenceItem['nivelRequerido'] - competenceItem['nivelActual'],
                                              'type': 1 if request.data["esNuevo"] ==  1 else 2,
                                                'state': 1,
                                              'active': True}
                if TrainingNeed.objects.filter(Q(employee__id=request.data["idEmpleado"]) & Q(competence__id = competenceItem['idCompetencia']) & Q(scalePosition__id =competenceItem['idEscala']) & Q(state=2)).count() == 0:
                    if TrainingNeed.objects.filter(Q(employee__id=request.data["idEmpleado"]) & Q(competence__id = competenceItem['idCompetencia']) & Q(scalePosition__id =competenceItem['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).count() > 0:
                        registerNeed = TrainingNeed.objects.filter(Q(employee__id=request.data["idEmpleado"]) & Q(competence__id = competenceItem['idCompetencia']) & Q(scalePosition__id =competenceItem['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).first()
                        trainingNeed_serializer = TrainingNeedSerializer(registerNeed,data=needFields)
                        if trainingNeed_serializer.is_valid():
                                        trainingNeed_serializer.save()
                    else:
                        needFields['competence'] = competenceItem['idCompetencia']
                        needFields['scalePosition'] = competenceItem['idEscala']
                        needFields['employee'] = request.data["idEmpleado"]
                        trainingNeed_serializer = TrainingNeedSerializer(data=needFields)
                        if trainingNeed_serializer.is_valid():
                            trainingNeed_serializer.save()
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'competencias cargadas correctamente',
                        },)	
    def put(self, request,id=0):
        register = CompetenceXEmployee.objects.filter(Q(employee__id = request.data["idEmpleado"]) & Q(competence__id = request.data['idCompetencia']) & Q(scalePosition__id =request.data['idEscala'])).first()
        if register is not None:        
            registerValues = CompetenceXEmployee.objects.filter(Q(employee__id = request.data["idEmpleado"]) & Q(competence__id = request.data['idCompetencia']) & Q(scalePosition__id =request.data['idEscala'])).values().first()
            fields = {'levelCurrent': request.data["nivelActual"], 
                    'levelGap': registerValues['levelRequired'] - request.data["nivelActual"] if registerValues['levelRequired'] > request.data["nivelActual"] else 0,
                    'likeness':100*(request.data["nivelActual"] / registerValues['levelRequired']) if registerValues['levelRequired'] > request.data["nivelActual"] else 100.00,
                          'active': True
                          }
            competencesEmployee_serializer = CompetenceXEmployeeSerializer(register, data = fields)
            if competencesEmployee_serializer.is_valid():
                competencesEmployee_serializer.save()
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
                if TrainingNeed.objects.filter(Q(employee__id=request.data["idEmpleado"]) & Q(competence__id = request.data['idCompetencia']) & Q(scalePosition__id =request.data['idEscala']) & Q(state=2)).count() == 0:
                    if TrainingNeed.objects.filter(Q(employee__id=request.data["idEmpleado"]) & Q(competence__id = request.data['idCompetencia']) & Q(scalePosition__id =request.data['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).count() > 0:
                        registerNeed = TrainingNeed.objects.filter(Q(employee__id=request.data["idEmpleado"]) & Q(competence__id = request.data['idCompetencia']) & Q(scalePosition__id =request.data['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).first()
                        trainingNeed_serializer = TrainingNeedSerializer(registerNeed,data=needFields)
                        if trainingNeed_serializer.is_valid():
                                        trainingNeed_serializer.save()
                    else:
                        needFields['competence'] = request.data['idCompetencia']
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
    
class SearchCompetenceAreaPositionView(APIView):
    def post(self, request):
        area = request.data["area"]
        position = request.data["posicion"]
        query = Q()
        query.add(Q(active=True), Q.AND)
        if area is not None and area>0:
            query.add(Q(area__id = area), Q.AND)
        if position is not None and position>0:
            query.add(Q(position__id = position), Q.AND)
        areaPositionCompetence = CompetenceXAreaXPosition.objects.filter(query).values('id','competence__id','competence__name','area__id','area__name','position__id','position__name','levelRequired', 'active','scalePosition__id', 'scalePosition__descriptor')
        return Response(list(areaPositionCompetence), status = status.HTTP_200_OK)
    
class SearchCompetenceEmployeeView(APIView):
    def post(self, request):
        employee = request.data["empleado"]
        query = Q()
        query.add(Q(active=True), Q.AND)
        if employee is not None and employee>0:
            query.add(Q(employee__id = employee), Q.AND)
        employeeCompetence = CompetenceXEmployee.objects.filter(query).values('id','competence__id','competence__name','employee__id','levelCurrent','levelRequired','levelGap','likeness', 'hasCertificate', 'registerByEmployee','requiredForPosition', 'active', 'scalePosition__id', 'scalePosition__descriptor')
        return Response(list(employeeCompetence), status = status.HTTP_200_OK)
    
class SearchNeedView(APIView):
    def post(self, request):
        employee = request.data["empleado"]
        query = Q()
        query.add(Q(active=True), Q.AND)
        if employee is not None and employee>0:
            query.add(Q(employee__id = employee), Q.AND)
        necesidades = TrainingNeed.objects.filter(query).values('id','competence__id','competence__name','employee__id','description','state','levelCurrent','levelRequired','levelGap','type','active','scalePosition__id', 'scalePosition__descriptor')
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
		
        needs = TrainingNeed.objects.filter(Q(employee__id__in =ids) & Q(state=1)).values('competence__id', 'scalePosition__id')
        needsUnique = GetUniqueDictionaries(needs)
		
        resultList = []
		
        for need in needsUnique:
            count = TrainingNeed.objects.filter(Q(employee__id__in =ids) & Q(state=1) & Q(competence__id = need['competence__id']) & Q(scalePosition__id = need['scalePosition__id'])).count()
            fields = {'competencia': need['competence__id'], 'escala': need['scalePosition__id'], 'cantidad': count}
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
            TrainingNeed.objects.filter(Q(employee__id__in =ids) & Q(state=1) & Q(competence__id= course['competencia']) & Q(scalePosition__id= course['escala'])).update(course=course['curso'])
        
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
            employee = {"empleado": employee['id'], "cursos": []}
            needs = TrainingNeed.objects.filter(Q(employee__id = employee['id']) & Q(state=1)).values('competence__id','competence__name', 'scalePosition__id', 'scalePosition__descriptor', 'course__id')
            for need in needs :
                course = {'cursoId': need['competence__id'], 'cursoNombre': need['competence__name'], 'escalaId': need['scalePosition__id'], 'escalaNombre': need['scalePosition__descriptor'], 'cursoId': need['course__id']}
                employee['cursos'].append(course)
            returnList.append(employee)
					
        return Response(returnList, status = status.HTTP_200_OK)  