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
from evaluations_and_promotions.models import *
from evaluations_and_promotions.serializers import *
from login.models import *
from personal.models import *
from personal.serializers import *
from login.serializers import *
from gaps.serializers import *

from datetime import datetime
from django.utils import timezone

#import openai as ai
#ai.api_key = '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'
# Create your views here.

class CapacityView(APIView):
    def get(self, request,id=0):
        competencias = SubCategory.objects.all()
        competencias_serializer = SubCategorySerializer(competencias,many = True)
        return Response(competencias_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request,id=0):
        #request.data['isActive'] = request.data.pop('active')
        if request.data["type"] == 0: 
            request.data["type"] = SubCategory.Type.TECNICA
            tipo='TEC'
        else: 
            request.data["type"] = SubCategory.Type.BLANDA
            tipo = 'HAB'
        competencias_serializer = SubCategorySerializer(data = request.data, context = request.data)
        print(competencias_serializer)
        if competencias_serializer.is_valid():
            competencias_serializer.save()
            # Generador de codigo de competencia
            competencia = SubCategory.objects.filter(id=competencias_serializer.data['id']).first()
            # response = ai.Completion.create(
            #                 engine='text-davinci-003',
            #                 prompt='Dame una descripción de máximo 100 caracteres de la competencia de ' + competencias_serializer.data['name'],
            #                 max_tokens=200,)
            campos = {'code': tipo + '-' + str(competencias_serializer.data['name'][0:3]).upper() + str(competencias_serializer.data['id'])
            }
            #          'description': str(response.choices[0].text.strip()).replace('\n', '')}
            competencias_serializer2 = SubCategorySerializer(competencia, data = campos)
            print(competencias_serializer2)
            if competencias_serializer2.is_valid():
                competencias_serializer2.save()
                return Response(competencias_serializer2.data,status=status.HTTP_200_OK)
            return Response(competencias_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request,id=0):
        idComp = request.data["id"]
        if request.data["type"] == 0: 
            request.data["type"] = SubCategory.Type.TECNICA
            tipo='TEC'
        else: 
            request.data["type"] = SubCategory.Type.BLANDA
            tipo = 'HAB'
        if request.data["type"] is not None:
            # Generador de codigo de competencia
            if request.data["type"] == 0: tipo='TEC'
            else: tipo = 'HAB'
            campos = {'code': tipo + '-'+ str(request.data['name'][0:3]).upper() + str(request.data['id'])}
            request.data["code"] = campos['code']
        competencia = SubCategory.objects.filter(id=idComp).first()
        competencias_serializer = SubCategorySerializer(competencia, data = request.data, context = request.data)
        if competencias_serializer.is_valid():
            competencias_serializer.save()
            return Response(competencias_serializer.data,status=status.HTTP_200_OK)
        return Response(None,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id=0):
        competencia = SubCategory.objects.filter(id=id).first()
        campos = {'isActive': 'false'}
        competencias_serializer = SubCategorySerializer(competencia, data = campos)
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
            competencia = SubCategory.objects.filter(id=idComp).first()
            competencias_serializer = CompetenceReadSerializer(competencia)
            return Response(competencias_serializer.data, status = status.HTTP_200_OK)
        else:
            if idEmp is not None and idEmp >0:
                query = Q(employee__id = idEmp)
                subquery1 = Q()
                subquery2 = Q()
                if(activo is not None):
                    if activo == 0: query.add(Q(isActive=False), Q.AND)
                    if activo == 1: query.add(Q(isActive=True), Q.AND)
                if(idTipo is not None and idTipo in [0,1]):
                    query.add(Q(competence__type=idTipo), Q.AND)
                if (cadena is not None):
                    subquery1.add(Q(competence__name__contains=cadena), Q.OR)
                    subquery2.add(Q(competence__code__contains=cadena), Q.OR)
                #competenciasEmpleado = CompetencessXEmployeeXLearningPath.objects.filter((subquery1 | subquery2) & query).values('competence__code','competence__name','competence__type','scale', 'scaleRequired', 'likeness')
                competenciasEmpleado = CompetencessXEmployeeXLearningPath.objects.filter((subquery1 | subquery2) & query)
                #competenciasEmpleado = CompetencessXEmployeeXLearningPath.objects.get((subquery1 | subquery2) & query)
                competenciasEmpleado_serializer = CompetenceEmployeeReadSerializer(competenciasEmpleado, many=True)
                #return Response(list(competenciasEmpleado), status = status.HTTP_200_OK)
                return Response(competenciasEmpleado_serializer.data, status = status.HTTP_200_OK)
            else:
                query = Q()
                subquery1 = Q()
                subquery2 = Q()
                if (cadena is not None):
                    subquery1.add(Q(name__contains=cadena), Q.OR)
                    subquery2.add(Q(code__contains=cadena), Q.OR)
                if(idTipo is not None and idTipo in [0,1]):
                    query.add(Q(type=idTipo), Q.AND)
                if(activo is not None):
                    if activo == 0: query.add(Q(isActive=False), Q.AND)
                    if activo == 1: query.add(Q(isActive=True), Q.AND)
                competencia = SubCategory.objects.filter((subquery1 | subquery2 ) & query)
                competencias_serializer = CompetenceReadSerializer(competencia, many=True)
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
            if activo == 0: query.add(Q(isActive=False), Q.AND)
            if activo == 1: query.add(Q(isActive=True), Q.AND)
        if estado is not None:
            query.add(Q(state__contains = estado), Q.AND)
        if tipo is not None:
            query.add(Q(type__contains = tipo), Q.AND)
        #necesidadesEmpleado = TrainingNeed.objects.filter(query).values('id','competence__id','competence__name','competence__type','employee__id','description','state','levelCurrent','levelRequired','levelGap','type','isActive','score')
        necesidadesEmpleado = TrainingNeed.objects.filter(query)
        necesidadesEmpleado_serializer = TrainingNeedReadSerializer(necesidadesEmpleado,many=True)
        #return Response(list(necesidadesEmpleado), status = status.HTTP_200_OK)
        return Response(necesidadesEmpleado_serializer.data, status = status.HTTP_200_OK)
        
