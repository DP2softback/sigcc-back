from datetime import timedelta

from django.db import models

# Create your models here.
from login.models import Employee


class Parametros(models.Model):

    nota_maxima = models.IntegerField()
    nota_minima = models.IntegerField()
    numero_intentos_curso = models.IntegerField()

    class Meta:
        db_table = 'Parametros'


class LearningPath(models.Model):

    estado_choices = [
        ('0', 'Desactivado'),
        ('1', 'CreadoSinFormulario'),
        ('2', 'ErrorFormulario'),
        ('3', 'CreadoCompleto')
    ]

    nombre = models.CharField(max_length=300)
    descripcion = models.TextField()
    url_foto = models.TextField(null=True)
    suma_valoraciones = models.IntegerField(default=0)
    cant_valoraciones = models.IntegerField(default=0)
    cant_empleados = models.IntegerField(default=0)
    horas_duracion = models.DurationField(default=timedelta(seconds=0))
    estado = models.CharField(max_length=1, choices=estado_choices, default='0')

    class Meta:
        db_table = 'LearningPath'

    def __str__(self):
        return self.nombre


class CursoGeneral(models.Model):
    nombre = models.CharField(max_length=300)
    descripcion = models.CharField(max_length=300)
    duracion = models.DurationField()
    suma_valoracionees = models.IntegerField(default=0)
    cant_valoraciones = models.IntegerField(default=0)
    curso_x_learning_path = models.ManyToManyField(LearningPath, through='CursoGeneralXLearningPath')

    class Meta:
        db_table = 'CursoGeneral'

    def __str__(self):
        return self.nombre


class CursoUdemy(CursoGeneral):
    udemy_id = models.IntegerField()
    course_udemy_detail = models.JSONField()

    class Meta:
        db_table = 'CursoUdemy'


class CursoEmpresa(CursoGeneral):

    tipo_choices = [
        ('P', 'Presencial'),
        ('S', 'Virtual sincrono'),
        ('A', 'Virtual asincrono')
    ]

    tipo = models.CharField(max_length=1, choices=tipo_choices)
    asunto = models.TextField()
    ubicacion = models.CharField(max_length=500,null=True)#Los cursos Empresa del Tipo Asincrono no tienen ubicacion
    fecha = models.DateTimeField()
    url_video = models.TextField()
    asistencia_x_empleado = models.ManyToManyField(Employee, through='AsistenciaCursoEmpresaXEmpleado')

    class Meta:
        db_table = 'CursoEmpresa'


class CursoGeneralXLearningPath(models.Model):

    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    curso = models.ForeignKey(CursoGeneral, on_delete=models.CASCADE)
    nro_orden = models.IntegerField()
    cant_intentos_max = models.IntegerField()

    class Meta:
        db_table = 'CursoGeneralXLearningPath'

    def get_cant_intentos_max_default(self):
        return Parametros.objects.first().numero_intentos_curso

    def get_nro_orden(self):
        pos = CursoGeneralXLearningPath.objects.filter(learning_path = self.learning_path).count()
        return pos + 1

    def update_learning_path_duration(self):
        self.learning_path.horas_duracion += self.curso.duracion
        self.learning_path.save()

    def save(self, *args, **kwargs):
        if not self.cant_intentos_max:
            self.cant_intentos_max = self.get_cant_intentos_max_default()

        if not self.nro_orden:
            self.nro_orden = self.get_nro_orden()

        super().save(*args, **kwargs)

        self.update_learning_path_duration()


class Pregunta(models.Model):
    texto = models.CharField(max_length=1000)
    pregunta_x_curso = models.ManyToManyField(CursoUdemy, through='PreguntaXCursoUdemy')

    class Meta:
        db_table = 'Pregunta'


class PreguntaXCursoUdemy(models.Model):
    curso = models.ForeignKey(CursoUdemy, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)

    class Meta:
        db_table = 'PreguntaXCursoUdemy'


class Alternativa(models.Model):
    texto_alternativa = models.CharField(max_length=1000)
    respuesta_correcta = models.BooleanField(default=0)

    class Meta:
        db_table = 'Alternativa'


