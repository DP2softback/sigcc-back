from django.db import models
from personal.models import *
from login.models import Employee
from capacitaciones.models import CursoGeneral

# Create your models here.

class CapacityType(models.Model):
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
        if self.upperType == None:
            depth = 0
        return depth
    
class Capacity(models.Model):
    id = models.BigAutoField(primary_key = True)
    code = models.CharField(max_length=12, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=300, blank=True, null=True)
    active = models.BooleanField(default=True)
    type = models.ForeignKey(CapacityType, on_delete=models.CASCADE, null=True, blank=True)

# class CompetenceScale(models.Model):
#     id = models.BigAutoField(primary_key = True)
#     competence = models.ForeignKey(Capacity, on_delete=models.CASCADE, null=True, blank=True)
#     descriptor = models.CharField(max_length=100, blank=True, null=True)
#     level = models.IntegerField(blank=True,null =True)
#     active = models.BooleanField(default=True)
	
class CapacityXAreaXPosition(models.Model):
    id = models.BigAutoField(primary_key=True)
    capacity = models.ForeignKey(Capacity, on_delete=models.CASCADE, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)    
    levelRequired = models.CharField(max_length=200, blank=True, null=True)    
    active = models.BooleanField(default=True)

class CapacityXEmployee(models.Model):
    id = models.BigAutoField(primary_key=True)
    capacity = models.ForeignKey(Capacity, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    levelCurrent = models.CharField(max_length=200, blank=True, null=True)
    levelRequired = models.CharField(max_length=200, blank=True, null=True)
    score = models.IntegerField(blank=True,null =True)
    levelGap = models.IntegerField(blank=True,null =True) #cuanta nota necesita para alcanzar desde levelCurrent hast levelRequired
    likeness = models.FloatField(blank=True,null =True)
    hasCertificate = models.BooleanField(default=False)
    registerByEmployee = models.BooleanField(default=False)
    requiredForPosition = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

class TrainingNeed(models.Model):
    id = models.BigAutoField(primary_key=True)
    capacity = models.ForeignKey(Capacity, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(CursoGeneral, on_delete=models.CASCADE, null=True, blank=True, default=None)
    description = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)  #por solucionar, en proceso, solucionado 
    levelCurrent = models.CharField(max_length=200, blank=True, null=True)
    levelRequired = models.CharField(max_length=200, blank=True, null=True)
    score = models.IntegerField(blank=True,null =True)
    levelGap = models.IntegerField(blank=True,null =True) #cuanta nota necesita para alcanzar desde levelCurrent hast levelRequired
    type = models.CharField(max_length=200, blank=True, null=True) # de incorporacion, de evaluacion 2, de ascenso
    active = models.BooleanField(default=True)