class CapacityTypeView(APIView):
    def get(self, request):
        lista = [
            {
                    "id": 0,
                    "abbreviation": "TEC",
                    "name": "Tecnica",
                    "description": "Competencias que involucran conocimientos de tecnologías",
                    "isActive": True,
                    "upperType": None
            } ,
            {
                    "id": 1,
                    "abbreviation": "HAB",
                    "name": "Blanda",
                    "description": "Competencias que involucran interacciones con otras personas",
                    "isActive": True,
                    "upperType": None
            }  
        ]
        #tipoCompetencias = CapacityType.objects.all()
        #tipoCompetencia_serializer = CapacityTypeSerializer(tipoCompetencias, many = True)
        return Response(lista, status = status.HTTP_200_OK)
    
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
            if active == 0: query.add(Q(isActive=False), Q.AND)
            if active == 1: query.add(Q(isActive=True), Q.AND)
        #query.add(Q(levelRequired__gte=1), Q.AND)
		
        countEmpleadoRange1 = CompetencessXEmployeeXLearningPath.objects.filter(query & Q(likeness__gte=0) & Q(likeness__lte=19.99)).count()
        countEmpleadoRange2 = CompetencessXEmployeeXLearningPath.objects.filter(query & Q(likeness__gte=20) & Q(likeness__lte=39.99)).count()
        countEmpleadoRange3 = CompetencessXEmployeeXLearningPath.objects.filter(query & Q(likeness__gte=40) & Q(likeness__lte=59.99)).count()
        countEmpleadoRange4 = CompetencessXEmployeeXLearningPath.objects.filter(query & Q(likeness__gte=60) & Q(likeness__lte=79.99)).count()
        countEmpleadoRange5 = CompetencessXEmployeeXLearningPath.objects.filter(query & Q(likeness__gte=80) & Q(likeness__lte=100)).count()
		
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
        competenceList = request.data["competencias"]
        # desactivar las activas
        areaXposition = AreaxPosicion.objects.filter(Q(area__id = request.data['area'])&Q(position__id = request.data['posicion'])).values().first()
        if areaXposition is None:
            return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'area y posicion no encontrado',
                        },)	
        CompetencyxAreaxPosition.objects.filter(Q(areaxposition__id = areaXposition["id"])).delete()
        # reactivar y agregar las nuevas
        for competenceItem in competenceList:
            fields = {'competency': competenceItem['competencia'],
                      'areaxposition': areaXposition["id"],
                      'scale': competenceItem['nivel']
                      #,'score': competenceItem['nota']
                      }
            competencyAreaPosition_serializer = CompetencyxAreaxPositionWriteSerializer(data = fields)
            if competencyAreaPosition_serializer.is_valid():
                    competencyAreaPosition_serializer.save()
        # # Se puede hacer como Trigger :
        # employees = Employee.objects.filter(Q(area__id=request.data["idArea"]) & Q(position__id= request.data["idPosicion"])).values()
        # if employees.count() > 0:
        #     for employee in  employees:
        #         # nivel requerido en 0
        #         CapacityXEmployee.objects.filter(Q(employee__id=employee['id'])).update(levelRequired=0, levelGap=0,likeness=0.0, requiredForPosition=False)
        #         # iterar en la lista de competencias: Por cada competencia gregarle o crearle su competenciaXempleado y necesidadCapacitacion para esa competencia
        #         for competenceItem in competenceList:
        #             if CapacityXEmployee.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id = competenceItem['idCompetencia'])& Q(scalePosition__id = competenceItem['idEscala'])).count() > 0:
        #                 register = CapacityXEmployee.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id = competenceItem['idCompetencia'])& Q(scalePosition__id = competenceItem['idEscala'])).first()
        #                 registerVal = CapacityXEmployee.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id = competenceItem['idCompetencia']) & Q(scalePosition__id = competenceItem['idEscala'])).values().first()
        #                 if registerVal['levelCurrent'] >= competenceItem['nivelRequerido']: 
        #                     fields = {'levelRequired': competenceItem['nivelRequerido'], 'levelGap': 0,'likeness':100.00, 'requiredForPosition': True}
        #                 else : 
        #                     fields = {'levelRequired': competenceItem['nivelRequerido'], 'levelGap': competenceItem['nivelRequerido'] - registerVal['levelCurrent'],'likeness': 100*(registerVal['levelCurrent'] / competenceItem['nivelRequerido']), 'requiredForPosition': True}
                            

        #                     # necesidades - ver si normal que se haga aca
        #                     level = competenceItem['nivelRequerido'] - registerVal['levelCurrent']
        #                     needFields = {'description': 'Necesita capacitacion de nivel ' + str(level), 
        #                                       'levelCurrent': registerVal['levelCurrent'],
        #                                       'levelRequired': competenceItem['nivelRequerido'],
        #                                       'levelGap': competenceItem['nivelRequerido'] - registerVal['levelCurrent'],
        #                                       'type': 2,
        #                                       'state': 1,
        #                                       'active': True}
        #                     if TrainingNeed.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id = competenceItem['idCompetencia']) & Q(scalePosition__id = competenceItem['idEscala']) & Q(state=2)).count() == 0:
        #                         if TrainingNeed.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id = competenceItem['idCompetencia']) & Q(scalePosition__id = competenceItem['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).count() > 0:
        #                             registerNeed = TrainingNeed.objects.filter(Q(employee__id=employee['id']) & Q(Capacity__id = competenceItem['idCompetencia']) & Q(scalePosition__id = competenceItem['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).first()
        #                             trainingNeed_serializer = TrainingNeedSerializer(registerNeed,data=needFields)
        #                             if trainingNeed_serializer.is_valid():
        #                                 trainingNeed_serializer.save()
        #                         else:
        #                             needFields['Capacity'] =  competenceItem['idCompetencia']
        #                             needFields['scalePosition'] =  competenceItem['idEscala']
        #                             needFields['employee'] = employee['id']
        #                             trainingNeed_serializer = TrainingNeedSerializer(data=needFields)
        #                             if trainingNeed_serializer.is_valid():
        #                                 trainingNeed_serializer.save()


        #                 CapacitysEmployee_serializer = CapacityXEmployeeSerializer(register, data = fields)
        #                 if CapacitysEmployee_serializer.is_valid():
        #                     CapacitysEmployee_serializer.save()
        #             else:
        #                 fields = {
        #                     'Capacity':  competenceItem['idCompetencia'],
        #                     'scalePosition': competenceItem['idEscala'],
        #                     'employee': employee['id'],
        #                     'levelCurrent': 0,
        #                     'levelRequired': competenceItem['nivelRequerido'],
        #                     'levelGap': competenceItem['nivelRequerido'],
        #                     'likeness': 0.0,
        #                     'hasCertificate': False,
        #                     'registerByEmployee': False,
        #                     'requiredForPosition': True,
        #                     'active': True
        #                 }
        #                 CapacitysEmployee_serializer = CapacityXEmployeeSerializer(data = fields)
        #                 if CapacitysEmployee_serializer.is_valid():
        #                     CapacitysEmployee_serializer.save()						
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
        Capacitys = CompetencessXEmployeeXLearningPath.objects.all()
        Capacitys_serializer = CompetenceEmployeeReadSerializer(Capacitys,many = True)
        return Response(Capacitys_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request,id=0):
        competenceList = request.data["competencias"]
        # poner en no requeridas las actuales
        if request.data["esNuevo"]:
            CompetencessXEmployeeXLearningPath.objects.filter(Q(employee__id = request.data["empleado"])).update(levelGap=0, likeness=0.0,requiredForPosition=False)
        employee = Employee.objects.filter(id=request.data["empleado"]).values().first()
        if employee is None:
            return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'empleado no encontrado',
                        },)	
        #print(employee)
        #print(employee['position'])
        areaXposition = AreaxPosicion.objects.filter(Q(area__id = employee['area_id']) and Q(position__id = employee['position_id'])).values().first()
        if areaXposition is None:
            return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'area y posicion no encontrado',
                        },)	
        # reactivar y agregar las nuevas
        for competenceItem in competenceList:
            nota = competenceItem['nota']
            if nota in range(0, 21): levelCurrent = CompetencessXEmployeeXLearningPath.Scale.NO_INICIADO
            elif nota in range(21, 41): levelCurrent = CompetencessXEmployeeXLearningPath.Scale.EN_PROCESO
            elif nota in range(41, 61): levelCurrent = CompetencessXEmployeeXLearningPath.Scale.LOGRADO
            elif nota in range(61, 81): levelCurrent = CompetencessXEmployeeXLearningPath.Scale.SOBRESALIENTE
            elif nota in range(81, 101): levelCurrent = CompetencessXEmployeeXLearningPath.Scale.EXPERTO
            levelGap = 0
            likeness = 100.00
            areaXpositionXcompetence = CompetencyxAreaxPosition.objects.filter(Q(areaxposition__id = areaXposition['id']) and Q(competency__id = competenceItem['competencia'])).values().first()
            if areaXpositionXcompetence is None:
                levelRequired = CompetencessXEmployeeXLearningPath.Scale.NO_INICIADO
                positionRequired = False
            else:
                levelRequired = areaXpositionXcompetence['scale']
                positionRequired = True
                levelGap = levelRequired - levelCurrent if levelRequired > levelCurrent else 0
                likeness = 100*(nota/(levelRequired*20+1)) if levelRequired > levelCurrent else 100.00

            fields = {
                    'scale': levelCurrent,
                    'scaleRequired': levelRequired, 
                    'levelGap': levelGap,
                    'likeness': likeness,
                    'hasCertificate': False,
                    'requiredForPosition': positionRequired,
                    'score': nota,
                    'isActual': True,
                    'modifiedBy': request.data["modificado"],
                    'isActive': True}
            if CompetencessXEmployeeXLearningPath.objects.filter(Q(employee__id = request.data["empleado"]) & Q(competence__id = competenceItem['competencia'])).count() > 0 :
                register = CompetencessXEmployeeXLearningPath.objects.filter(Q(employee__id = request.data["empleado"]) & Q(competence__id = competenceItem['competencia'])).first()
                competenceEmployee_serializer = CompetencessXEmployeeXLearningPathSerializer(register, data = fields)
                if competenceEmployee_serializer.is_valid():
                    competenceEmployee_serializer.save()
            else:
                fields['competence'] = competenceItem['competencia']
                fields['employee'] = request.data["empleado"]
                fields['registerByEmployee'] = False
                competenceEmployee_serializer = CompetencessXEmployeeXLearningPathSerializer(data = fields)
                if competenceEmployee_serializer.is_valid():
                    competenceEmployee_serializer.save()
            #necesidades
            if levelGap != 0:
                #level = competenceItem['nivelRequerido'] - competenceItem['nivelActual']
                needFields = {'description': 'Necesita capacitacion',# + str(level), 
                                              'levelCurrent': levelCurrent,
                                              'levelRequired': levelRequired,
                                              'levelGap': levelGap,
                                              'type': 'Incorporacion' if request.data["esNuevo"] ==  1 else 'Evaluacion Continua',
                                              'score':  nota,
                                                'state': 'Por solucionar',
                                              'isActive': True
                                              #podria poner idCurso=null
                                              }
                if TrainingNeed.objects.filter(Q(employee__id=request.data["empleado"]) & Q(competence__id = competenceItem['competencia']) & Q(state='En proceso')).count() == 0:
                    if TrainingNeed.objects.filter(Q(employee__id=request.data["empleado"]) & Q(competence__id = competenceItem['competencia'])).count() > 0:
                        registerNeed = TrainingNeed.objects.filter(Q(employee__id=request.data["empleado"]) & Q(competence__id = competenceItem['competencia'])).first()
                        trainingNeed_serializer = TrainingNeedSerializer(registerNeed,data=needFields)
                        if trainingNeed_serializer.is_valid():
                                        trainingNeed_serializer.save()
                    else:
                        needFields['competence'] = competenceItem['competencia']
                        needFields['employee'] = request.data["empleado"]
                        trainingNeed_serializer = TrainingNeedSerializer(data=needFields)
                        if trainingNeed_serializer.is_valid():
                            trainingNeed_serializer.save()
            else:
                if TrainingNeed.objects.filter(Q(employee__id=request.data["empleado"]) & Q(competence__id = competenceItem['competencia'])).count() > 0:
                    #podria poner idCurso=null
                    TrainingNeed.objects.filter(Q(employee__id=request.data["empleado"]) & Q(competence__id = competenceItem['competencia'])).update(state='Solucionado')
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'competencias cargadas correctamente',
                        },)	
    def put(self, request,id=0):
    #     register = CapacityXEmployee.objects.filter(Q(employee__id = request.data["idEmpleado"]) & Q(Capacity__id = request.data['idCompetencia']) & Q(scalePosition__id =request.data['idEscala'])).first()
    #     if register is not None:        
    #         registerValues = CapacityXEmployee.objects.filter(Q(employee__id = request.data["idEmpleado"]) & Q(Capacity__id = request.data['idCompetencia']) & Q(scalePosition__id =request.data['idEscala'])).values().first()
    #         fields = {'levelCurrent': request.data["nivelActual"], 
    #                 'levelGap': registerValues['levelRequired'] - request.data["nivelActual"] if registerValues['levelRequired'] > request.data["nivelActual"] else 0,
    #                 'likeness':100*(request.data["nivelActual"] / registerValues['levelRequired']) if registerValues['levelRequired'] > request.data["nivelActual"] else 100.00,
    #                       'active': True
    #                       }
    #         CapacitysEmployee_serializer = CapacityXEmployeeSerializer(register, data = fields)
    #         if CapacitysEmployee_serializer.is_valid():
    #             CapacitysEmployee_serializer.save()
    #         # necesidades
    #         if registerValues['levelRequired'] > request.data["nivelActual"]:
    #             level = registerValues['levelRequired'] - request.data["nivelActual"]
    #             needFields = {'description': 'Necesita capacitacion de nivel ' + str(level), 
    #                                           'levelCurrent': request.data["nivelActual"],
    #                                           'levelRequired': registerValues['levelRequired'],
    #                                           'levelGap': registerValues['levelRequired'] - request.data["nivelActual"],
    #                                           'type': 2,
    #                                             'state': 1,
    #                                           'active': True}
    #             if TrainingNeed.objects.filter(Q(employee__id=request.data["idEmpleado"]) & Q(Capacity__id = request.data['idCompetencia']) & Q(scalePosition__id =request.data['idEscala']) & Q(state=2)).count() == 0:
    #                 if TrainingNeed.objects.filter(Q(employee__id=request.data["idEmpleado"]) & Q(Capacity__id = request.data['idCompetencia']) & Q(scalePosition__id =request.data['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).count() > 0:
    #                     registerNeed = TrainingNeed.objects.filter(Q(employee__id=request.data["idEmpleado"]) & Q(Capacity__id = request.data['idCompetencia']) & Q(scalePosition__id =request.data['idEscala']) & Q(state__gte=1) & Q(state__lte=3)).first()
    #                     trainingNeed_serializer = TrainingNeedSerializer(registerNeed,data=needFields)
    #                     if trainingNeed_serializer.is_valid():
    #                                     trainingNeed_serializer.save()
    #                 else:
    #                     needFields['Capacity'] = request.data['idCompetencia']
    #                     needFields['scalePosition'] = request.data['idEscala']
    #                     needFields['employee'] = request.data["idEmpleado"]
    #                     trainingNeed_serializer = TrainingNeedSerializer(data=needFields)
    #                     if trainingNeed_serializer.is_valid():
    #                         trainingNeed_serializer.save()
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
        #query.add(Q(isActive=True), Q.AND)
        if area is not None and area>0:
            query.add(Q(areaxposition__area__id = area), Q.AND)
        if position is not None and position>0:
            query.add(Q(areaxposition__position__id = position), Q.AND)
        areaPositionCapacity = CompetencyxAreaxPosition.objects.filter(query).values('id','competency__id','competency__name','areaxposition__area__id','areaxposition__area__name','areaxposition__position__id','areaxposition__position__name','scale')
        return Response(list(areaPositionCapacity), status = status.HTTP_200_OK)
    
