# Generated by Django 2.0.5 on 2019-09-03 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        # ('avion', '0003_auto_20190809_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='aircraft',
            name='challenge',
            field=models.BooleanField(default=False),
        ),
    ]
