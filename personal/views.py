from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import *
from django.db import transaction
from django.core.serializers import serialize
from gaps.models import *
from evaluations_and_promotions.models import *


class HiringProcessView(APIView):
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        hps= HiringProcess.objects.all() #should be just active ones and may be by some extra criteria...like user
        hps_serializer = HiringProcessSerializer(hps, many=True)

        return Response(hps_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request):
        hp_serializer = HiringProcessSerializer(data=request.data, context=request.data)
        if not hp_serializer.is_valid():
         return Response(hp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        hiring_process = hp_serializer.save()
        
        employees_data = request.data.get('employees', [])
        employee_x_hiring_process_serializer = EmployeeXHiringProcessSerializer(data=employees_data, many=True)
        for employee_data in employees_data:
            employee_data['hiring_process'] = hiring_process.id
        if not employee_x_hiring_process_serializer.is_valid(): #If it fails here, atomicity is compromised :(  
            return Response(employee_x_hiring_process_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        employee_x_hiring_process_serializer.save()

        process_stages_data = request.data.get('process_stages', [])
        process_stage_serializer = ProcessStageSerializer(data=process_stages_data, many=True)
        for stage_data in process_stages_data:
            stage_data['hiring_process'] = hiring_process.id
        if not process_stage_serializer.is_valid(): #If it fails here, atomicity is compromised :(  
            return Response(process_stage_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        process_stage_serializer.save()

        return Response(hp_serializer.data, status=status.HTTP_201_CREATED)

        
    
    def put(self, request, pk):
        hiring_process = HiringProcess.objects.filter(id=pk).first()
        if not hiring_process:
            return Response({'message': 'HiringProcess not found'}, status=status.HTTP_404_NOT_FOUND)

        hp_serializer = HiringProcessSerializer(hiring_process, data=request.data, context=request.data)
        if not hp_serializer.is_valid():
            return Response(hp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        updated_hiring_process = hp_serializer.save()

        process_stages_data = request.data.get('process_stages', [])
        existing_process_stages = updated_hiring_process.process_stages.all()
        existing_process_stages_mapping = {stage.id: stage for stage in existing_process_stages}
        updated_process_stages = []
        created_process_stages = []

        for stage_data in process_stages_data:
            stage_id = stage_data.get('id')
            if stage_id:
                # Update existing process stage
                if stage_id in existing_process_stages_mapping:
                    stage_instance = existing_process_stages_mapping[stage_id]
                    stage_serializer = ProcessStageSerializer(
                        instance=stage_instance,
                        data=stage_data,
                        partial=True
                    )
                    if stage_serializer.is_valid():
                        updated_stage = stage_serializer.save()
                        updated_process_stages.append(updated_stage)
                    else:
                        return Response(stage_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': f"ProcessStage with id '{stage_id}' does not exist"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                # Create new process stage
                stage_data['hiring_process'] = updated_hiring_process.id
                stage_serializer = ProcessStageSerializer(data=stage_data)
                if stage_serializer.is_valid():
                    created_stage = stage_serializer.save()
                    created_process_stages.append(created_stage)
                else:
                    return Response(stage_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Delete any existing process stages that were not included in the request data
        existing_stage_ids = existing_process_stages_mapping.keys()
        stages_to_delete = set(existing_stage_ids) - set([stage.id for stage in updated_process_stages])
        ProcessStage.objects.filter(id__in=stages_to_delete).delete()

        #TODO: Update assigned employees
        return Response({'message': 'HiringProcess and ProcessStages updated successfully'},
                        status=status.HTTP_200_OK)



class StageTypeView(APIView):
    def get(self, request):
        sts= StageType.objects.all() 
        st_serializer = StageTypeSerializer(sts, many=True)

        return Response(st_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request, id=0):
        st_serializer = StageTypeSerializer(data = request.data, context = request.data)
        if st_serializer.is_valid():
            st_serializer.save()
            return Response(st_serializer.data,status=status.HTTP_201_CREATED)
        return Response(st_serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class ProcessStageView(APIView):
    def get(self, request):
        hiring_process_id = request.GET.get('hiring_process_id')
        
        if hiring_process_id:
            process_stages = ProcessStage.objects.filter(hiring_process_id=hiring_process_id)
        else:
            process_stages = ProcessStage.objects.all()
        
        process_stage_serializer = ProcessStageSerializer(process_stages, many=True)
        return Response(process_stage_serializer.data, status = status.HTTP_200_OK)

class JobOfferView(APIView):
    def get(self, request):

        queryset = JobOffer.objects.all()
        serializer_class = JobOfferSerializerRead(queryset, many = True)
        return Response(serializer_class.data, status=status.HTTP_200_OK)

    
    def post(self, request, id=0):
        job_offer_serializer = JobOfferSerializer(data=request.data, context=request.data)
        if job_offer_serializer.is_valid():
            job_offer_serializer.save()
            return Response(job_offer_serializer.data, status=status.HTTP_201_CREATED)
        return Response(job_offer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AreaxPositionView(APIView):
    def get(self, request):
        axp= AreaxPosicion.objects.all() 
        axp_serializer = AreaxPositionSerializer(axp, many=True)
        return Response(axp_serializer.data, status = status.HTTP_200_OK)

class PositionView(APIView):
    def get(self, request, pk):
        print(pk)
        positions = Position.objects.filter(id=pk)
        print(positions)
        serializer = PositionSerializer(positions, many=True)

        for position_data in serializer.data:
            print(position_data)
            position_id = position_data['id']            
            functions = Functions.objects.filter(position_id=position_id)
            functions_serializer = FunctionsSerializer(functions, many=True)
            position_data['functions'] = functions_serializer.data
            areasxposition = AreaxPosicion.objects.filter(position_id=position_id)
            areas_serializer = AreaxPositionSerializer(areasxposition, many=True)
            
            areas = []
            for area in areas_serializer.data:
                areas.append((area['id'], area['area_name']))
            
            position_data['areas'] = dict(areas)

        return Response(serializer.data)
    
    def post(self, request):

        print(request.user)
        print(request.data)

        name = request.data["name"]
        description = request.data["description"]
        area = request.data["area"]
        job_modality = request.data["job_modality"]
        workday_type = request.data["workday_type"]

        competencies = request.data["competencies"]            
        capacities = request.data["capacities"]
        training = request.data["training"]

        functions = request.data["responsabilities"]

        # check if all data exits
        try:             
            area = Area.objects.get(id=area)
            #saving every competence, capacity and training
            competency_list=[]
            capacity_list=[]
            training_list=[]
            for com in competencies:
                competencyobj = SubCategory.objects.get(id=com)                
                print(f"Competence: {competencyobj.name}")
                competency_list.append(competencyobj)
            for cap in capacities:
                capacityobj = Capacity.objects.get(id=cap)                
                print(f"Capacity: {capacityobj.name}")
                competency_list.append(capacityobj)
            for tr in training:
                trainingobj = TrainingxLevel.objects.get(id=tr)                
                print(f"Training: {trainingobj.name}")
                competency_list.append(trainingobj)                        

        except Exception as e:
            return Response(data=f"Exception: {e}", status=status.HTTP_404_NOT_FOUND)


        # insert position
        position = Position(
            name = name,
            description = description,
            area=area,
            modalidadTrabajo=job_modality,
            tipoJornada=workday_type,                              
        )    
        position.save()      

        #saving functions
        for function in functions:
            functionobj = Functions.objects.create(
                area=area,
                position=position, 
                description=function
            )
            functionobj.save()
            position.functions_set.add(functionobj)

        #linking position with Area
        areaxposition = AreaxPosicion(area=area, position=position)
        areaxposition.save()

        #linking capacities, competencies and training with position
        for com in competencies:
            obj = CompetencyxAreaxPosition(
                competency=com, 
                areaxposition = areaxposition,
                score='M'
            )
            obj.save()
        #linking capacities, competencies and training with position
        for cap in capacities:
            obj = CapacityXAreaXPosition(
                capacity=cap, 
                positionArea = areaxposition,
                levelRequired='M'
            )
            obj.save()
        #linking capacities, competencies and training with position
        for tr in training:
            obj = TrainingxAreaxPosition(
                training=tr, 
                areaxposition = areaxposition,
                score='M'
            )
            obj.save()                        

        return Response(data=f"Position registered", status=status.HTTP_201_CREATED)
        
    
    def put(self, request, pk):
        position = Position.objects.filter(pk=pk).first()
        if not position:
            return Response({"error": "Position not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PositionSerializer(position, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class FunctionsView(APIView):
    def get(self, request):
        functions = Functions.objects.all()
        serializer = FunctionsSerializer(functions, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = FunctionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        function = Functions.objects.filter(pk=pk).first()
        if not function:
            return Response({"error": "Function not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = FunctionsSerializer(function, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
