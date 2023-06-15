from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.
class Position(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    name = models.CharField(max_length=100, null=True)
    benefits = models.TextField(blank=True, default='', null=True)
    # responsabilities = models.TextField(blank=True, default='', null=True)
    description = models.TextField(blank=True, default='', null=True)
    tipoJornada = models.TextField(blank=True, default='', null=True)
    modalidadTrabajo = models.TextField(blank=True, default='', null=True)

    def __str__(self):
        return self.name


class Area(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    description = models.TextField(blank=True, default='')
    name = models.CharField(max_length=100)
    supervisorsArea = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, blank=True)
    roles = models.ManyToManyField(Position, through="AreaxPosicion")

    def __str__(self):
        return self.name


class AreaxPosicion(models.Model):
    id = models.BigAutoField(primary_key=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    creationDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    availableQuantity = models.IntegerField(default=0)
    unavailableQuantity = models.IntegerField(default=0)

class Functions(models.Model):
    id = models.BigAutoField(primary_key=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='', null=True)
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.description


class HiringProcess(models.Model):
    class Meta:
        db_table = 'ProcesoSeleccion'
    id = models.BigAutoField(primary_key=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    name = models.CharField(max_length=60)
    available_positions_quantity = models.IntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class EmployeeXHiringProcess(models.Model):
    class Meta:
        db_table = 'EmpleadoXProcesoSeleccion'
    id = models.BigAutoField(primary_key=True)
    employee = models.ForeignKey('login.Employee', on_delete=models.CASCADE)
    hiring_process = models.ForeignKey(HiringProcess, on_delete=models.CASCADE)
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

    def __str__(self):
        return self.name

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

    def __str__(self):
        return self.name

class JobOffer(models.Model):
    class Meta:
        db_table = 'OfertaLaboral'
    id = models.BigAutoField(primary_key=True)
    hiring_process = models.ForeignKey(HiringProcess, on_delete=models.CASCADE)
    introduction = models.TextField(blank=True, default='')
    offer_introduction = models.TextField(blank=True, default='')
    responsabilities_introduction = models.TextField(blank=True, default='')
    creation_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    photo_url = models.TextField(blank=True, default='')
    location = models.TextField(blank=True, default='')
    salary_range = models.TextField(blank=True, default='')

    def __str__(self):
        return "Oferta para el puesto "+ self.hiring_process.position.name
    
class JobOfferNotification(models.Model): # Tabla intermedia Empleado x Oferta laboral
    class Meta:
        db_table = 'NotificacionLaboral'
    id = models.BigAutoField(primary_key=True)
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE)
    employee = models.ForeignKey('login.Employee', on_delete=models.CASCADE)
    sent = models.BooleanField(default = False) # Si la notificacion fue enviada o no
    suitable = models.BooleanField(default = False) # Si es que el empleado es compatible para la oferta laboral

    


