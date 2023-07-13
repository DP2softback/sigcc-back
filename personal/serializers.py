from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from DP2softback.constants import messages
from evaluations_and_promotions.models import *
from evaluations_and_promotions.serializers import *
from gaps.serializers import *
from login.models import *
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .models import *
from .serializers import *


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


class HiringProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiringProcess
        fields = '__all__'


class EmployeeXHiringProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeXHiringProcess
        fields = '__all__'


class StageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StageType
        fields = '__all__'


class ProcessStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessStage
        fields = '__all__'


class JobOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOffer
        fields = '__all__'


class JobOfferSerializerRead(serializers.ModelSerializer):

    def my_training(self, obj):
        training = TrainingxAreaxPosition.objects.filter(areaxposition_id=obj.hiring_process.position_id)
        training_list = messages.TRAINING_INTRODUCTION
        for t in training:
            training_list += t.to_str() + '\n'

        print(training_list)
        return training_list

    training_detail = serializers.SerializerMethodField('my_training')
    position_name = serializers.CharField(source="hiring_process.position.position.name")
    position_id = serializers.CharField(source="hiring_process.position.position.id")

    class Meta:
        model = JobOffer
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'


class FunctionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Functions
        fields = '__all__'


class JobOfferNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOfferNotification
        fields = '__all__'


class TrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        fields = '__all__'


class TrainingxLevelSerializer(serializers.ModelSerializer):

    def my_training(self, obj):
        training = Training.objects.get(id=obj.training_id)
        return str(training.name)

    def my_level(self, obj):
        level = TrainingLevel.objects.get(id=obj.level_id)
        return str(level.name)

    def my_training_str(self, obj):
        training = TrainingxLevel.objects.get(id=obj.id)
        print(training)
        return str(training)

    training_detail = serializers.SerializerMethodField('my_training')
    level_detail = serializers.SerializerMethodField('my_level')
    training_literal = serializers.SerializerMethodField('my_training_str')

    class Meta:
        model = TrainingxLevel
        fields = '__all__'


class TrainingxAreaxPositionSerializer(serializers.ModelSerializer):
    def my_training(self, obj):
        training = TrainingxLevel.objects.get(id=obj.training_id)
        print(training)
        return str(training)

    position_detail = serializers.SerializerMethodField('my_training')

    class Meta:
        model = TrainingxAreaxPosition
        fields = ['id',
                  'position_detail',
                  'score',
                  'training',
                  'areaxposition',
                  ]


class AreaxPositionSerializer(serializers.ModelSerializer):

    def my_position(self, obj):
        positions = Position.objects.get(id=obj.position_id)
        return PositionSerializer(positions, many=False).data

    def my_area(self, obj):
        areas = Area.objects.get(id=obj.area_id)
        return AreaSerializer(areas, many=False).data

    def my_competencies(self, obj):
        competencies = CompetencyxAreaxPosition.objects.filter(areaxposition=obj.id)
        return CompetencyxAreaxPositionSerializerRead(competencies, many=True).data

    def my_training(self, obj):
        training = TrainingxAreaxPosition.objects.filter(areaxposition=obj.id)
        return TrainingxAreaxPositionSerializer(training, many=True).data

    def my_functions(self, obj):
        functions = Functions.objects.filter(areaxposition=obj.id)
        return FunctionsSerializer(functions, many=True).data

    position_detail = serializers.SerializerMethodField('my_position')
    area_detail = serializers.SerializerMethodField('my_area')
    position_name = serializers.CharField(source='position.name')
    area_name = serializers.CharField(source='area.name')
    competencies_detail = serializers.SerializerMethodField('my_competencies')
    training_detail = serializers.SerializerMethodField('my_training')
    function_detail = serializers.SerializerMethodField('my_functions')

    class Meta:
        model = AreaxPosicion
        fields = ['id',
                  'isActive',
                  'availableQuantity',
                  'unavailableQuantity',
                  'area',
                  'area_name',
                  'area_detail',
                  'position',
                  'position_name',
                  'position_detail',
                  'competencies_detail',
                  'training_detail',
                  'function_detail'
                  ]


####

class TrainingxApplicantSerializerRead(serializers.ModelSerializer):

    def my_training(self, obj):
        training = TrainingxLevel.objects.get(id=obj.trainingxlevel_id)
        print(training)
        return str(training)

    training_detail = serializers.SerializerMethodField('my_training')

    class Meta:
        model = TrainingxApplicant
        fields = [
            'training_detail',
            'trainingxlevel',
            'applicant'
        ]


class ExperienceSerializerRead(serializers.ModelSerializer):

    class Meta:
        model = Experience
        fields = '__all__'


class ApplicantSerializerRead(serializers.ModelSerializer):

    def my_user(self, obj):
        user = User.objects.get(id=obj.user.id)
        return UserSerializerRead(user, many=False).data

    user = serializers.SerializerMethodField('my_user')

    class Meta:
        model = Applicant
        fields = '__all__'

class CompetenceEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetenceEvaluation
        fields = '__all__'