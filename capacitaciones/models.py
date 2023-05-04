from django.db import models

# Create your models here.
class LearningPath(models.Model):
    nombre = models.CharField(max_length=300)
    descripcion = models.TextField()

    class Meta:
        db_table = 'LearningPath'


class Curso(models.Model):
    udemy_id = models.IntegerField()
    course_udemy_detail = models.JSONField()
    duracion = models.DurationField()
    calificacion = models.DecimalField(default=4.5, max_digits=3, decimal_places=2)
    curso_x_learning_path = models.ManyToManyField(LearningPath, through='CursoXLearningPath')

    class Meta:
        db_table = 'Curso'


class CursoXLearningPath(models.Model):

    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)

    class Meta:
        db_table = 'CursoXLearningPath'


class Pregunta(models.Model):
    texto = models.CharField(max_length=1000)
    pregunta_x_curso = models.ManyToManyField(Curso, through='PreguntaXCurso')

    class Meta:
        db_table = 'Pregunta'


class PreguntaXCurso(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)

    class Meta:
        db_table = 'PreguntaXCurso'


class Alternativa(models.Model):
    textoAlternativa = models.CharField(max_length=1000)
    respuestaCorrecta = models.BooleanField(default=0)

    class Meta:
        db_table = 'Alternativa'
