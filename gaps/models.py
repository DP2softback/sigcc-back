from django.db import models
from evaluations_and_promotions.models import Area, Position
from login.models import Employee

# Create your models here.

class TipoCompetencia(models.Model):
    id = models.BigAutoField(primary_key=True)
    abreviatura = models.CharField(max_length=30, blank=True, null=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=300, blank=True, null=True)
    activo = models.BooleanField(default=True)
    export_fields = [
        'id',
        'abreviatura',
        'nombre',
        'descripcion',
        'activo'
    ]
    
class Competencia(models.Model):
    id = models.BigAutoField(primary_key = True)
    codigo = models.CharField(max_length=12, blank=True, null=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=300, blank=True, null=True)
    activo = models.BooleanField(default=True)
    tipo = models.ForeignKey(TipoCompetencia, on_delete=models.CASCADE, null=True, blank=True)
	
class CompetenciaXAreaXPosicion(models.Model):
    id = models.BigAutoField(primary_key=True)
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE, null=True, blank=True)
    posicion = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    nivelRequerido = models.IntegerField(blank=True,null =True)
    activo = models.BooleanField(default=True)

class CompetenciaXEmpleado(models.Model):
    id = models.BigAutoField(primary_key=True)
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE, null=True, blank=True)
    empleado = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    nivelActual = models.IntegerField(blank=True,null =True)
    nivelRequerido = models.IntegerField(blank=True,null =True)
    nivelBrecha = models.IntegerField(blank=True,null =True)
    adecuacion = models.FloatField(blank=True,null =True)
    tieneCertificado = models.BooleanField(default=False)
    agregadoPorEmpleado = models.BooleanField(default=False)
    requeridoParaPuesto = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

class NecesidadCapacitacion(models.Model):
    id = models.BigAutoField(primary_key=True)
    competencia = models.ForeignKey(Competencia, on_delete=models.CASCADE, null=True, blank=True)
    empleado = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    estado = models.IntegerField(blank=True,null =True)  #0: por solucionar, 1: en proceso, 2: solucionado 
    nivelActual = models.IntegerField(blank=True,null =True)
    nivelRequerido = models.IntegerField(blank=True,null =True)
    nivelBrecha = models.IntegerField(blank=True,null =True) #1: brecha de nivel 1, 2: brecha de nivel 2, 3: brecha de nivel 3, 4: brecha de nivel 4
    tipo = models.IntegerField(blank=True,null =True) #1: de incorporacion, 2: de evaluacion 2, 3: de ascenso
    activo = models.BooleanField(default=True)


