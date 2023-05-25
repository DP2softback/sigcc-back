# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db import models
from model_utils import Choices
from model_utils.models import TimeStampedModel
from personal.models import Area, Position
from safedelete.models import SOFT_DELETE, SOFT_DELETE_CASCADE, SafeDeleteModel

# Create your models here.


class Role(TimeStampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    name = models.CharField(max_length=32, unique=True)
    description = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class User(AbstractUser, TimeStampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    second_name = models.CharField(max_length=25)
    maiden_name = models.CharField(max_length=25)
    role = models.ForeignKey(Role, null=True, on_delete=models.RESTRICT)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    # objects = CustomUserManager()

    def __str__(self):
        return self.first_name + " " + self.second_name


class Employee(TimeStampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    isSupervisor = models.BooleanField()
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)

class Applicant(TimeStampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    