from rest_framework import serializers
from gaps.models import Competence, CompetenceXAreaXPosition, CompetenceXEmployee, TrainingNeed, CompetenceType
from personal.models import Area, Position, AreaxPosicion
from evaluations_and_promotions.serializers import AreaSerializer, PositionSerializer, EmployeeSerializer

class CompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competence
        fields = '__all__'
		
class CompetenceXAreaXPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetenceXAreaXPosition
        fields = '__all__'

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