from django.db import models
from django.contrib.auth import get_user_model

from model_utils.models import TimeStampedModel
from safedelete.models import SOFT_DELETE, SOFT_DELETE_CASCADE, SafeDeleteModel

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
    positions = models.ManyToManyField(Position, through="AreaxPosicion")
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

    def __str__(self):
        return f"Position {self.position.name} in area {self.area.name}"


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
    position = models.ForeignKey(AreaxPosicion, on_delete=models.CASCADE)
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
    # First Stage
    position_similarity = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

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
    capacities_introduction = models.TextField(blank=True, default='')
    beneficies_introduction = models.TextField(blank=True, default='')
    creation_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    photo_url = models.TextField(blank=True, default='')
    location = models.TextField(blank=True, default='')
    salary_range = models.TextField(blank=True, default='')

    def __str__(self):
        return "Oferta para el puesto "+ self.hiring_process.position.position.name
    
class JobOfferNotification(models.Model): # Tabla intermedia Empleado x Oferta laboral
    class Meta:
        db_table = 'NotificacionLaboral'
    id = models.BigAutoField(primary_key=True)
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE)
    employee = models.ForeignKey('login.Employee', on_delete=models.CASCADE)
    sent = models.BooleanField(default = False) # Si la notificacion fue enviada o no
    suitable = models.BooleanField(default = False) # Si es que el empleado es compatible para la oferta laboral


class TrainingType(TimeStampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    
    def __str__(self):
        return self.code
    
class TrainingLevel(TimeStampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    level = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return self.code    

class Training(TimeStampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')    
    training_type = models.ForeignKey(TrainingType, on_delete=models.SET_NULL, null=True, blank=True)
    levels = models.ManyToManyField(TrainingLevel, through="TrainingxLevel")
    def __str__(self):
        return self.name

# this is the real EDUCACIÓN
class TrainingxLevel(TimeStampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    training = models.ForeignKey(Training, on_delete=models.SET_NULL, null=True, blank=True)
    level = models.ForeignKey(TrainingLevel, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.training.training_type.name} {self.level.name} en {self.training.name}"


# intersections

class TrainingxAreaxPosition(TimeStampedModel, SafeDeleteModel):    
    training = models.ForeignKey(TrainingxLevel, on_delete=models.CASCADE, null=True, blank=True)
    areaxposition = models.ForeignKey(AreaxPosicion, on_delete=models.CASCADE, null=True, blank=True)
    score = models.CharField(max_length=20, blank=True, null=True)    
    def __str__(self):
        return f"{self.training} for position {self.areaxposition}"
    

