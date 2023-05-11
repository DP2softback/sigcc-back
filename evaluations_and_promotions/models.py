from django.db import models

# Create your models here.


class EvaluationType(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add = True)
    modifiedDate = models.DateTimeField(auto_now = True)
    isActive = models.BooleanField(default=True)
    name = models.CharField(max_length=40,blank=True)
    description = models.TextField(blank=True, default='')


class Position(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add = True)
    modifiedDate = models.DateTimeField(auto_now = True)
    isActive = models.BooleanField(default=True)
    name = models.CharField(max_length=40)
    benefits = models.TextField(blank=True, default='')
    responsabilities = models.TextField(blank=True, default='')
    description =  models.TextField(blank=True, default='')
    tipoJornada =  models.TextField(blank=True, default='')
    modalidadTrabajo = models.TextField(blank=True, default='')

class Area(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add = True)
    modifiedDate = models.DateTimeField(auto_now = True)
    isActive = models.BooleanField(default=True)
    description =  models.TextField(blank=True, default='')
    name = models.CharField(max_length=100)
    supervisorsArea = models.ForeignKey('self',null=True, on_delete=models.SET_NULL)
    roles = models.ManyToManyField(Position, through="AreaxPosicion")

class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField()
    modifiedDate = models.DateTimeField()
    isActive = models.BooleanField(default=True)
    name = models.TextField(blank=True,default='')
    code = models.CharField(max_length=5, blank=True)
    description = models.TextField(blank=True, default='')
    evaluationType = models.ForeignKey(EvaluationType,on_delete=models.SET_NULL, null=True)

class AreaxPosicion(models.Model):
    id = models.BigAutoField(primary_key=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)   
    position = models.ForeignKey(Position, on_delete=models.CASCADE)  
    creationDate = models.DateTimeField()
    modifiedDate = models.DateTimeField() 
    isActive = models.BooleanField(default=True)
    availableQuantity = models.IntegerField()
    unavailableQuantity = models.IntegerField()

class Evaluation(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add = True)
    modifiedDate = models.DateTimeField(auto_now = True)
    isActive = models.BooleanField(default=True)
    evaluationDate = models.DateTimeField()
    hasComment = models.BooleanField()
    generalComment = models.CharField(max_length=500,null=True,blank=True)
    isFinished = models.BooleanField()
    finalScore = models.FloatField(null=True, blank=True)
    evaluator = models.ForeignKey('login.Employee',related_name="employeeEvaluator", on_delete=models.SET_NULL, blank=True, null=True)
    evaluated = models.ForeignKey('login.Employee',related_name="employeeEvaluated", on_delete=models.SET_NULL,blank=True, null=True)
    evaluationType = models.ForeignKey(EvaluationType, on_delete=models.CASCADE)
    areaxPosicion = models.ForeignKey(AreaxPosicion, on_delete=models.SET_NULL, null=True)

class SubCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add = True)
    modifiedDate = models.DateTimeField(auto_now = True)
    isActive = models.BooleanField(default=True)
    code = models.CharField(max_length=5)
    name = models.TextField(blank=True,default='')
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)


class EvaluationxSubCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add = True)
    modifiedDate = models.DateTimeField(auto_now = True)
    isActive = models.BooleanField(default=True)
    hasComment = models.BooleanField(default=True)
    comment = models.TextField(blank=True, default='')
    score = models.FloatField(blank=True,null=True)
    subCategory = models.ForeignKey(SubCategory, null=True, blank=True, on_delete=models.SET_NULL)
    evaluation= models.ForeignKey(Evaluation, on_delete=models.SET_NULL, null=True)


    




