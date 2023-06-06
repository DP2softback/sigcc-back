from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import *


# Create your views here.
class HiringProcessView(APIView):
    def get(self, request):
        hps= HiringProcess.objects.all() #should be just active ones and may be by some extra criteria...
        hps_serializer = HiringProcessSerializer(hps, many=True)

        return Response(hps_serializer.data, status = status.HTTP_200_OK)
    
    def post(self, request, id=0):
        hp_serializer = HiringProcessSerializer(data = request.data, context = request.data)
        if hp_serializer.is_valid():
            hp_serializer.save()
            return Response(hp_serializer.data,status=status.HTTP_201_CREATED)
        return Response(hp_serializer.errors,status=status.HTTP_400_BAD_REQUEST)


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

