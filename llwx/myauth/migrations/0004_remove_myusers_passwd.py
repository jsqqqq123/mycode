# Generated by Django 2.1.1 on 2018-11-07 02:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myauth', '0003_auto_20181102_2022'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='myusers',
            name='passwd',
        ),
    ]