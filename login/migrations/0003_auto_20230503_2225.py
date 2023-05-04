# Generated by Django 3.1.3 on 2023-05-04 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_auto_20230501_1324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='creationDate',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='employee',
            name='modifiedDate',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='creationDate',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='modifiedDate',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='creationDate',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='modifiedDate',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
