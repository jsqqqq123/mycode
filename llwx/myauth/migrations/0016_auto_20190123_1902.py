# Generated by Django 2.2.dev20190101154022 on 2019-01-23 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myauth', '0015_auto_20190104_1419'),
    ]

    operations = [
        migrations.CreateModel(
            name='Combi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.CharField(max_length=50, verbose_name='时间')),
                ('zx_total', models.IntegerField()),
                ('zx_xima_total', models.IntegerField()),
                ('sb_total', models.IntegerField()),
                ('sb_com_total', models.IntegerField()),
                ('sb_user_total', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='UserBi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50, verbose_name='用户名')),
                ('agent_name', models.CharField(max_length=50, verbose_name='代理别名')),
                ('zx_xima_total', models.IntegerField()),
                ('sb_xima_total', models.IntegerField()),
                ('zx_total', models.IntegerField()),
                ('sb_total', models.IntegerField()),
                ('yx_total', models.IntegerField()),
                ('date_time', models.CharField(max_length=50, verbose_name='时间')),
            ],
        ),
        migrations.AddField(
            model_name='myusers',
            name='fencheng',
            field=models.IntegerField(default=10, verbose_name='分成比例 %'),
        ),
    ]