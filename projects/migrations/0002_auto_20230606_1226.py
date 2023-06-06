# Generated by Django 3.2.19 on 2023-06-06 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='change_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='end_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='external_users',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='project',
            name='internal_users',
            field=models.IntegerField(default=1),
        ),
    ]
