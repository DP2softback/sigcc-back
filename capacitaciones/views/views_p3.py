# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoUdemy
from capacitaciones.serializers import LearningPathSerializer,  CursoUdemySerializer


from django.db import transaction

class LearningPathCreateFromTemplateAPIView(APIView):

    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        lp_serializer = LearningPathSerializer(data=request.data,context=request.data)
        print("wenas")
        if lp_serializer.is_valid():
            lp = lp_serializer.save()

            for curso_lp in request.data['cursos']:
                print(curso_lp)
                curso_serializer = CursoUdemySerializer(data=curso_lp)

                if curso_serializer.is_valid():
                    curso = CursoUdemy.objects.filter(udemy_id=curso_lp['udemy_id']).first()
                    if curso is None:
                        curso = curso_serializer.save()

                    CursoGeneralXLearningPath.objects.create(curso=curso, learning_path=lp)
                else:
                    return Response({"message": "No se pudo crear el curso {}".format(curso_lp['nombre'])}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Se ha creado el learning path con exito"}, status=status.HTTP_200_OK)

        else:
            return Response({"message": "No se pudo crear el learning path"}, status=status.HTTP_400_BAD_REQUEST)
