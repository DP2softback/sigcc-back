from rest_framework import serializers
from gaps.models import Capacity, CapacityXAreaXPosition, CapacityXEmployee, TrainingNeed, CapacityType
from personal.models import Area, Position, AreaxPosicion
from evaluations_and_promotions.serializers import AreaSerializer, PositionSerializer, EmployeeSerializer

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