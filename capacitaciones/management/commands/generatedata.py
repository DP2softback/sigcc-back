from django.core.management.base import BaseCommand
from django.db import transaction

from capacitaciones.factory import CursoUdemyFactory, CursoEmpresaFactory, CursoGeneralXLearningPathFactory, \
    LearningPathFactory
from capacitaciones.models import CursoUdemy, CursoEmpresa, LearningPath, CursoGeneralXLearningPath


class Command(BaseCommand):
    help = 'Generates data'

    def handle(self, *args, **options):

        cant_rows = 1

        with transaction.atomic():
            cursos_udemy = CursoUdemyFactory.create_batch(cant_rows)
            self.stdout.write(self.style.SUCCESS('{} Cursos Udemy creados con exito').format(cant_rows))

            cursos_empresa = CursoEmpresaFactory.create_batch(cant_rows)
            self.stdout.write(self.style.SUCCESS('{} Cursos Empresa creados con exito').format(cant_rows))

            learning_paths = LearningPathFactory.create_batch(cant_rows)
            self.stdout.write(self.style.SUCCESS('{} Learning Paths creados con exito').format(cant_rows))

            curso_general_x_learning_paths = CursoGeneralXLearningPathFactory.create_batch(cant_rows*5)
            self.stdout.write(self.style.SUCCESS('{} CursoGeneralXLearningPath creados con exito').format(cant_rows))

            self.stdout.write(self.style.SUCCESS('Datos generados correctamente.'))
