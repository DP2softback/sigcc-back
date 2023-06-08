from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from login.models import *
from .models import *
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed


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

    position_name = serializers.CharField(source="hiring_process.position.name")
    position_id = serializers.CharField(source="hiring_process.position.id")
    class Meta:

        model = JobOffer
        depth = 1
        fields = [
            'id',
            'hiring_process',
            'position_id',
            'position_name',
            'introduction',
            'offer_introduction',
            'responsabilities_introduction',
            'creation_date',
            'modified_date',
            'photo_url',
            'location',
            'salary_range',
            'is_active'
        ]

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = '__all__'

class FunctionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Functions
        fields = '__all__'
