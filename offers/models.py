from django.db import models

# Create your models here.

class CompetencyType(models.Model):
    id = models.IntegerField(primary_key = True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(default=True)

class Competency(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(default=True)
    typeComp = models.ForeignKey(CompetencyType, on_delete=models.CASCADE, null=True, blank=True)

# #############################################################################################################
# Modelos login creados por otro grupo - se reemplazará
class Role(models.Model):
    id =models.BigAutoField(primary_key=True)
    creationDate = models.DateField()
    modifiedDate = models.DateField()
    isActive = models.BooleanField(default=True)
    name = models.CharField(max_length=32, unique=True)
    description = models.TextField(blank=True)

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateField()
    modifiedDate = models.DateField()
    isActive = models.BooleanField(default=True)
    username = models.CharField(max_length=25, unique=True)
    firstName = models.CharField(max_length=25)
    secondName = models.CharField(max_length=25)
    lastName = models.CharField(max_length=25)
    maidenName = models.CharField(max_length=25)
    email = models.EmailField(max_length=46, unique=True, null=False, blank=False)
    password = models.CharField(max_length=32)
    role = models.ForeignKey(Role, on_delete=models.RESTRICT)
    cv = models.TextField(blank=True)

# #############################################################################################################
# #############################################################################################################
# Modelos evaluations creados por otro grupo - se reemplazará

class Position(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateField()
    modifiedDate = models.DateField()
    isActive = models.BooleanField(default=True)
    name = models.CharField(max_length=40)
    benefits = models.TextField(blank=True, default='')
    responsabilities = models.TextField(blank=True, default='')
    description =  models.TextField(blank=True, default='')
    tipoJornada =  models.TextField(blank=True, default='')
    modalidadTrabajo = models.TextField(blank=True, default='')


class Area(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateField()
    modifiedDate = models.DateField()
    isActive = models.BooleanField(default=True)
    description =  models.TextField(blank=True, default='')
    name = models.CharField(max_length=100)
    supervisorsArea = models.ForeignKey('self',null=True, on_delete=models.SET_NULL)
    roles = models.ManyToManyField(Position, through="AreaxPosicion")
    
class AreaxPosicion(models.Model):
    id = models.BigAutoField(primary_key=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)   
    position = models.ForeignKey(Position, on_delete=models.CASCADE)  
    creationDate = models.DateField()
    modifiedDate = models.DateField() 
    isActive = models.BooleanField(default=True)
    availableQuantity = models.IntegerField()
    unavailableQuantity = models.IntegerField()
    competencies = models.ManyToManyField(Competency, through='AreaxPositionxCompetency') #cambio 1 - competencias de areaposicion

# #############################################################################################################
# #############################################################################################################
# Modelos de login 2

class Employee(models.Model):
    id = models.BigAutoField(primary_key=True)
    creationDate = models.DateField()
    modifiedDate = models.DateField()
    isActive = models.BooleanField(default=True)
    isSupervisor = models.BooleanField()
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)
    competencies = models.ManyToManyField(Competency, through='EmployeexCompetency') #cambio 2 - competencias de empleado

# #############################################################################################################
# #############################################################################################################

class JobOffer(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    requirements = models.CharField(max_length=500, blank=True, null=True)
    publicationDate = models.DateField(blank=True, null=True)
    selectionStartDate = models.DateField(blank=True, null=True)
    selectionFinishDate = models.DateField(blank=True, null=True)
    state = models.IntegerField(blank=True,null =True)
    available = models.IntegerField(blank=True,null =True)
    active = models.BooleanField(default=True)
    position = models.ForeignKey(AreaxPosicion, on_delete=models.CASCADE, null=True, blank=True) #cambiar cuando se haga el merge
    candidates = models.ManyToManyField(User, through='JobOfferxUser') #cambiar cuando se haga el merge

class JobOfferxUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) #cambiar cuando se haga el merge
    jobOffer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)

class OfferNotification(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=300, blank=True, null=True)
    active = models.BooleanField(default=True)
    jobOffer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, null=True, blank=True)

class AreaxPositionxCompetency(models.Model):
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE, null=True, blank=True)
    position = models.ForeignKey(AreaxPosicion, on_delete=models.CASCADE, null=True, blank=True) #cambiar cuando se haga el merge
    level = models.IntegerField(blank=True,null =True)
    active = models.BooleanField(default=True)

class EmployeexCompetency(models.Model):
    competency = models.ForeignKey(Competency, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True) #cambiar cuando se haga el merge
    level = models.IntegerField(blank=True,null =True)
    active = models.BooleanField(default=True)