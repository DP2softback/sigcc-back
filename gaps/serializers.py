from rest_framework import serializers
from gaps.models import Competencia, CompetenciaXAreaXPosicion, CompetenciaXEmpleado, NecesidadCapacitacion
from evaluations_and_promotions.serializers import AreaSerializer, PositionSerializer, EmployeeSerializer
class CompetenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competencia
        fields = '__all__'
		
class CompetenciaXAreaXPosicionSerializer(serializers.ModelSerializer):
    posicion = PositionSerializer()
    area = AreaSerializer()
    class Meta:
        model = CompetenciaXAreaXPosicion
        fields = '__all__'

class CompetenciaXEmpleadoSerializer(serializers.ModelSerializer):
    empleado = EmployeeSerializer()
    class Meta:
        model = CompetenciaXEmpleado
        fields = '__all__'

class NecesidadCapacitacionSerializer(serializers.ModelSerializer):
    empleado = EmployeeSerializer()
    class Meta:
        model = NecesidadCapacitacion
        fields = '__all__'