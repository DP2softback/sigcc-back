from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from login.models import *

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

class UserSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class EmployeeSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class RoleSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'