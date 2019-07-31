#!/usr/bin/env python
#-*- coding: UTF-8 -*-

"""
@version: Python3.6.4
@author:  Justinli

"""

import sys
import io
import time
from django.contrib.auth import get_user_model
from myauth.models import UserBi, MyAgent, Rooms, Combi, ChargeHistory
from chat.utils.tool import getredis
import django.utils.timezone as timezone
import datetime


MyUsers = get_user_model()
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def getuserbifromredis():
    error_list = []
    r = getredis()
    zx_total_key_1 = "_add_total" + time.strftime('%Y-%m-%d')
    zx_xima_total_key_1 = "_reduce_total" + time.strftime('%Y-%m-%d')
    sb_total_key_1 = "_sb_add_total" + time.strftime('%Y-%m-%d')
    sb_xima_total_key_1 = "_sb_reduce_total" + time.strftime('%Y-%m-%d')
    users = MyUsers.objects.filter(is_robot=False)
    if len(users) > 0:
        for user in users:
            agent = MyAgent.objects.filter(agent_id=user.agent_id)
            if len(agent) > 0:
                agent_name = agent[0].agent_name
            else:
                agent_name = "admin"
            zx_total_key = user.username + zx_total_key_1
            zx_xima_total_key = user.username + zx_xima_total_key_1
            sb_total_key = user.username + sb_total_key_1
            sb_xima_total_key = user.username + sb_xima_total_key_1
            zx_total = 0
            zx_xima_total = 0
            sb_total = 0
            sb_xima_total = 0
            yx_total = 0

            if r.exists(zx_total_key):
                zx_total = int(r.get(zx_total_key))
            if r.exists(zx_xima_total_key):
                zx_xima_total = int(r.get(zx_xima_total_key))
            if r.exists(sb_total_key):
                sb_total = int(r.get(sb_total_key))
            if r.exists(sb_xima_total_key):
                sb_xima_total = int(r.get(sb_xima_total_key))

            if zx_total == 0 and zx_xima_total == 0:
                continue
            else:
                syear = time.strftime('%Y')
                smonth = time.strftime('%m')
                sdy = time.strftime('%d')
                userbi = UserBi.objects.filter(username=user.username, date_time__year=syear, date_time__month=smonth, date_time__day=sdy)
                if len(userbi) > 0:
                    userbi[0].zx_xima_total = zx_xima_total
                    userbi[0].sb_xima_total = sb_xima_total
                    userbi[0].zx_total = zx_total
                    userbi[0].sb_total = sb_total
                    userbi[0].yx_total = yx_total
                    userbi[0].save()

                else:
                    try:
                        ubi = UserBi(username=user.username,agent_name=agent_name,
                                     zx_xima_total=zx_xima_total, sb_xima_total=sb_xima_total,zx_total=zx_total,
                                     sb_total=sb_total,yx_total=0)
                        ubi.save()
                    except:
                        return 1
        return 0
    else:
        return 1


def getuserbifromdb(date_time=None):
    date_time = date_time
    # ubi = UserBi.objects.filter(date_time=date_time)
    # if len(ubi) > 0:
    #     return ubi
    # else:
    if date_time is not None:
        ubi = UserBi.objects.filter(date_time=date_time)
        if len(ubi) > 0:
            return ubi
        else:
            return None
    else:
        result = getuserbifromredis()
        if result == 0:
            ubi = UserBi.objects.filter().order_by('-id')
            return ubi
        else:
            return None


def getcombifromredis():
    rooms = Rooms.objects.all()
    r = getredis()
    sb_total = 0
    com_sb_reduce_total = 0
    #台面总赢亏
    zx_total = 0
    #台面总洗码
    zx_xima_total = 0
    tui_lingshu_total = 0
    if len(rooms) > 0:
        for room in rooms:
            sb_total_keys = room.room_id + "_sb_total" + time.strftime('%Y-%m-%d')
            com_sb_reduce_key = room.room_id + "_sb_reduce_total" + time.strftime('%Y-%m-%d')
            zx_total_key = room.room_id + "shuyintotal" + time.strftime('%Y-%m-%d')
            zx_xima_total_key = room.room_id + "shutotal" + time.strftime('%Y-%m-%d')
            tui_lingshu_total_key = room.room_id + "_tui_lingshu" + time.strftime('%Y-%m-%d')
            if r.exists(tui_lingshu_total_key):
                tui_lingshu_total = tui_lingshu_total + int(r.get(tui_lingshu_total_key))
            if r.exists(sb_total_keys):
                sb_total = sb_total + int(r.get(sb_total_keys))
            if r.exists(com_sb_reduce_key):
                com_sb_reduce_total = com_sb_reduce_total + int(r.get(com_sb_reduce_key))
            if r.exists(zx_total_key):
                zx_total = zx_total + int(r.get(zx_total_key))
            if r.exists(zx_xima_total_key):
                zx_xima_total = zx_xima_total + int(r.get(zx_xima_total_key))
    else:
        return 1

    try:
        syear = time.strftime('%Y')
        smonth = time.strftime('%m')
        sdy = time.strftime('%d')
        combi = Combi.objects.filter(date_time__year=syear, date_time__month=smonth, date_time__day=sdy)
        if len(combi) > 0:
            combi[0].sb_total = sb_total
            #公司总数分
            combi[0].sb_com_total = com_sb_reduce_total 
            combi[0].sb_user_total =0 - com_sb_reduce_total
            combi[0].zx_total = zx_total
            combi[0].zx_xima_total =zx_xima_total
            combi[0].ls_com_total = tui_lingshu_total
            combi[0].save()
        else:
            if com_sb_reduce_total > 0:
                sb_com_total = sb_total - com_sb_reduce_total
            else:
                sb_com_total = com_sb_reduce_total
            combi = Combi(zx_total=zx_total, zx_xima_total=zx_xima_total,
                          sb_total=sb_total,sb_com_total=sb_com_total,sb_user_total=com_sb_reduce_total, ls_com_total=tui_lingshu_total)
            combi.save()
        # combis = Combi.objects.filter(date_time=time.strftime('%Y-%m-%d'))
        return 0
    except:
        return 1



def getcombifromdb(date_time=None):
    date_time = date_time
    # ubi = UserBi.objects.filter(date_time=date_time)
    # if len(ubi) > 0:
    #     return ubi
    # else:
    if date_time is not None:
        ubi = Combi.objects.filter(date_time=date_time)
        if len(ubi) > 0:
            return ubi
        else:
            return None
    else:
        result = getcombifromredis()
        if result == 0:
            ubi = Combi.objects.filter().order_by('-id')
            return ubi
        else:
            return None


def addChargeHistory(opusername, username, operator, content):
    date_time = time.strftime('%Y-%m-%d %H:%m')
    try:
        ch = ChargeHistory(opusername=opusername, username=username, operator=operator, content=content)
        ch.save()
        return 0
    except:
        return 1
