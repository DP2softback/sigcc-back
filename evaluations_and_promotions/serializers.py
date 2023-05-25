from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from evaluations_and_promotions.models import *
from login.serializers import *

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class EvaluationTypeSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
    class Meta:
        model = EvaluationType
        fields = '__all__'

class EmployeeSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class PositionSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'

class AreaSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'

class CategorySerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
    isActive = serializers.BooleanField(read_only=True)
    creationDate = serializers.DateField(read_only=True)
    modifiedDate = serializers.DateField(read_only=True)
    class Meta:
        model = Category
        fields = '__all__'

class AreaxPosicionSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
    class Meta:
        model = AreaxPosicion
        fields = '__all__'
        
class EvaluationSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
    evaluator = EmployeeSerializer()
    evaluated = EmployeeSerializer()
    evaluationType = EvaluationTypeSerializer()
    areaxPosicion = AreaxPosicionSerializer()
    class Meta:
        model = Evaluation
        fields = '__all__'

class SubCategorySerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'

class EvaluationxSubCategorySerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
    class Meta:
        model = EvaluationxSubCategory
        fields = '__all__'


