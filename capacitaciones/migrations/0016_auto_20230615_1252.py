# Generated by Django 3.1.3 on 2023-06-15 17:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('capacitaciones', '0015_auto_20230615_1245'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='detallerubricaexamenxempleado',
            name='detalle_rubrica_examen',
        ),
        migrations.RemoveField(
            model_name='detallerubricaexamenxempleado',
            name='empleado',
        ),
        migrations.RemoveField(
            model_name='rubricaexamen',
            name='learning_path',
        ),
        migrations.RemoveField(
            model_name='rubricaexamen',
            name='rubrica_examen_x_empleado',
        ),
        migrations.RemoveField(
            model_name='rubricaexamenxempleado',
            name='empleado',
        ),
        migrations.RemoveField(
            model_name='rubricaexamenxempleado',
            name='rubrica_examen',
        ),
        migrations.DeleteModel(
            name='DetalleRubricaExamen',
        ),
        migrations.DeleteModel(
            name='DetalleRubricaExamenXEmpleado',
        ),
        migrations.DeleteModel(
            name='RubricaExamen',
        ),
        migrations.DeleteModel(
            name='RubricaExamenXEmpleado',
        ),
    ]
