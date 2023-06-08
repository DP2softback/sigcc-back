from django.db import models
# from login.models import Employee


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

class HiringProcess(models.Model):
    class Meta:
        db_table = 'ProcesoSeleccion'
    id = models.BigAutoField(primary_key=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    # employees = models.ManyToManyField(Employee, related_name='hiring_processes')
    available_positions_quantity = models.IntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

class StageType(models.Model):
    class Meta:
        db_table = 'TipoEtapa'
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=40)
    creation_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

class ProcessStage(models.Model):
    class Meta:
        db_table = 'EtapaProceso'
    id = models.BigAutoField(primary_key=True)
    stage_type = models.ForeignKey(StageType, on_delete=models.CASCADE)
    hiring_process = models.ForeignKey(HiringProcess, related_name='process_stages', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    order = models.IntegerField()
    name = models.CharField(max_length=40)
    description = models.TextField(blank=True, default='')
    creation_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)



