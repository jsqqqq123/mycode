# Generated by Django 2.1.1 on 2018-12-04 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myauth', '0007_myagent_rooms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myagent',
            name='father_agent',
            field=models.CharField(default='0', max_length=20, verbose_name='初始代理'),
        ),
    ]
