from rest_framework import serializers
from gaps.models import *
from personal.models import *
from evaluations_and_promotions import *
from evaluations_and_promotions.serializers import *

class CapacitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Capacity
        fields = '__all__'
        
class CapacityXAreaXPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapacityXAreaXPosition
        fields = '__all__'

class CapacityXEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapacityXEmployee
        fields = '__all__'

class TrainingNeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingNeed
        fields = '__all__'

class CapacityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapacityType
        fields = '__all__'

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'

class CompetenceReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id','isActive','code','name','description', 'type']

class CompetenceEmployeeReadSerializer(serializers.ModelSerializer):
    competence_code = serializers.CharField(source='competence.code')
    competence_name = serializers.CharField(source='competence.name')
    competence_type = serializers.IntegerField(source='competence.type')
    levelCurrent = serializers.IntegerField(source='scale')
    levelRequired = serializers.IntegerField(source='scaleRequired')
    class Meta:
        model = CompetencessXEmployeeXLearningPath
        fields = ['competence_code','competence_name','competence_type','levelCurrent', 'levelRequired', 'likeness']

class CompetenceEmployeeReadLearningSerializer(serializers.ModelSerializer):
    competencia = serializers.CharField(source='competence.id')
    competencia_nombre = serializers.CharField(source='competence.name')
    competencia_tipo = serializers.IntegerField(source='competence.type')
    nivel = serializers.IntegerField(source='scale')
    nota = serializers.FloatField(source='score')
    modificado = serializers.CharField(source='modifiedBy')
    class Meta:
        model = CompetencessXEmployeeXLearningPath
        fields = ['competencia','competencia_nombre','competencia_tipo','nivel','nota','modificado']

class CompetencyxAreaxPositionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetencyxAreaxPosition
        fields = '__all__'

class TrainingNeedReadSerializer(serializers.ModelSerializer):
    competence_name = serializers.CharField(source='competence.name')
    competence_type = serializers.IntegerField(source='competence.type')
    class Meta:
        model = TrainingNeed
        fields = ['competence_name','competence_type','levelCurrent', 'levelRequired', 'levelGap','description']