from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from zappa.asynchronous import task
from .models import JobOffer

class JobOfferView(APIView):
    def get(self, request):
        jobOffers = JobOffer.objects.values()
        list_result = [entry for entry in jobOffers]

        response = Response(
            data={
                'title': '¡Listo!',
                'message': 'Lista de ofertas laborales',
                'offers': list_result,

            },
            status=status.HTTP_200_OK,
        )

        return response

    def post(self, request):
        offerData = request.data
        # newOffer = JobOffer.objects.create()
        # newOffer.save()

        response = Response(
            data={
                'title': '¡Listo!',
                'message': 'Oferta registrada',

            },
            status=status.HTTP_200_OK,
        )

        return response

