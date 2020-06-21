# Generated by Django 3.0.7 on 2020-06-20 03:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trivia', '0004_auto_20200618_2227'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='score',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='game',
            name='date',
            field=models.DateField(default=datetime.date(2020, 6, 19)),
        ),
    ]