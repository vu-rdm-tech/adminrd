# Generated by Django 3.2.19 on 2023-06-06 08:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50)),
                ('type', models.CharField(choices=[('w', 'WBS-Element'), ('o', 'Order Number'), ('c', 'Cost Center item number'), ('u', 'unknown')], max_length=1)),
                ('vunetid', models.CharField(max_length=6)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255)),
                ('abbreviation', models.CharField(blank=True, max_length=255)),
                ('faculty', models.CharField(blank=True, max_length=255)),
                ('institute', models.CharField(blank=True, max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='MiscStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size_total', models.DecimalField(decimal_places=4, max_digits=8)),
                ('quotum_total', models.BigIntegerField()),
                ('users_total', models.IntegerField()),
                ('internal_users_total', models.IntegerField()),
                ('external_users_total', models.IntegerField()),
                ('projects_total', models.IntegerField(default=6)),
                ('collected', models.DateField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rdid', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('create_date', models.DateTimeField()),
                ('change_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('quotum', models.IntegerField(default=10)),
                ('admin_remarks', models.TextField(blank=True, default='')),
                ('internal_users', models.IntegerField()),
                ('external_users', models.IntegerField()),
                ('delete_date', models.DateField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('budget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.budget')),
                ('department', models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='projects.department')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rdid', models.IntegerField()),
                ('username', models.CharField(blank=True, max_length=12)),
                ('name', models.CharField(max_length=50)),
                ('email', models.CharField(blank=True, max_length=50)),
                ('backend', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=50)),
                ('last_login', models.DateTimeField(auto_now_add=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.DecimalField(decimal_places=4, max_digits=8)),
                ('quotum', models.IntegerField()),
                ('collected', models.DateField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='projects.project')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='owner_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.user'),
        ),
        migrations.AddConstraint(
            model_name='department',
            constraint=models.UniqueConstraint(fields=('abbreviation', 'faculty'), name='unique_abbreviation_faculty'),
        ),
        migrations.AddConstraint(
            model_name='budget',
            constraint=models.UniqueConstraint(fields=('code',), name='unique_code'),
        ),
    ]