class SearchCapacityEmployeeView(APIView):
    def post(self, request):
        employee = request.data["empleado"]
        query = Q()
        query.add(Q(isActive=True), Q.AND)
        if employee is not None and employee>0:
            query.add(Q(employee__id = employee), Q.AND)
        employeeCompetence = CompetencessXEmployeeXLearningPath.objects.filter(query)
        employeeCompetence_serializer = CompetenceEmployeeReadLearningSerializer(employeeCompetence, many=True)
        return Response(employeeCompetence_serializer, status = status.HTTP_200_OK)
    
class SearchNeedView(APIView):
    def post(self, request):
        employee = request.data["empleado"]
        query = Q()
        query.add(Q(isActive=True), Q.AND)
        if employee is not None and employee>0:
            query.add(Q(employee__id = employee), Q.AND)
        necesidades = TrainingNeed.objects.filter(query).values('id','competence__id','competence__name','employee__id','description','state','levelCurrent','levelRequired','levelGap','type','active','score')
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
    
class EmployeePositionView(APIView):
    def post(self, request):
        area = request.data["area"]
        query = Q()
        query.add(Q(isActive=True), Q.AND)
        if area is not None and area>0:
            query.add(Q(area__id = area), Q.AND)
        positions = AreaxPosicion.objects.filter(query).values('position__id','position__name')
        return Response(list(positions), status = status.HTTP_200_OK)

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
        employees = request.data["empleados"]
        query = Q()
        ids = []
        
        if employees:
            for item in employees:
                ids.append(item['empleado'])
        else:
            if area is not None and area > 0:
                query.add(Q(area__id=area), Q.AND)
            if position is not None and position > 0:
                query.add(Q(position__id=position), Q.AND)
            employeesList = Employee.objects.filter(query).values('id')
            for item in employeesList:
                ids.append(item['id'])

        needs = TrainingNeed.objects.filter(Q(employee__id__in =ids) & Q(state='Por solucionar')).values('competence__id')
        needsUnique = GetUniqueDictionaries(needs)
		
        resultList = []
		
        for need in needsUnique:
            count = TrainingNeed.objects.filter(Q(employee__id__in =ids) & Q(state='Por solucionar') & Q(competence__id = need['competence__id']) ).count()
            fields = {'competencia': need['competence__id'], 'cantidad': count}
            resultList.append(fields)
			
        return Response(resultList, status = status.HTTP_200_OK)    

