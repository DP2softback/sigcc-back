from django.db import models
from evaluations_and_promotions.models import Area, Position
from login.models import Employee

# Create your models here.

class CompetenceType(models.Model):
    id = models.BigAutoField(primary_key=True)
    abbreviation = models.CharField(max_length=30, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=300, blank=True, null=True)
    active = models.BooleanField(default=True)
    upperType = models.ForeignKey('self', blank=True,null = True, on_delete=models.CASCADE)
    export_fields = [
        'id',
        'abbreviation',
        'name',
        'description',
        'active'
    ]
          
    def get_depth(self):
        depth = 0
        obj = self
        while obj.upperType:
            print("entro en el while")
            depth += 1
            obj = obj.upperType
        return depth
    
class Competence(models.Model):
    id = models.BigAutoField(primary_key = True)
    code = models.CharField(max_length=12, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=300, blank=True, null=True)
    active = models.BooleanField(default=True)
    type = models.ForeignKey(CompetenceType, on_delete=models.CASCADE, null=True, blank=True)
	
class CompetenceXAreaXPosition(models.Model):
    id = models.BigAutoField(primary_key=True)
    competence = models.ForeignKey(Competence, on_delete=models.CASCADE, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    levelRequired = models.IntegerField(blank=True,null =True)
    active = models.BooleanField(default=True)

class CompetenceXEmployee(models.Model):
    id = models.BigAutoField(primary_key=True)
    competence = models.ForeignKey(Competence, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    levelCurrent = models.IntegerField(blank=True,null =True)
    levelRequired = models.IntegerField(blank=True,null =True)
    levelGap = models.IntegerField(blank=True,null =True)
    likeness = models.FloatField(blank=True,null =True)
    hasCertificate = models.BooleanField(default=False)
    registerByEmployee = models.BooleanField(default=False)
    requiredForPosition = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

class TrainingNeed(models.Model):
    id = models.BigAutoField(primary_key=True)
    competence = models.ForeignKey(Competence, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    state = models.IntegerField(blank=True,null =True)  #1: por solucionar, 2: en proceso, 3: solucionado 
    levelCurrent = models.IntegerField(blank=True,null =True)
    levelRequired = models.IntegerField(blank=True,null =True)
    levelGap = models.IntegerField(blank=True,null =True) #1: brecha de nivel 1, 2: brecha de nivel 2, 3: brecha de nivel 3, 4: brecha de nivel 4
    type = models.IntegerField(blank=True,null =True) #1: de incorporacion, 2: de evaluacion 2, 3: de ascenso
    active = models.BooleanField(default=True)


