from rest_framework import serializers

from Cursos.models import LearningPath, Curso, CursoXLearningPath


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


class CursoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Curso
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
        cursos_id = CursoXLearningPath.objects.filter(learning_path=obj).values_list('curso_id', flat=True)
        cursos = Curso.objects.filter(id__in=cursos_id)
        return CursoSerializer(cursos, many=True).data