class GenerateTrainingNeedCourseView(APIView):
    def post(self, request):
        competences = request.data
        coursesList = []
        for item in competences:
            #cambiar segun como se va a hacer la relacion entre curso y competencia
            courseRegister = CursoGeneral.objects.filter(Q(competence__id=item['competencia'])).values().first()
            if courseRegister:
                entry = {"competencia": item['competencia']}
                for entryList in coursesList:
                    if entryList['curso'] == courseRegister['id']:
                        entryList['competencias'].append(entry)
                        break
                coursesList.append({"curso": courseRegister['id'], "competencias": [entry]})
        return Response(coursesList, status = status.HTTP_200_OK)                    
                
class TrainingNeedCourseView(APIView):
    def post(self, request):
        area = request.data["area"]
        position = request.data["posicion"]
        employees = request.data["empleados"]
        query = Q()
        ids = []
        courses = request.data["cursos"]
		
        if employees:
            for item in employees:
                ids.append(item['empleado'])
        else:
            if area is not None and area > 0:
                query.add(Q(area__id=area), Q.AND)
            if position is not None and position > 0:
                query.add(Q(position__id=position), Q.AND)
            employeesList = Employee.objects.filter(query).values('id')
            for item in employeesList:
                ids.append(item['id'])
		
        for course in courses :
            for competence in course['competencias']:
                #ver bien el update()
                TrainingNeed.objects.filter(Q(employee__id__in =ids) & Q(state='Por solucionar') & Q(competence__id= competence['competencia'])).update(course=course['curso'], state='En proceso')
        
        return Response(status=status.HTTP_200_OK,
                        data={
                            'message': 'cursos cargados correctamente',
                        },)	
    
