# Generated by Django 3.1.3 on 2023-06-06 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capacitaciones', '0008_auto_20230605_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cursoudemy',
            name='preguntas',
            field=models.JSONField(null=True),
        ),
    ]