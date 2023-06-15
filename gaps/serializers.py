from rest_framework import serializers
from gaps.models import Competence, CompetenceScale,CompetenceXAreaXPosition, CompetenceXEmployee, TrainingNeed, CompetenceType
from personal.models import Area, Position, AreaxPosicion
from evaluations_and_promotions.serializers import AreaSerializer, PositionSerializer, EmployeeSerializer

class CompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competence
        fields = '__all__'
		
class CompetenceScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetenceScale
        fields = '__all__'
        
class CompetenceXAreaXPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetenceXAreaXPosition
        fields = '__all__'

class CompetenceXAreaXPositionSerializerRead(serializers.ModelSerializer):
    
    competence_id = serializers.CharField(source="competence.id")
    competence_name = serializers.CharField(source="competence.name")    
    competence_type_id = serializers.CharField(source="competence.type.id")    
    competence_type_name = serializers.CharField(source="competence.type.name")    
    scalePosition_id = serializers.CharField(source="scalePosition.id")
    scalePosition_name = serializers.CharField(source="scalePosition.descriptor")
    scalePosition_value = serializers.CharField(source="scalePosition.level")
 
    class Meta:
        model = CompetenceXAreaXPosition
        depth = 1
        fields = [
            "id",
            "competence_id",
            "competence_name",
            "competence_type_id",
            "competence_type_name",
            "scalePosition_id",
            "scalePosition_name",
            "scalePosition_value",
            "levelRequired",
            "active"
        ]

class CompetenceXEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetenceXEmployee
        fields = '__all__'

class TrainingNeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingNeed
        fields = '__all__'

class CompetenceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetenceType
        fields = '__all__'

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'