class SearchTrainingNeedCourseView(APIView):
    def post(self, request):
        area = request.data["area"]
        position = request.data["posicion"]
        employees = request.data["empleados"]
        query = Q()
		
        if employees:
            for item in employees:
                item['empleado'] = item.pop('id')
        else:
            if area is not None and area > 0:
                query.add(Q(area__id=area), Q.AND)
            if position is not None and position > 0:
                query.add(Q(position__id=position), Q.AND)
            employees = Employee.objects.filter(query).values('id')
        
        returnList = []
		
        for employee in employees:
            employeeFields = {"empleado": employee['id'], "cursos": []}
            courses = TrainingNeed.objects.filter(Q(employee__id = employee['id']) & Q(state='En proceso')).values('course__id','course__nombre')
            coursesUnique = GetUniqueDictionaries(courses)
            for course in coursesUnique:
                courseFields = {'curso': course['course__id'], 'curso_nombre': course['course__nombre'], 'competencias': []}
                needs = TrainingNeed.objects.filter(Q(employee__id = employee['id']) & Q(state='En proceso') & Q(course__id = course['course__id'])).values('competence__id', 'competence__name')
                for need in needs :
                    needField = {'competencia': need['competence__id'], 'competencia_nombre': need['competence__name']}
                    courseFields['competencias'].append(needField)
                employeeFields['cursos'].append(courseFields)
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

