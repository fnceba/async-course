# Generated by Django 4.2.4 on 2023-08-14 07:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.PositiveSmallIntegerField(choices=[(1, 'Admin'), (2, 'Boss'), (3, 'Developer'), (4, 'Manager'), (5, 'Accountant')], verbose_name='Роль')),
                ('name', models.CharField(blank=True, default='', max_length=50, verbose_name='Имя')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(verbose_name='Описание задачи')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'In Progress'), (2, 'Done')], default=0, verbose_name='Статус задачи')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='task_tracker.user', verbose_name='Ответственный за выполнение задачи')),
            ],
        ),
    ]
