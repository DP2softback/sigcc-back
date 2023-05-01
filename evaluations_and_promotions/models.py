from django.db import models

# Create your models here.

class CategoryType(models.Model):
    id = models.BigAutoField(primary_key=True)
    code = models.CharField(max_length=4,null=True, blank=True, unique=True)
    description = models.CharField(max_length=500 ,null=True, blank=True)
    isActive = models.BooleanField(default=True)
    creationDate = models.DateField()
    modifiedDate = models.DateField()

class EvaluationType(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateField()
    modifiedDate = models.DateField()
    isActive = models.BooleanField(default=True)
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=500,null=True, blank=True)

class Position(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateField()
    modifiedDate = models.DateField()
    isActive = models.BooleanField(default=True)
    name = models.CharField(max_length=40)
    benefits = models.CharField(max_length=100,null=True, blank=True)
    responsabilities = models.CharField(max_length=100,null=True, blank=True)
    description =  models.CharField(max_length=100,null=True, blank=True)
    tipoJornada =  models.CharField(max_length=100,null=True, blank=True)
    modalidadTrabajo = models.CharField(max_length=100,null=True, blank=True)
class Area(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateField()
    modifiedDate = models.DateField()
    isActive = models.BooleanField(default=True)
    description =  models.CharField(max_length=100,null=True, blank=True)
    name = models.CharField(max_length=100)
    supervisorsArea = models.ForeignKey('self',null=True, on_delete=models.SET_NULL)
    roles = models.ManyToManyField(Position, through="AreaxPosicion")

class Evaluation(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateField()
    modifiedDate = models.DateField()
    isActive = models.BooleanField(default=True)
    evaluationDate = models.DateField()
    hasComment = models.BooleanField()
    generalComment = models.CharField(max_length=500,null=True,blank=True)
    isFinished = models.BooleanField()
    finalScore = models.FloatField(null=True, blank=True)
    evaluator = models.ForeignKey('login.Employee',related_name="employeeEvaluator", on_delete=models.SET_NULL, blank=True, null=True)
    evaluated = models.ForeignKey('login.Employee',related_name="employeeEvaluated", on_delete=models.SET_NULL,blank=True, null=True)
    evaluationType = models.ForeignKey(EvaluationType, on_delete=models.CASCADE)

class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateField()
    modifiedDate = models.DateField()
    isActive = models.BooleanField(default=True)
    hasComment = models.BooleanField()
    hasScore = models.BooleanField()
    comment  = models.CharField(max_length=500,null=True, blank=True)
    score = models.FloatField(null=True,blank=True)
    categoryType = models.ForeignKey(CategoryType, on_delete=models.RESTRICT)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)




class AreaxPosicion(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE)   
    position = models.ForeignKey(Position, on_delete=models.CASCADE)  
    creationDate = models.DateField()
    modifiedDate = models.DateField() 
    isActive = models.BooleanField(default=True)
    availableQuantity = models.IntegerField()
    unavailableQuantity = models.IntegerField()
    




