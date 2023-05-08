from rest_framework import serializers

from capacitaciones.models import LearningPath, CursoGeneral, CursoGeneralXLearningPath, CursoUdemy, CursoEmpresa

from django.utils import timezone

class LearningPathSerializer(serializers.ModelSerializer):

    class Meta:
        model = LearningPath
        fields = '__all__'

    def validate_nombre(self, value):
        if value == '':
            raise serializers.ValidationError('El nombre no puede ser valor vacío')
        return value

    def validate_descripcion(self, value):
        if self.validate_nombre(self.context['nombre']) == value:
            raise serializers.ValidationError('La descripcion no puede ser igual al nombre')
        return value


class CursoUdemySerializer(serializers.ModelSerializer):

    class Meta:
        model = CursoUdemy
        exclude = ('curso_x_learning_path',)

    def validate_udemy_id(self, value):

        if value == '':
            raise serializers.ValidationError('El valor de este campo no puede ser vacio')

        return value


class LearningPathSerializerWithCourses(serializers.ModelSerializer):

    curso_x_learning_path = serializers.SerializerMethodField()

    class Meta:
        model = LearningPath
        fields = '__all__'

    def get_curso_x_learning_path(self, obj):
        cursos_id = CursoGeneralXLearningPath.objects.filter(learning_path=obj).values_list('curso_id', flat=True)
        cursos = CursoUdemy.objects.filter(id__in=cursos_id)
        return CursoUdemySerializer(cursos, many=True).data


class CursoEmpresaSerializer(serializers.ModelSerializer):

    class Meta:
        model = CursoEmpresa
        fields = '__all__'

    def validate_nombre(self, value):
        if value == '':
            raise serializers.ValidationError('El nombre no puede ser valor vacío')
        return value

    def validate_descripcion(self, value):
        if self.validate_nombre(self.context['nombre']) == value:
            raise serializers.ValidationError('La descripcion no puede ser igual al nombre')
        return value

    def validate_asunto(self, value):

        if self.validate_descripcion(self.context['descripcion']) == value:
            raise serializers.ValidationError('El asunto no puede ser igual a la descripcion')
        return value

    def validate_fecha(self, value):
        fecha_actual = timezone.now()
        if value <= fecha_actual:
            raise serializers.ValidationError('La fecha debe ser mayor a la fecha de la peticion')
        return value