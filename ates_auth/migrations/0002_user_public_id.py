# Generated by Django 4.2.4 on 2023-08-27 12:06

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ates_auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='public_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Public ID'),
        ),
    ]