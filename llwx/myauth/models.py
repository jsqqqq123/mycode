from django.db import models

# Create your models here.


from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
import django.utils.timezone as timezone
from datetime import datetime

class MyUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('Users must have an username')
        user = self.model(
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(
            username,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUsers(AbstractBaseUser):
    username = models.CharField(verbose_name="用户名", max_length=255, unique=True)
    nickname = models.CharField(verbose_name='昵称', max_length=255, unique=True, default='l')
    user_id = models.CharField(verbose_name="用户id",  max_length=255, unique=True, default='0000000000000000')
    avatar_url = models.CharField(verbose_name="用户头像", max_length=255, default="")
    agent_id = models.CharField(verbose_name="代理id", max_length=255)
    is_admin = models.BooleanField(verbose_name="管理员", default=False)
    state = models.BooleanField(verbose_name="用户状态", default=True)
    is_vip = models.IntegerField(verbose_name="vip", default=0)
    is_active = models.BooleanField(verbose_name="用户激活", default=True)
    is_talke = models.BooleanField(verbose_name="用户禁言", default=True)
    is_robot = models.BooleanField(verbose_name="机器人", default=False)
    last_login = models.DateField(verbose_name="最后登陆时间", auto_now=True)
    register_time = models.DateField(verbose_name="注册时间", auto_now_add=True)
    fencheng = models.IntegerField(verbose_name="分成比例 %", default=10) 
    type_1 = models.CharField(max_length=255)
    type_2 = models.CharField(max_length=255)
    type_3 = models.CharField(max_length=255)

    objects = MyUserManager()
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class MyBi(models.Model):
    user_id = models.OneToOneField(MyUsers, on_delete=models.CASCADE)
    total_m = models.CharField(verbose_name="历史总分", max_length=50, default="0")
    cur_m = models.CharField(verbose_name="当前总分", max_length=50, default="0")
    get_m = models.CharField(verbose_name="历史总下分", max_length=50, default="0")
    recharge_lasttime = models.CharField(verbose_name="最后充值时间",max_length=50)
    withdraw_lastime = models.CharField(verbose_name="最后下分时间",max_length=50)


class MyAgent(models.Model):
    agent_id = models.CharField(verbose_name='代理id', max_length=20, unique=True, default="000000000000")
    agent_name = models.CharField(verbose_name='代理名', max_length=50, unique=True, default="XX公司")
    username = models.CharField(verbose_name='用户名', max_length=50, unique=True, default="root")
    father_agent = models.CharField(verbose_name='初始代理', max_length=20, default="0")
    pre_agent = models.CharField(verbose_name='上一级代理id', max_length=20, default="0")
    next_agent = models.CharField(verbose_name='下一级代理id', max_length=20, default="0")
    agent_percent = models.IntegerField(verbose_name='代理分成比例%', default=10)


class Rooms(models.Model):
    room_id = models.CharField(verbose_name='房间id号', max_length=10, unique=True, default="room001")
    room_name = models.CharField(verbose_name='房间名', max_length=20, unique=True, default="百丽宫")
    room_video = models.CharField(verbose_name='房间视频地址', max_length=255, default='ws://lelewuxian.com')
    is_active = models.BooleanField(verbose_name="房间开启状态", default=True)
    is_public = models.BooleanField(verbose_name="房间是否公开", default=True)
    is_vip = models.BooleanField(verbose_name="房间是否属于vip", default=False)
    passwd = models.CharField(verbose_name='vip房间密码', max_length=10, default="123456")
    agent_id = models.CharField(verbose_name='房间所属于agent', max_length=20, default="000000000000")
    room_admin = models.CharField(verbose_name='房间管理员', max_length=20, default="root")


class UserOperator(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=255)
    bacc_num = models.CharField(verbose_name="靴数", max_length=15)
    xiazhu = models.CharField(verbose_name="用户下注", max_length=50)
    pre_yue = models.CharField(verbose_name="下注后余额", max_length=10)
    result = models.CharField(verbose_name="本靴结果", max_length=10)
    after_yue = models.CharField(verbose_name="结算后余额", max_length=15)
    #xiazhu_date = models.CharField(verbose_name="下注时间", max_length=15)
    xiazhu_date = models.DateTimeField(verbose_name="下注时间", default=timezone.now)

class UserBi(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=50)
    agent_name = models.CharField(verbose_name="代理别名", max_length=50)
    zx_xima_total = models.IntegerField()
    sb_xima_total = models.IntegerField()
    zx_total = models.IntegerField()
    sb_total = models.IntegerField()
    yx_total = models.IntegerField()
    #date_time = models.CharField(verbose_name="时间", max_length=50)
    date_time = models.DateTimeField(verbose_name="时间", default=timezone.now)

class Combi(models.Model):
    #date_time = models.CharField(verbose_name="时间", max_length=50)
    date_time = models.DateTimeField(verbose_name="时间", default=timezone.now)
    zx_total = models.IntegerField()
    zx_xima_total = models.IntegerField()
    sb_total = models.IntegerField()
    sb_com_total = models.IntegerField()
    sb_user_total = models.IntegerField()
    ls_com_total = models.IntegerField(default=0)


class ChargeHistory(models.Model):
    #date_time = models.CharField(verbose_name="时间", max_length=50)
    date_time = models.DateTimeField(verbose_name="时间", default=timezone.now)
    opusername = models.CharField(verbose_name="操作人", max_length=50)
    username = models.CharField(verbose_name="用户名", max_length=50)
    operator = models.CharField(verbose_name="(上分/下分)", max_length=10)
    content = models.CharField(verbose_name="操作内容", max_length=500)
