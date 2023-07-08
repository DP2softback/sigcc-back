from capacitaciones.models import LearningPath
from django.db import models
from login.models import Employee
from model_utils.models import TimeStampedModel
from personal.models import Area, AreaxPosicion, Position
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
    #evaluationType = models.ForeignKey(EvaluationType, on_delete=models.SET_NULL, null=True)


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
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, blank=True, null=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, blank=True, null=True)
    proyecto = models.TextField(blank=True, default='')
    relatedEvaluation = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)


class SubCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    code = models.CharField(max_length=12, blank=True, null=True)
    name = models.TextField(max_length=100, blank=True, null=True,default='')
    description = models.TextField(max_length=300, blank=True, null=True, default='')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    # por favor cuando llenen las competencias, agreguen un valor 0 o 1 dependiend si se relaciona a lo técnico o lo personal
    class Type(models.IntegerChoices):
        TECNICA = 0, 'Relacionado a aspectos técnicos'
        BLANDA = 1, 'Relacionado a la persona'
    type = models.IntegerField(
        choices=Type.choices,
        default=Type.BLANDA
    )

    class Meta:
        db_table = 'Competence'

    def __str__(self):
        return self.name


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

    level = models.TextField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)


    class Scale(models.IntegerChoices):  # PONGANLE EL NOMBRE QUE QUIERAN, EN LA BD SE GUARDA SOLO EL INTEGER
        NO_INICIADO = 0, 'de 0 a 20, no iniciado'
        EN_PROCESO = 1, 'de 21 a 40, en proceso'
        LOGRADO = 2, 'de 41 a 60, en proceso'
        SOBRESALIENTE = 3, 'de 61 a 80, en proceso'
        EXPERTO = 4, 'de 81 a 100, en proceso'

    scale = models.IntegerField(
        choices=Scale.choices,
        default=Scale.LOGRADO
    )
    scaleRequired = models.IntegerField(
        choices=Scale.choices,
        default=Scale.LOGRADO,
        blank=True, null =True
    )
    levelGap = models.IntegerField(blank=True,null =True) #cuanta nota necesita para alcanzar nivel requerido
    likeness = models.FloatField(blank=True,null =True) #porcentaje entre level actual y requerido
    hasCertificate = models.BooleanField(null=True, blank=True,default=False)
    registerByEmployee = models.BooleanField(null=True, blank=True,default=False)
    requiredForPosition = models.BooleanField(null=True, blank=True,default=False)

    isActual = models.BooleanField(null=True, blank=True)
    modifiedBy = models.TextField(blank=True, default='', null=True)


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
    nombre = models.CharField(max_length=500, null=True, blank=True)
    evaluationType = models.ForeignKey(EvaluationType, on_delete=models.CASCADE, null=True)
    image = models.CharField(max_length=500, null=True, blank=True)


class PlantillaxSubCategoria(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(default=True)
    nombre = models.CharField(max_length=500, null=True, blank=True)
    plantilla = models.ForeignKey(Plantilla, on_delete=models.CASCADE, null=True)
    subCategory = models.ForeignKey(SubCategory, null=True, blank=True, on_delete=models.SET_NULL)
    posicion = models.IntegerField(null=True, blank=True)


class CompetencyxAreaxPosition(TimeStampedModel, SafeDeleteModel):
    competency = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)
    areaxposition = models.ForeignKey(AreaxPosicion, on_delete=models.CASCADE, null=True, blank=True)
    score = models.CharField(max_length=20, blank=True, null=True)

    class Scale(models.IntegerChoices):  # PONGANLE EL NOMBRE QUE QUIERAN, EN LA BD SE GUARDA SOLO EL INTEGER
        NO_INICIADO = 0, 'de 0 a 20, no iniciado'
        EN_PROCESO = 1, 'de 21 a 40, en proceso'
        LOGRADO = 2, 'de 41 a 60, en proceso'
        SOBRESALIENTE = 3, 'de 61 a 80, en proceso'
        EXPERTO = 4, 'de 81 a 100, en proceso'

    scale = models.IntegerField(
        choices=Scale.choices,
        default=Scale.LOGRADO
    )

    def __str__(self):
        return f"{self.competency.name} for position {self.areaxposition}"