class AcceptOrDeclineJobOfferPreRegistered(APIView):

    def post(self, request):

        offer = request.data['oferta']
        employee = request.data['empleado']
        accept = request.data['acepta']

        query = Q()
        if accept == 0:# eliminamos la notificacion de la oferta laboral.
            if employee is not None and employee > 0 and offer is not None and offer > 0:
                # Primero, tenemos que hallar el hiring process adecuado
                query.add(Q(job_offer__id = offer), Q.AND)
                query.add(Q(employee__id = employee))
                # Una vez que tenemos el query armado, obtenemos la notificacion de la oferta laboral
                job_offer_notification = JobOfferNotification.objects.get(query)
                # Luego, toca eliminarlo
                try:
                    job_offer_notification.delete()
                    Response("Postulación retirada correctamente",status=status.HTTP_200_OK)
                except Exception as e:
                    return Response(str(e),status=status.HTTP_400_BAD_REQUEST)    
        else: # Si ahora queremos insertar esta informacion en la tabla EmployeexHiringProcess
            json_data = {}
            json_data['employee'] = employee
            # Tenemos que obtener el hiring process, dentro del job offer
            # nostros ya tenemos la oferta laboral, falta ver 
            query.add(Q(job_offer__id = offer))
            job_offer = JobOffer.objects.get(query)
            hiring_process = job_offer.hiring_process
            hiring_process_id = hiring_process.id
            json_data['hiring_process'] = hiring_process_id
            current_datetime = timezone.now()
            json_data['creation_date'] = current_datetime
            json_data['modified_date'] = current_datetime
            json_data['is_active'] = True
            try:
                serializer = EmployeeXHiringProcess(data = json_data)
                serializer.is_valid(raise_exception = True)
                serializer.save()
            except Exception as e:
                return Response(str(e),status=status.HTTP_400_BAD_REQUEST)
            return Response("Postulación registrada correctamente",status=status.HTTP_200_OK)
        

