from django.db import models

class Users(models.Model):   
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    age = models.IntegerField()

    def __str__(self):
        return self.first_name


    class Meta:
        verbose_name_plural = 'users'

class School(models.Model):   
    name = models.CharField(max_length=64)
    acronym = models.CharField(max_length=64)

    class Meta:
        verbose_name_plural = 'schools'    
        