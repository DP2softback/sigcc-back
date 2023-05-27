from django.db import models


# Create your models here.
class Position(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    name = models.CharField(max_length=40)
    benefits = models.TextField(blank=True, default='')
    responsabilities = models.TextField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    tipoJornada = models.TextField(blank=True, default='')
    modalidadTrabajo = models.TextField(blank=True, default='')


class Area(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    description = models.TextField(blank=True, default='')
    name = models.CharField(max_length=100)
    supervisorsArea = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)
    roles = models.ManyToManyField(Position, through="AreaxPosicion")


class AreaxPosicion(models.Model):
    id = models.BigAutoField(primary_key=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    creationDate = models.DateTimeField()
    modifiedDate = models.DateTimeField()
    isActive = models.BooleanField(default=True)
    availableQuantity = models.IntegerField()
    unavailableQuantity = models.IntegerField()