class EmpleadoXLearningPath(models.Model):
    estado_choices = [
        ('Sin iniciar', 'Sin iniciar'),
        ('Completado', 'Completado'),
        ('En progreso', 'En progreso'),
        ('Caducado', 'Caducado'),
        ('Desaprobado', 'Desaprobado'),
    ]

    empleado = models.ForeignKey(Employee, on_delete=models.CASCADE)
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    estado = models.CharField(max_length=30, choices=estado_choices)
    porcentaje_progreso = models.DecimalField(default=0, max_digits=3, decimal_places=2)
    apreciacion = models.TextField()
    fecha_asignacion = models.DateTimeField()
    fecha_limite = models.DateTimeField()

    class Meta:
        db_table = 'EmpleadoXLearningPath'


class DocumentoRespuesta(models.Model):
    url_documento = models.TextField()
    empleado_learning_path = models.ForeignKey(EmpleadoXLearningPath, on_delete=models.CASCADE)

    class Meta:
        db_table = 'DocumentosRespuesta'


class EmpleadoXCurso(models.Model):
    empleado = models.ForeignKey(Employee, on_delete=models.CASCADE)
    curso = models.ForeignKey(CursoGeneral, on_delete=models.CASCADE)
    valoracion = models.IntegerField()

    class Meta:
        db_table = 'EmpleadoXCurso'


class EmpleadoXCursoXLearningPath(models.Model):
    estado_choices = [
        ('Sin iniciar', 'Sin iniciar'),
        ('Completado', 'Completado'),
        ('En progreso', 'En progreso'),
        ('Sin evaluar', 'Sin evaluar'),
        ('Desaprobado', 'Desaprobado'),
    ]
    empleado = models.ForeignKey(Employee, on_delete=models.CASCADE)
    progreso = models.DecimalField(default=0, max_digits=3, decimal_places=2)
    curso = models.ForeignKey(CursoGeneral, on_delete=models.CASCADE)
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    estado = models.CharField(max_length=30, choices=estado_choices)
    nota_final = models.IntegerField()
    cant_intentos = models.IntegerField(default = 0)
    fecha_evaluacion = models.DateTimeField()
    ultima_evaluacion = models.BooleanField()

    class Meta:
        db_table = 'EmpleadoXCursoXLearningPath'


class EmpleadoXCursoXPreguntaXAlternativa(models.Model):
    empleado = models.ForeignKey(Employee, on_delete=models.CASCADE)
    curso = models.ForeignKey(CursoUdemy, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    alternativa = models.ForeignKey(Alternativa, on_delete=models.CASCADE)

    class Meta:
        db_table = 'EmpleadoXCursoXPreguntaXAlternativa'


class AsistenciaCursoEmpresaXEmpleado(models.Model):
    curso_empresa = models.ForeignKey(CursoEmpresa, on_delete=models.CASCADE)
    empleado_id = models.ForeignKey(Employee, on_delete=models.CASCADE)
    tipo_choices = [
        ('P','Asistio puntual'),
        ('T','Asistio tarde'),
        ('N','No asistio'),
        ('J','Falta justificada')
    ]

    estado_asistencia= models.CharField(max_length=1, choices=tipo_choices)

    class Meta:
        db_table = 'AsistenciaCursoEmpresaXEmpleado'


class RubricaExamen(models.Model):
    descripcion = models.CharField(max_length=200)
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    rubrica_examen_x_empleado = models.ManyToManyField(Employee, through='RubricaExamenXEmpleado')

    class Meta:
        db_table = 'RubricaExamen'


class DocumentoExamen(models.Model):
    #Este atributo es el link para recuperar los archivos
    url_documento = models.TextField()
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)

    class Meta:
        db_table = 'DocumentoExamen'


class DetalleRubricaExamen(models.Model):
    criterio_evaluacion = models.CharField(max_length=200)
    nota_maxima = models.IntegerField()
    rubrica_examen = models.ForeignKey(RubricaExamen, on_delete=models.CASCADE)
    detalle_rubrica_x_empleado = models.ManyToManyField(Employee, through='DetalleRubricaExamenXEmpleado')

    class Meta:
        db_table = 'DetalleRubricaExamen'


class DetalleRubricaExamenXEmpleado(models.Model):

    detalle_rubrica_examen = models.ForeignKey(DetalleRubricaExamen, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Employee, on_delete=models.CASCADE)
    nota = models.IntegerField()
    comentario = models.TextField()

    class Meta:
        db_table = 'DetalleRubricaExamenXEmpleado'


class RubricaExamenXEmpleado(models.Model):

    rubrica_examen = models.ForeignKey(RubricaExamen, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Employee, on_delete=models.CASCADE)
    nota = models.IntegerField()
    comentario = models.TextField()

    class Meta:
        db_table = 'RubricaExamenXEmpleado'

