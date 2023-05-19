# Generated by Django 3.1.3 on 2023-05-19 02:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('creationDate', models.DateTimeField(auto_now_add=True)),
                ('modifiedDate', models.DateTimeField(auto_now=True)),
                ('isActive', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True, default='')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='AreaxPosicion',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('creationDate', models.DateTimeField()),
                ('modifiedDate', models.DateTimeField()),
                ('isActive', models.BooleanField(default=True)),
                ('availableQuantity', models.IntegerField()),
                ('unavailableQuantity', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('creationDate', models.DateTimeField()),
                ('modifiedDate', models.DateTimeField()),
                ('isActive', models.BooleanField(default=True)),
                ('name', models.TextField(blank=True, default='')),
                ('code', models.CharField(blank=True, max_length=5)),
                ('description', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('creationDate', models.DateTimeField(auto_now_add=True)),
                ('modifiedDate', models.DateTimeField(auto_now=True)),
                ('isActive', models.BooleanField(default=True)),
                ('evaluationDate', models.DateTimeField()),
                ('hasComment', models.BooleanField()),
                ('generalComment', models.CharField(blank=True, max_length=500, null=True)),
                ('isFinished', models.BooleanField()),
                ('finalScore', models.FloatField(blank=True, null=True)),
                ('areaxPosicion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='evaluations_and_promotions.areaxposicion')),
            ],
        ),
        migrations.CreateModel(
            name='EvaluationType',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('creationDate', models.DateTimeField(auto_now_add=True)),
                ('modifiedDate', models.DateTimeField(auto_now=True)),
                ('isActive', models.BooleanField(default=True)),
                ('name', models.CharField(blank=True, max_length=40)),
                ('description', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('creationDate', models.DateTimeField(auto_now_add=True)),
                ('modifiedDate', models.DateTimeField(auto_now=True)),
                ('isActive', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=40)),
                ('benefits', models.TextField(blank=True, default='')),
                ('responsabilities', models.TextField(blank=True, default='')),
                ('description', models.TextField(blank=True, default='')),
                ('tipoJornada', models.TextField(blank=True, default='')),
                ('modalidadTrabajo', models.TextField(blank=True, default='')),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('creationDate', models.DateTimeField(auto_now_add=True)),
                ('modifiedDate', models.DateTimeField(auto_now=True)),
                ('isActive', models.BooleanField(default=True)),
                ('code', models.CharField(max_length=5)),
                ('name', models.TextField(blank=True, default='')),
                ('description', models.TextField(blank=True, default='')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='evaluations_and_promotions.category')),
            ],
        ),
        migrations.CreateModel(
            name='EvaluationxSubCategory',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('creationDate', models.DateTimeField(auto_now_add=True)),
                ('modifiedDate', models.DateTimeField(auto_now=True)),
                ('isActive', models.BooleanField(default=True)),
                ('hasComment', models.BooleanField(default=True)),
                ('comment', models.TextField(blank=True, default='')),
                ('score', models.FloatField(blank=True, null=True)),
                ('evaluation', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='evaluations_and_promotions.evaluation')),
                ('subCategory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='evaluations_and_promotions.subcategory')),
            ],
        ),
    ]
