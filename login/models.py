# from django.contrib.auth.models import User
from django.contrib import admin
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
    roles = models.ManyToManyField(Role, related_name='users', through='UserxRole')
    recovery_code = models.CharField(max_length=25, null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    # objects = CustomUserManager()

    def __str__(self):
        return self.first_name + " " + self.second_name

    export_fields = [
        'username',
        'email',
        'first_name',
        'second_name',
        'last_name',
        'maiden_name'
        'roles',
        'is_active'
    ]


class UserxRole(TimeStampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    roles = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email + " is " + self.roles.name


class Employee(TimeStampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    isSupervisor = models.BooleanField()
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Employee: {self.user.first_name} {self.user.last_name}"


class Applicant(TimeStampedModel, SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Applicant: {self.user.first_name} {self.user.last_name}"
