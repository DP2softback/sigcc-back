from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from login.models import *

# class DynamicFieldsModelSerializer(serializers.ModelSerializer):
#     """
#     A ModelSerializer that takes an additional `fields` argument that
#     controls which fields should be displayed.
#     """

#     def __init__(self, *args, **kwargs):
#         # Don't pass the 'fields' arg up to the superclass
#         fields = kwargs.pop('fields', None)

#         # Instantiate the superclass normally
#         super().__init__(*args, **kwargs)

#         if fields is not None:
#             # Drop any fields that are not specified in the `fields` argument.
#             allowed = set(fields)
#             existing = set(self.fields)
#             for field_name in existing - allowed:
#                 self.fields.pop(field_name)

class UserSerializerRead(serializers.ModelSerializer):
    class Meta:
        model = User
        depth = 1
        fields =  ['id', 'creationDate', 'modifiedDate', 'isActive', 'username', 'firstName', 'secondName', 'lastName', 'maidenName', 'email', 'password', 'role']

class UserSerializerWrite(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =  ['id', 'creationDate', 'modifiedDate', 'isActive', 'username', 'firstName', 'secondName', 'lastName', 'maidenName', 'email', 'password', 'role']

class EmployeeSerializerRead(serializers.ModelSerializer):
    class Meta:
        model = Employee
        depth = 1
        fields = '__all__'

class EmployeeSerializerWrite(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class RoleSerializerRead(serializers.ModelSerializer):
    class Meta:
        model = Role
        depth = 1
        fields = '__all__'

class RoleSerializerWrite(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'