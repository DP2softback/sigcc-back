from django.db import models

# Create your models here.

class Role(models.Model):
    id =models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add = True)
    modifiedDate = models.DateTimeField(auto_now = True)
    isActive = models.BooleanField(default=True)
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=256)

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add = True)
    modifiedDate = models.DateTimeField(auto_now = True)
    isActive = models.BooleanField(default=True)
    username = models.CharField(max_length=25, unique=True)
    firstName = models.CharField(max_length=25)
    secondName = models.CharField(max_length=25)
    lastName = models.CharField(max_length=25)
    maidenName = models.CharField(max_length=25)
    email = models.EmailField(max_length=46, unique=True, null=False, blank=False)
    password = models.CharField(max_length=32)
    role = models.ForeignKey(Role, null = True, on_delete=models.RESTRICT)

class Employee(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add = True)
    modifiedDate = models.DateTimeField(auto_now = True)
    isActive = models.BooleanField(default=True)
    isSupervisor = models.BooleanField()
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    area = models.ForeignKey('evaluations_and_promotions.Area', on_delete=models.SET_NULL, null=True)
    position = models.ForeignKey('evaluations_and_promotions.Position', on_delete=models.SET_NULL, null=True)


