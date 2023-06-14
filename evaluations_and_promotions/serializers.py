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

class EvaluationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationType
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        depth = 1
        fields = '__all__'




class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    isActive = serializers.BooleanField(read_only=True)
    creationDate = serializers.DateField(read_only=True)
    modifiedDate = serializers.DateField(read_only=True)
    class Meta:
        model = Category
        fields = '__all__'

class AreaxPosicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaxPosicion
        fields = '__all__'
        
class EvaluationSerializer(serializers.ModelSerializer):
    # evaluator = EmployeeSerializer()
    # evaluated = EmployeeSerializer()
    # evaluationType = EvaluationTypeSerializer()
    # areaxPosicion = AreaxPosicionSerializer()
    class Meta:
        model = Evaluation
        fields = '__all__'

class EvaluationxSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationxSubCategory
        fields = '__all__'
class CategoryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id','name')
class SubcategoryCategoryNameSerializer(serializers.ModelSerializer):
    category = CategoryNameSerializer()
    class Meta:
        model =SubCategory
        fields = ('id','category')
class EvaluationIdSerializer(serializers.ModelSerializer):
    class Meta:
        model= Evaluation
        fields=  ['id']
class ContinuousEvaluationIntermediateSerializer(serializers.ModelSerializer):
    subCategory = SubcategoryCategoryNameSerializer()
    evaluation = EvaluationIdSerializer()
    class Meta:
        model= EvaluationxSubCategory
        fields = ('subCategory','score','evaluation')
class PerformanceEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model= Evaluation
        fields=('evaluationDate','finalScore')


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'

class EvaluationSerializerWrite(serializers.ModelSerializer):
    # evaluator = EmployeeSerializer()
    # evaluated = EmployeeSerializer()
    # evaluationType = EvaluationTypeSerializer()
    # areaxPosicion = AreaxPosicionSerializer()
    class Meta:
        model = Evaluation
        fields = '__all__'

class CategorySerialiazerRead(DynamicFieldsModelSerializer):
    class Meta:
        model = CategorySerializer
        fields = '__all__'


class EvaluationSerializerRead(DynamicFieldsModelSerializer):
    #category = CategorySerialiazerRead()
    

    class Meta:
        model = Evaluation
        fields = '__all__'   



##API LINECHART NO MOVER
class CategorySerializerRead(DynamicFieldsModelSerializer):
    #category = CategorySerialiazerRead()
    

    class Meta:
        model = Category
        fields = '__all__'   

class SubCategorySerializerRead(DynamicFieldsModelSerializer):
    category = CategoryNameSerializer()
    class Meta:
        model =SubCategory
        fields = '__all__' 

    def get_category(self, obj):
        category = obj.category
        category_serializer = CategorySerializerRead(category,fields=('id','name'))
        return category_serializer.data    

class EvaluationxSubCategoryRead(DynamicFieldsModelSerializer):
    evaluation = serializers.SerializerMethodField()    
    subCategory = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationxSubCategory
        fields = '__all__'
    
    def get_evaluation(self, obj):
        evaluation = obj.evaluation
        evaluation_serializer = EvaluationSerializerRead(evaluation,fields=('id','evaluationDate','finalScore'))
        return evaluation_serializer.data
    
    def get_subCategory(self, obj):
        subCategory = obj.subCategory
        subCategory_serializer = SubCategorySerializerRead(subCategory,fields=('id','name','category'))
        return subCategory_serializer.data
        



class EvaluationTypeSerializerRead(DynamicFieldsModelSerializer):
    class Meta:
        model = EvaluationType
        fields = '__all__'

class PlantillaSerializerRead(DynamicFieldsModelSerializer):
    evaluationType = serializers.SerializerMethodField()   
    

    class Meta:
        model = Plantilla
        fields = '__all__'   

    def get_evaluationType(self, obj):
        evaluationType = obj.evaluationType
        evaluationType_serializer = EvaluationTypeSerializerRead(evaluationType,fields=('id','name'))
        return evaluationType_serializer.data    

class PlantillaxSubCategoryRead(DynamicFieldsModelSerializer):
    plantilla = serializers.SerializerMethodField()    
    subCategory = serializers.SerializerMethodField()
    
    class Meta:
        model = PlantillaxSubCategoria
        fields = '__all__'
    
    def get_plantilla(self, obj):
        plantilla = obj.plantilla
        plantilla_serializer = PlantillaSerializerRead(plantilla,fields=('id','nombre','evaluationType','image'))
        return plantilla_serializer.data
    
    def get_subCategory(self, obj):
        subCategory = obj.subCategory
        subCategory_serializer = SubCategorySerializerRead(subCategory,fields=('id','name','category'))
        return subCategory_serializer.data   
       
class CategorySerializerRead2(DynamicFieldsModelSerializer):
    evaluationType = serializers.SerializerMethodField()  
    
    class Meta:
        model = Category
        fields = '__all__' 

    def get_evaluationType(self, obj):
        evaluationType = obj.evaluationType
        evaluationType_serializer = EvaluationTypeSerializerRead(evaluationType,fields=('id','name'))
        return evaluationType_serializer.data