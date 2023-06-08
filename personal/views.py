from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import *
from django.db import transaction


# Create your views here.
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
        process_stages_data = request.data.get('process_stages', [])
        process_stage_serializer = ProcessStageSerializer(data=process_stages_data, many=True)
        for stage_data in process_stages_data:
            stage_data['hiring_process'] = hiring_process.id
        if process_stage_serializer.is_valid(): #If it fails here, atomicity is compromised :(  
            process_stage_serializer.save()
            return Response(hp_serializer.data, status=status.HTTP_201_CREATED)

        return Response(process_stage_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
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

