from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import *


# Create your views here.
class HiringProcessView(APIView):
    def get(self, request):
        hps= HiringProcess.objects.all() #should be just active ones...
        hps_serializer = HiringProcessSerializer(hps, many=True)

        return Response(hps_serializer.data, status = status.HTTP_200_OK)
