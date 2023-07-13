from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
#from evaluations_and_promotions.models import SubCategory
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


class AreaxPosicion(models.Model):  # THIS IS THE REAL POSITION
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


class Functions(models.Model):  # DEPENDS OF AREAXPOSITION
    id = models.BigAutoField(primary_key=True)
    areaxposition = models.ForeignKey(AreaxPosicion, on_delete=models.CASCADE, blank=True, null=True)
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
    current_process_stage = models.IntegerField(default=1, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_current_process_stage(self):
        current_date = timezone.now().date()
        process_stages = self.process_stages.filter(start_date__lte=current_date, end_date__gte=current_date)

        if process_stages.exists():
            process_stages = process_stages.order_by('start_date')
            current_stage = None

            for stage in process_stages:
                if current_stage is None or stage.start_date >= current_stage.end_date:
                    current_stage = stage
            return current_stage

        return None

    def get_current_process_stageV2(self):
        if self.current_process_stage is None:
            return None
        try:
            current_stage = self.process_stages.get(stage_type_id=self.current_process_stage)
            return current_stage
        except ProcessStage.DoesNotExist:
            pass


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
    order = models.IntegerField()  # not used...
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
    introduction = models.TextField(blank=True, default='')  # TEXT LITERAL, ABOUT COMPANY
    offer_introduction = models.TextField(blank=True, default='')  # TEXT LITERAL, ABOUT POSITION
    responsabilities_introduction = models.TextField(blank=True, default='')  # AUTOGENERATED
    capacities_introduction = models.TextField(blank=True, default='')  # AUTOGENERATED
    beneficies_introduction = models.TextField(blank=True, default='')  # TEXT LITERAL
    creation_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    photo_url = models.TextField(blank=True, default='')
    location = models.TextField(blank=True, default='')  # TEXT LITERAL
    salary_range = models.TextField(blank=True, default='')  # TEXT LITERAL

    def __str__(self):
        return "Oferta para el puesto " + self.hiring_process.position.position.name


class JobOfferNotification(models.Model):  # Tabla intermedia Empleado x Oferta laboral
    class Meta:
        db_table = 'NotificacionLaboral'
    id = models.BigAutoField(primary_key=True)
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE)
    employee = models.ForeignKey('login.Employee', on_delete=models.CASCADE)
    sent = models.BooleanField(default=False)  # Si la notificacion fue enviada o no
    suitable = models.BooleanField(default=False)  # Si es que el empleado es compatible para la oferta laboral
    recommendation = models.TextField(blank = True, default = '')

# por ejemplo: Grado académico, Idioma, Certificación
class TrainingType(TimeStampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.code

# por ejemplo: Incompleto, bachiller, licenciado, maestría, doctorado
# por ejemplo: A1, A2, B1, B2, C1, C2


class TrainingLevel(TimeStampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    level = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.code

# por ejemplo: [grado] Ingeniería Informática


class Training(TimeStampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)  # por ejemplo Ingeniería informática
    description = models.TextField(blank=True, default='')
    training_type = models.ForeignKey(TrainingType, on_delete=models.SET_NULL, null=True, blank=True)
    levels = models.ManyToManyField(TrainingLevel, through="TrainingxLevel")

    def __str__(self):
        return self.name

# this is the real EDUCACIÓN
# por ejemplo: [grado] Ingeniería Informática [bachiller]
# por ejemplo: [idioma] Inglés [A1]
# por ejemplo: [Certificacion] AWS Certified Developer [Asociate]


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
    score = models.CharField(max_length=20, blank=True, null=True)  # no se pa que es

    def __str__(self):
        return f"{self.training} for position {self.areaxposition}"

    def to_str(self):
        return f"{self.training}"


class Experience(TimeStampedModel, SafeDeleteModel):

    applicant = models.ForeignKey('login.Applicant', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True, default='', null=True)

    def __str__(self):
        return self.description


class TrainingxApplicant(TimeStampedModel, SafeDeleteModel):

    trainingxlevel = models.ForeignKey(TrainingxLevel, on_delete=models.CASCADE, null=True, blank=True)
    applicant = models.ForeignKey('login.Applicant', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Training: {self.trainingxlevel} for {self.applicant}"


class ApplicantxProcessStage(TimeStampedModel, SafeDeleteModel):
    applicant = models.ForeignKey('login.Applicant', on_delete=models.CASCADE, null=True, blank=True)
    process_stage = models.ForeignKey(ProcessStage, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.applicant}, process {self.process_stage.hiring_process}, stage {self.process_stage}"
    
class CompetenceEvaluation(models.Model):
    score = models.IntegerField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4')], default=2)
    competency_applicant = models.ForeignKey('evaluations_and_promotions.CompetencyxApplicant', on_delete=models.CASCADE)

    def __str__(self):
        return f"Competence Evaluation: Competency {self.competency_applicant.competency.name} - Applicant {self.competency_applicant.applicant.user.username}"