class SearchEmployeeSuggestedXJobOffer(APIView):

    def post(self, request):
        offer = request.data['oferta']
        query = Q()
        if offer is not None and offer > 0:
            query.add(Q(job_offer__id = offer))# obtenemos la oferta laboral
            job_offer = JobOffer.objects.get(query)
            hiring_process = job_offer.hiring_process
            position = hiring_process.position
            position_id = position.id
            query = Q()
            query.add(Q(position__id = position_id))
            area_position = AreaxPosicion.objects.get(query)
            area_position_id = area_position.id
            query = Q()
            query.add(Q(positionArea__id = area_position_id))
            capacity_area_position = CapacityXAreaXPosition.objects.get(query)
            capacity = capacity_area_position.capacity
            capacity_id = capacity.id
            query = Q()
            query.add(Q(capacity__id = capacity_id))
            array = CapacityXEmployee.objects.filter(query)
            # entonces, ahora si podemos crear el response
            response_data = []
            for obj in array:
                query = Q()
                emp_id = obj.employee.id
                employee = Employee.objects.filter(id = emp_id).values("id, user__first_name, user__last_name, position__name, area__name, user__email, user__is_active")
                json_data = serializers.serialize('json', employee)
                response_data.append(json_data)

            return Response(response_data, status = status.HTTP_200_OK) 
        else:
            return Response("La oferta laborarl no existe",status=status.HTTP_400_BAD_REQUEST)  