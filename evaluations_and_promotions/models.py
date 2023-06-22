from django.db import models

from capacitaciones.models import LearningPath
from login.models import Employee
from personal.models import Area, Position, AreaxPosicion
from model_utils.models import TimeStampedModel
from safedelete.models import SOFT_DELETE, SOFT_DELETE_CASCADE, SafeDeleteModel
from .models import *

# Create your models here.


class EvaluationType(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    name = models.CharField(max_length=40, blank=True)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField()
    modifiedDate = models.DateTimeField()
    isActive = models.BooleanField(default=True)
    name = models.TextField(blank=True, default='')
    code = models.CharField(max_length=5, blank=True)
    description = models.TextField(blank=True, default='')
    evaluationType = models.ForeignKey(EvaluationType, on_delete=models.SET_NULL, null=True)


class Evaluation(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    evaluationDate = models.DateTimeField(null=True)
    hasComment = models.BooleanField()
    generalComment = models.CharField(max_length=500, null=True, blank=True)
    isFinished = models.BooleanField()
    finalScore = models.FloatField(null=True, blank=True)
    evaluator = models.ForeignKey(Employee, related_name="Evaluator", on_delete=models.SET_NULL, blank=True, null=True)
    evaluated = models.ForeignKey(Employee, related_name="Evaluated", on_delete=models.SET_NULL, blank=True, null=True)
    evaluationType = models.ForeignKey(EvaluationType, on_delete=models.CASCADE, null=True)
    area = models.ForeignKey(Area,on_delete=models.SET_NULL, blank=True, null=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, blank=True, null=True)
    proyecto = models.TextField(blank=True, default='')
    relatedEvaluation = models.ForeignKey('self', blank=True,null=True, on_delete=models.SET_NULL)


class SubCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    code = models.CharField(max_length=5)
    name = models.TextField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'Competence'


class CompetencessXEmployeeXLearningPath(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    competence = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, null=True, blank=True)
    lp = models.ForeignKey(LearningPath, on_delete=models.CASCADE, null=True, blank=True)
    isInitial = models.BooleanField(default=False)
    level = models.TextField(blank=True,null =True)
    score = models.FloatField(blank=True,null =True)

    isActual = models.BooleanField(null=True,blank=True)
    modifiedBy = models.TextField(blank=True, default='',null =True)



class EvaluationxSubCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    hasComment = models.BooleanField(default=True)
    comment = models.TextField(blank=True, default='')
    score = models.FloatField(blank=True, null=True)
    subCategory = models.ForeignKey(SubCategory, null=True, blank=True, on_delete=models.SET_NULL)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.SET_NULL, null=True)

class Plantilla(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    nombre =  models.CharField(max_length=500, null=True, blank=True)
    evaluationType = models.ForeignKey(EvaluationType, on_delete=models.CASCADE, null=True)
    image = models.CharField(max_length=500, null=True, blank=True)

class PlantillaxSubCategoria(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    nombre =  models.CharField(max_length=500, null=True, blank=True)
    plantilla = models.ForeignKey(Plantilla, on_delete=models.CASCADE, null=True)
    subCategory = models.ForeignKey(SubCategory, null=True, blank=True, on_delete=models.SET_NULL)
    posicion = models.IntegerField(null=True,blank=True)

class CompetencyxAreaxPosition(TimeStampedModel, SafeDeleteModel):    
    competency = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)
    areaxposition = models.ForeignKey(AreaxPosicion, on_delete=models.CASCADE, null=True, blank=True)
    score = models.CharField(max_length=20, blank=True, null=True)    
    def __str__(self):
        return f"{self.competency.name} for position {self.areaxposition}"    