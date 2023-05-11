from rest_framework import serializers
from offers.models import CompetencyType, Competency, JobOffer, JobOfferxUser, OfferNotification, AreaxPositionxCompetency, EmployeexCompetency

class CompetencyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetencyType
        fields = '__all__'

class CompetencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Competency
        fields = '__all__'

class JobOfferSerializer(serializers.ModelSerializer):
    #position = 
    #area = 
    #candidates = 
    class Meta:
        model = JobOffer
        fields = '__all__'

class JobOfferxUserSerializer(serializers.ModelSerializer):
    #user = 
    class Meta:
        model = JobOfferxUser
        fields = '__all__'

class OfferNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferNotification
        fields = '__all__'

class AreaxPositionxCompetencySerializer(serializers.ModelSerializer):
    #position =
    #area =
    class Meta:
        model = AreaxPositionxCompetency
        fields = '__all__'

class EmployeexCompetencySerializer(serializers.ModelSerializer):
    #employee =
    class Meta:
        model = EmployeexCompetency
        fields = '__all__'