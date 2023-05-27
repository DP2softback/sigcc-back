# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoUdemy, ProveedorEmpresa, Habilidad, \
    ProveedorUsuario, HabilidadXProveedorUsuario
from capacitaciones.serializers import LearningPathSerializer, CursoUdemySerializer, ProveedorUsuarioSerializer
from capacitaciones.models import LearningPath, CursoGeneralXLearningPath, CursoUdemy, Sesion, Tema, Categoria
from capacitaciones.serializers import LearningPathSerializer, CursoUdemySerializer, SesionSerializer, TemaSerializer, CategoriaSerializer, ProveedorEmpresaSerializer,HabilidadSerializer

from django.db import transaction
from rest_framework.permissions import AllowAny
from django.db.models import Q

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


class CategoriaAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categorias = Categoria.objects.all()
        categorias_serializer = CategoriaSerializer(categorias, many=True)

        return Response(categorias_serializer.data, status = status.HTTP_200_OK)


class ProveedorEmpresaXCategoriaAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        proveedor_empresas = ProveedorEmpresa.objects.filter(categoria=pk).all()
        proveedor_serializer = ProveedorEmpresaSerializer(proveedor_empresas, many=True)

        return Response(proveedor_serializer.data, status=status.HTTP_200_OK)


class HabilidadesXEmpresaAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        usuarios = ProveedorUsuario.objects.filter(empresa=pk).all()
        habilidades_id = HabilidadXProveedorUsuario.objects.filter(proveedor_usuario__in=usuarios).values_list('habilidad_id', flat=True)
        habilidades = Habilidad.objects.filter(id__in=habilidades_id)
        habilidades_serializer = HabilidadSerializer(habilidades, many=True)

        return Response(habilidades_serializer.data, status=status.HTTP_200_OK)

class PersonasXHabilidadesXEmpresaAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        id_proveedor = request.data.get('id_proveedor',None)
        id_habilidades = request.data.get('habilidades', None)
        usuarios_proveedor = ProveedorUsuario.objects.filter(Q(id__in=id_habilidades) & Q(empresa=id_proveedor))
        usuarios_proveedor_serializer = ProveedorUsuarioSerializer(usuarios_proveedor, many=True)

        return Response(usuarios_proveedor_serializer.data, status=status.HTTP_200_OK)


class SesionAPIView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        sesiones_emp = Sesion.objects.all()
        sesiones_emp_serializer = SesionSerializer(sesiones_emp, many=True)
        return Response(sesiones_emp_serializer.data, status=status.HTTP_200_OK)

    def post(self, request):

        sesiones_emp_serializer = SesionSerializer(data=request.data, context=request.data)

        if sesiones_emp_serializer.is_valid():
            curso_empresa_id = request.data['curso_empresa_id']
            sesiones_emp = sesiones_emp_serializer.save(cursoEmpresa_id=curso_empresa_id)

            for tema_sesion in request.data['temas']:
                print(tema_sesion)
                tema_serializer = TemaSerializer(data=tema_sesion)

                if tema_serializer.is_valid():
                    tema_serializer.validated_data['sesion'] = sesiones_emp
                    tema = Tema.objects.filter(nombre=tema_serializer.validated_data['nombre']).first()
                    if tema is None:
                        tema = tema_serializer.save()
                else:
                    return Response({"message": "No se pudo crear el tema {}".format(tema_sesion['nombre'])},
                                    status=status.HTTP_400_BAD_REQUEST)

            return Response({'id': sesiones_emp.id,
                             'message': 'La sesion se ha con sus temas creado correctamente'},
                            status=status.HTTP_200_OK)

        return Response(sesiones_emp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
