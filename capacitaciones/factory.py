import factory
from django.db.models.expressions import Random
from factory import lazy_attribute
from faker import Faker
from .models import Parametros, LearningPath, CursoGeneral, CursoUdemy, CursoEmpresa, CursoGeneralXLearningPath

#pip install faker
#pip install factory-boy

fake = Faker()

class LearningPathFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LearningPath

    nombre = factory.Faker('sentence', nb_words=3)
    descripcion = factory.Faker('text')
    url_foto = factory.Faker('url')
    suma_valoraciones = factory.Faker('random_int', min=0, max=1000)
    cant_valoraciones = factory.Faker('random_int', min=0, max=100)
    cant_empleados = factory.Faker('random_int', min=0, max=1000)
    horas_duracion = factory.Faker('time_delta')

    @lazy_attribute
    def cant_intentos_cursos_max(self):
        return Parametros.objects.first().numero_intentos_curso

    @lazy_attribute
    def cant_intentos_evaluacion_integral_max(self):
        return Parametros.objects.first().numero_intentos_lp

    estado = factory.Faker('random_int', min=0, max=3)


class CursoGeneralFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CursoGeneral

    nombre = factory.Faker('sentence', nb_words=3)
    descripcion = factory.Faker('text')
    duracion = factory.Faker('time_delta')
    suma_valoracionees = factory.Faker('random_int', min=0, max=1000)
    cant_valoraciones = factory.Faker('random_int', min=0, max=100)


class CursoUdemyFactory(CursoGeneralFactory):
    class Meta:
        model = CursoUdemy

    udemy_id = factory.Faker('random_int', min=1000, max=9999)
    course_udemy_detail = {}


class CursoEmpresaFactory(CursoGeneralFactory):
    class Meta:
        model = CursoEmpresa

    tipo = factory.Faker('random_element', elements=['P', 'S', 'A'])
    es_libre = factory.Faker('boolean')
    url_foto = factory.Faker('text')


class CursoGeneralXLearningPathFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = CursoGeneralXLearningPath

    curso = factory.LazyFunction(lambda : CursoGeneral.objects.order_by(Random()).first())
    learning_path = factory.LazyFunction(lambda: LearningPath.objects.order_by(Random()).first())
    cant_intentos_max = factory.Faker('random_int', min=2, max=4)
    porcentaje_asistencia_aprobacion = factory.Faker('random_int', min=0, max=100)