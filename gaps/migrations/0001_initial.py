# Generated by Django 3.1.3 on 2023-05-27 22:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('login', '0001_initial'),
        ('personal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competencia',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('codigo', models.CharField(blank=True, max_length=12, null=True)),
                ('nombre', models.CharField(blank=True, max_length=100, null=True)),
                ('descripcion', models.CharField(blank=True, max_length=300, null=True)),
                ('activo', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='TipoCompetencia',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('abreviatura', models.CharField(blank=True, max_length=30, null=True)),
                ('nombre', models.CharField(blank=True, max_length=100, null=True)),
                ('descripcion', models.CharField(blank=True, max_length=300, null=True)),
                ('activo', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='NecesidadCapacitacion',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('descripcion', models.CharField(blank=True, max_length=200, null=True)),
                ('estado', models.IntegerField(blank=True, null=True)),
                ('nivelActual', models.IntegerField(blank=True, null=True)),
                ('nivelRequerido', models.IntegerField(blank=True, null=True)),
                ('nivelBrecha', models.IntegerField(blank=True, null=True)),
                ('tipo', models.IntegerField(blank=True, null=True)),
                ('activo', models.BooleanField(default=True)),
                ('competencia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gaps.competencia')),
                ('empleado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='login.employee')),
            ],
        ),
        migrations.CreateModel(
            name='CompetenciaXEmpleado',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('nivelActual', models.IntegerField(blank=True, null=True)),
                ('nivelRequerido', models.IntegerField(blank=True, null=True)),
                ('nivelBrecha', models.IntegerField(blank=True, null=True)),
                ('adecuacion', models.FloatField(blank=True, null=True)),
                ('tieneCertificado', models.BooleanField(default=False)),
                ('agregadoPorEmpleado', models.BooleanField(default=False)),
                ('requeridoParaPuesto', models.BooleanField(default=False)),
                ('activo', models.BooleanField(default=True)),
                ('competencia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gaps.competencia')),
                ('empleado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='login.employee')),
            ],
        ),
        migrations.CreateModel(
            name='CompetenciaXAreaXPosicion',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('nivelRequerido', models.IntegerField(blank=True, null=True)),
                ('activo', models.BooleanField(default=True)),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='personal.area')),
                ('competencia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gaps.competencia')),
                ('posicion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='personal.position')),
            ],
        ),
        migrations.AddField(
            model_name='competencia',
            name='tipo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gaps.tipocompetencia'),
        ),
    ]