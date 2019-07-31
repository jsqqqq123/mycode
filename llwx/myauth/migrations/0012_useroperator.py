# Generated by Django 2.1.1 on 2018-12-31 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myauth', '0011_auto_20181224_1206'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserOperator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, verbose_name='用户名')),
                ('bacc_num', models.CharField(max_length=15, verbose_name='靴数')),
                ('xiazhu', models.CharField(max_length=10, verbose_name='用户下注')),
                ('pre_yue', models.CharField(max_length=10, verbose_name='下注后余额')),
                ('result', models.CharField(max_length=10, verbose_name='本靴结果')),
                ('after_yue', models.CharField(max_length=15, verbose_name='结算后余额')),
                ('xiazhu_date', models.CharField(max_length=15, verbose_name='下注时间')),
            ],
        ),
    ]