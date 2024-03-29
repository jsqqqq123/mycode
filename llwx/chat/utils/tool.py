#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
@version: Python2.7.10
@author:  Justinli

"""

from django.contrib.auth import get_user_model
from myauth.models import MyBi, UserOperator
import re
import redis
import hashlib
import random
import time
import ast
import json
import logging
from django.db import connections

logger = logging.getLogger(__name__)

MyUsers = get_user_model()

result_json = {
    'z': "2",
    'z,zd': "18",
    'z,xd': "10",
    'z,sd': "26",
    'x': "1",
    'x,zd': "17",
    'x,xd': "9",
    'x,sd': "25",
    'h': "4",
    'h,zd': "20",
    'h,xd': "12",
    'sb': "28",
}

POOL = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True, db=0)

def getjufromstr(bac_num):
    res = "(?P<ju>[0-9]+)"
    myju = re.findall(res, bac_num)
    if len(myju) == 2:
        return(myju[1])
    else:
        return None

def getredis():
    try:
        return redis.StrictRedis(connection_pool=POOL)
    except:
        return None


def fromStrParseInt(data):
    pmatch = "(?P<xue>[0-9]+)"
    roomnum = re.findall(pmatch, data)
    return roomnum


def getRoadFromRedis(room_id, result, bac_num):
    bac_num_str = getjufromstr(bac_num)
    if bac_num_str is not None:
        bac_num_int = int(bac_num_str)
    else:
        bac_num_int = None
    print(bac_num_int)
    roadkey = room_id + "_road"
    resultkey = room_id + "_road_total"
    r = getredis()
    ret = {}
    try:
        if r.exists(roadkey):
            pre_result = r.get(roadkey)
            pre_result_list = pre_result.split(",")
            if len(pre_result_list) >= bac_num_int:
                pre_result_list[bac_num_int - 1] = result_json[result]
                now_result = ",".join(pre_result_list)
            elif len(pre_result_list) > 0:
                now_result = pre_result + "," + result_json[result]
            else:
                now_result = result_json[result]
            r.set(roadkey, now_result)
        else:
            now_result = result_json[result]
            r.set(roadkey, now_result)

        pre_total = [0, 0, 0, 0, 0]

        next_result_list = now_result.split(',')
        pre_total[0] = str(next_result_list.count('2') + next_result_list.count('18') + next_result_list.count(
            '10') + next_result_list.count('26'))
        pre_total[1] = str(next_result_list.count('1') + next_result_list.count('17') + next_result_list.count(
            '9') + next_result_list.count('25'))
        pre_total[2] = str(next_result_list.count('4') + next_result_list.count('20') + next_result_list.count(
            '12') + next_result_list.count('28'))
        pre_total[3] = str(next_result_list.count('18') + next_result_list.count('17') + next_result_list.count(
            '20') + next_result_list.count('28'))
        pre_total[4] = str(next_result_list.count('10') + next_result_list.count('9') + next_result_list.count(
            '12') + next_result_list.count('28'))
        print(next_result_list)
        pre_total_str = ",".join(pre_total)
        print(pre_total_str)
        r.set(resultkey, pre_total_str)
        ret['tongji'] = pre_total_str
        ret['result_list'] = now_result
        print(ret)
        return ret
    except:
        return None


def getRoadFromRedisAPI(room_id):
    roadkey = room_id + "_road"
    resultkey = room_id + "_road_total"
    r = getredis()
    ret = {}
    try:
        if r.exists(roadkey):
            now_result = r.get(roadkey)
            r.set(roadkey, now_result)
        else:
            now_result = ""
        pre_total = [0, 0, 0, 0, 0]
        next_result_list = now_result.split(',')
        pre_total[0] = str(next_result_list.count('2') + next_result_list.count('18') + next_result_list.count(
            '10') + next_result_list.count('26'))
        pre_total[1] = str(next_result_list.count('1') + next_result_list.count('17') + next_result_list.count(
            '9') + next_result_list.count('25'))
        pre_total[2] = str(next_result_list.count('4') + next_result_list.count('20') + next_result_list.count(
            '12') + next_result_list.count('28'))
        pre_total[3] = str(next_result_list.count('18') + next_result_list.count('17') + next_result_list.count(
            '20') + next_result_list.count('28'))
        pre_total[4] = str(next_result_list.count('10') + next_result_list.count('9') + next_result_list.count(
            '12') + next_result_list.count('28'))
        pre_total_str = ",".join(pre_total)
        r.set(resultkey, pre_total_str)
        ret['tongji'] = pre_total_str
        ret['result_list'] = now_result
        return ret
    except:
        return None


def historyChatRoom(room_name, bac_num):
    room_name = room_name
    bac_num = bac_num
    ret = {}
    r = getredis()
    if room_name is not None and bac_num is not None:
        try:
            hkeys = 'h' + room_name + bac_num + '*'
            filename = 'log/h' + room_name + bac_num + '.log'
            keys = r.keys(hkeys)
            if len(keys) > 0:
                with open(filename, 'a+') as f:
                    for key in keys:
                        f.write(r.get(key) + '\n')
                ret['code'] = 0
                ret['msg'] = "历史记录写入成功"
            else:
                ret['code'] = 1
                ret['msg'] = "没有历史记录"
        except:
            ret['code'] = 1
            ret['msg'] = "文件写入错误"
    else:
        ret['code'] = 1
        ret['msg'] = "没有历史记录"

    return ret


def parseEndStatus(message):
    touzhu_list = ['z', 'x', 'h', 's']
    if len(message) > 2 and message[0].lower() in touzhu_list and message[-2].isdigit():
        return 1
    else:
        return 0


def hashmd5():
    randname = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba1234567890', 7))
    md5str = randname + str(time.time())
    md5str = md5str.encode('utf-8')
    hmd5 = hashlib.md5()
    hmd5.update(md5str)
    user_id_md5 = hmd5.hexdigest()
    return user_id_md5


def checkUserMoney(username):
    r = getredis()
    money_key = username + "_money"
    try:
        myuser = MyUsers.objects.get(username=username)
        mybi = MyBi.objects.filter(user_id=myuser)
        if len(mybi) > 0:
            if r.exists(money_key):
                my_money = r.get(money_key)
                if mybi[0].cur_m != my_money:
                    mybi[0].cur_m = my_money
                    mybi[0].save()
        return 0
    except:
        return 1


# 单用户操作记录表
def userOperatorLog(username, xueshu, xiazhu, xiazhu_money, result, result_money):
    # xiazhu = str(xiazhu).replace(",", "_")
    # result = str(result).replace(",", "_")
    try:
        uo = UserOperator(username=username, bacc_num=xueshu, xiazhu=xiazhu, pre_yue=xiazhu_money, result=result,
                          after_yue=result_money)
        # uo = UserOperator(username="lixiaoding", bacc_num="1ju136xue", xiazhu="z100,h1000", pre_yue=90000,result="z,zd", after_yue=100000,xiazhu_date="12:31")
        uo.save()
    except:
        print("用户操作记录出错")


def betparse(bet):
    if bet[0:2].isalpha():
        return bet[0:2], bet[2:len(bet)]
    else:
        return bet[0], bet[1:len(bet)]


# 显示台面是否流局 用于 consumer里的  show 之后
def show_admin_bac(room_name, bac_num):
    r = getredis()
    ret = {}
    tui_key = room_name + "_tui" + time.strftime('%Y-%m-%d')
    tui_total_set_key = "com_tui_total_setting"
    tui_lingshu_cur_key = room_name + "_tui_lingshu_cur"
    liuju_set_key = room_name + "_liuju" + time.strftime('%Y-%m-%d')
    starttouzhu = 5000
    if r.exists(tui_total_set_key):
        starttouzhu = int(r.get(tui_total_set_key))
    showadminkey = "showbac_" + room_name + "_" + bac_num

    z_total = 0
    x_total = 0
    sb_total = 0
    try:
        robot_list = MyUsers.objects.filter(is_robot=True)
        if len(robot_list) > 0:
            robot_list_username = [robot.username for robot in robot_list]
        else:
            robot_list_username = []
    except:
        robot_list_username = []
    r = getredis()
    if r.exists(showadminkey):
        mybets = r.get(showadminkey)
        mybet_list = ast.literal_eval(mybets)
        for users in mybet_list:
            if users["username"] not in robot_list_username:
                betlist = users["userbacc"].split(',')

                for bet in betlist:
                    if len(bet) > 1:
                        (betwhich, betnumber) = betparse(bet)
                        if betwhich == "z":
                            z_total = z_total + int(betnumber)
                        elif betwhich == "x":
                            x_total = x_total + int(betnumber)
                        elif betwhich == "sb":
                            sb_total = sb_total + int(betnumber)
        if z_total - x_total >= starttouzhu:
            # room001 房间传输message   room001 js 弹出对话框
            # 同时将这个记录到redis中 用于 结算的时候 牌面总输赢
            tui_lingshu_cur = (z_total - x_total) % 1000
            r.set(tui_lingshu_cur_key, tui_lingshu_cur)
            tui_msg = "z" + str(z_total - x_total - tui_lingshu_cur)
            ret["code"] = 0
            ret["msg"] = "第" + bac_num + ": 请推 【庄】" + str(z_total - x_total - tui_lingshu_cur)
            r.set(tui_key, tui_msg)
            return ret
        elif x_total - z_total >= starttouzhu:
            tui_lingshu_cur = (x_total - z_total) % 1000
            r.set(tui_lingshu_cur_key, tui_lingshu_cur)
            tui_msg = "x" + str(x_total - z_total - tui_lingshu_cur)
            ret["code"] = 0
            ret["msg"] = "第" + bac_num + ": 请推 【闲】" + str(x_total - z_total - tui_lingshu_cur)
            r.set(tui_key, tui_msg)
            return ret
        else:
            ret["code"] = 0
            ret["msg"] = bac_num + "----本局流局----"
            r.set(tui_key, "k000")
            r.set(tui_lingshu_cur_key, 0)
            return ret
            # ret["code"] = 1
            # op_result = liuju_operator(showadminkey)
            # if op_result == 0:
            #     ret["msg"] = "@所有人:" + bac_num + "---本局流局 ### 所有下注将自动还回给各位"
            # else:
            #     ret["msg"] = "@所有人:" + bac_num + "---本局流局 ### 所有下注将后续手动还回给各位"
            # return ret


#流局， 将钱还给用户
def liuju_operator(showadminkey):
    showadminkey = showadminkey
    backshowadminkey = showadminkey + "_bak"
    r = getredis()
    if r.exists(showadminkey):
        mybets = r.get(showadminkey)
        mybet_list = ast.literal_eval(mybets)
        for users in mybet_list:
            money_key = users["username"] + "_money"
            yue_money = int(users["usermoney"])
            if r.exists(money_key):
                betlist = users["userbacc"].split(',')
                for bet in betlist[:-1]:
                    (betwhich, betnumber) = betparse(bet)
                    if betwhich == "sb":
                        yue_money = yue_money + int(betnumber) * 3
                    else:
                        yue_money = yue_money + int(betnumber)
            r.set(money_key, yue_money)
        r.set(backshowadminkey, mybets)
        return 0
    else:
        return 1


# 用于处理官方推码总输赢等
def jiesuan_admin(roomname, result, bac_num):

    betinfo = {
        "z": 0.95,
        "x": 1,
        "zd": 11,
        "xd": 11,
        "h": 8,
        "sb": 1,
    }
    tui_back_key = roomname + "_tui" + bac_num 
    tui_key = roomname + "_tui" + time.strftime('%Y-%m-%d')
    liuju_set_key = roomname + "_liuju" + time.strftime('%Y-%m-%d')
    liuju_total_set_key = roomname + "_liuju_total" + time.strftime('%Y-%m-%d')
    shuyin_total_key = roomname + "shuyintotal" + time.strftime('%Y-%m-%d')
    shutotal_key = roomname + "shutotal" + time.strftime('%Y-%m-%d')
    tui_lingshu_total_key = roomname + "_tui_lingshu" + time.strftime('%Y-%m-%d')
    tui_lingshu_cur_key = roomname + "_tui_lingshu_cur"
    result_list = result.split(",")
    r = getredis()
    if r.exists(liuju_set_key):
        liuju_str = r.get(liuju_set_key)
        if r.exists(liuju_total_set_key):
            liuju_total = int(r.get(liuju_total_set_key))
        else:
            liuju_total = 0
    else:
        liuju_str = None
        liuju_total = 0
    if r.exists(tui_key):
        if r.exists(shuyin_total_key):
            shuyintotal = int(r.get(shuyin_total_key))
        else:
            shuyintotal = 0
        if r.exists(shutotal_key):
            shutotal = int(r.get(shutotal_key))
        else:
            shutotal = 0
        if r.exists(tui_lingshu_total_key):
            tui_lingshu_total = int(r.get(tui_lingshu_total_key))
        else:
            tui_lingshu_total = 0
        if r.exists(tui_lingshu_cur_key):
            tui_lingshu_cur = int(r.get(tui_lingshu_cur_key))
        else:
            tui_lingshu_cur = 0
        tui_total_str = r.get(tui_key)
        r.set(tui_back_key, tui_total_str)
        r.expire(tui_back_key, 86400)
        (betwhich, betnumber) = betparse(tui_total_str)
        if betwhich in result_list:
            if betwhich == "z":
                shuyintotal = int(int(betnumber) * 0.95) + shuyintotal
            else:
                shuyintotal = int(betnumber) + shuyintotal
            tui_lingshu_total = tui_lingshu_total - tui_lingshu_cur
            if liuju_str is not None:
                (liuwhich, liunumber) = betparse(liuju_str)
                liuju_total = liuju_total - int(int(liunumber) * betinfo[betwhich])
        elif "h" in result_list:
            r.set(shutotal_key, shutotal)
            r.expire(shutotal_key, 172800)
        else:
            shuyintotal = shuyintotal - int(betnumber)
            shutotal = shutotal + int(betnumber)
            r.set(shutotal_key, shutotal)
            r.expire(shutotal_key, 172800)
            tui_lingshu_total = tui_lingshu_total + tui_lingshu_cur
            if liuju_str is not None:
                (liuwhich, liunumber) = betparse(liuju_str)
                liuju_total = liuju_total + int(liunumber)

        r.set(tui_lingshu_total_key, tui_lingshu_total)
        r.expire(shutotal_key, 172800)
        r.set(shuyin_total_key, shuyintotal)
        r.expire(shuyin_total_key, 172800)
        r.set(liuju_total_set_key, liuju_total)
        return 0
    else:
        return 1


# 用于更改官方推码总输赢等
def change_jiesuan_admin(roomname, result, bac_num):
    betinfo = {
        "z": 0.95,
        "x": 1,
        "zd": 11,
        "xd": 11,
        "h": 8,
        "sb": 1,
    }
    tui_back_key = roomname + "_tui" + bac_num
    shuyin_total_key = roomname + "shuyintotal" + time.strftime('%Y-%m-%d')
    shutotal_key = roomname + "shutotal" + time.strftime('%Y-%m-%d')
    tui_lingshu_total_key = roomname + "_tui_lingshu" + time.strftime('%Y-%m-%d')
    tui_lingshu_cur_key = roomname + "_tui_lingshu_cur"
    result_list = result.split(",")
    r = getredis()
    if r.exists(tui_back_key):
        if r.exists(shuyin_total_key):
            shuyintotal = int(r.get(shuyin_total_key))
        else:
            shuyintotal = 0
        if r.exists(shutotal_key):
            shutotal = int(r.get(shutotal_key))
        else:
            shutotal = 0
        if r.exists(tui_lingshu_total_key):
            tui_lingshu_total = int(r.get(tui_lingshu_total_key))
        else:
            tui_lingshu_total = 0
        if r.exists(tui_lingshu_cur_key):
            tui_lingshu_cur = int(r.get(tui_lingshu_cur_key))
        else:
            tui_lingshu_cur = 0
        tui_total_str = r.get(tui_back_key)
        (betwhich, betnumber) = betparse(tui_total_str)
        if betwhich in result_list:
            shuyintotal = int(betnumber) + shuyintotal * 2
            tui_lingshu_total = tui_lingshu_total - tui_lingshu_cur * 2
        else:
            shuyintotal = shuyintotal - int(betnumber) * 2
            shutotal = shutotal + int(betnumber) * 2
            r.set(shutotal_key, shutotal)
            r.expire(shutotal_key, 172800)
            tui_lingshu_total = tui_lingshu_total + tui_lingshu_cur * 2
        r.set(shuyin_total_key, shuyintotal)
        r.expire(shuyin_total_key, 172800)
        r.set(tui_lingshu_total_key, tui_lingshu_total)
        r.expire(shutotal_key, 172800)
        return 0
    else:
        return 1


def zx_count(zpai, xpai):
    z3 = 0
    x3 = 0
    if len(zpai) == 4:
        z1 = zpai[1]
        z2 = zpai[3]
    elif len(zpai) == 6:
        z1 = zpai[1]
        z2 = zpai[3]
        z3 = zpai[5]


    if len(xpai) == 4:
        x1 = xpai[1]
        x2 = xpai[3]
    elif len(xpai) == 6:
        x1 = xpai[1]
        x2 = xpai[3]
        x3 = xpai[5]
    if z1 in ["j","q","k"]:
        z1 = 0
    if z2 in ["j","q","k"]:
        z2 = 0
    if z3 in ["j","q","k"]:
        z3 = 0

    if x1 in ["j","q","k"]:
        x1 = 0
    if x2 in ["j","q","k"]:
        x2 = 0
    if x3 in ["j","q","k"]:
        x3 = 0
    rez = (int(z1) + int(z2) + int(z3)) % 10
    rex = (int(x1) + int(x2) + int(x3)) % 10
    return [rez, rex]


def async_db(username, money):
    username = username
    money = money
    if username is not None and username != "" and money is not None and money != "":
        close_old_connections()
        user = MyUsers.objects.filter(username=username)
        if len(user) > 0:
            mybi = MyBi.objects.filter(user_id=user[0])
            if len(mybi) > 0:
                mybi[0].cur_m = money
                mybi[0].save()
            return 0
    else:
        return 1

#删除无效链接， 根据django.db里的 __init__ 来写的
def close_old_connections():
    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()
