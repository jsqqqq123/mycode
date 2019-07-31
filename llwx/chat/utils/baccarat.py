#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
@version: Python2.7.10
@author:  Justinli

"""

import json
import re
import ast
from django.contrib.auth import get_user_model
from .tool import getredis, userOperatorLog, async_db
import time
import logging


logger = logging.getLogger(__name__)
r = getredis()

# r = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True, db=0)


myuser = get_user_model()

# key的规则 room_几靴_几局_username   value 'username#余额#庄300&闲400'
# value {
#           'username':'庄300&闲400'，
#           'username': '庄300&闲400',
#       }



# 根据message解析下注的用户跟下注的金额是否合规
# 并构造message消息传递给前端聊天室 @消息格式


xiazhumatch = "(?P<un>[a-z]+[0-9]+)"
zfmatch = "(?P<uu>[a-z]+)"
valuematch = "(?P<vu>[0-9]+)"
zhmodel = re.compile(u'[\u4e00-\u9fa5]')
parsematch = "(?P<xt>[a-z]+)(?P<xv>[0-9]+)"
allow_list = ['z', 'x', 'zd', 'xd', 'h', 'sb']


# 解析投注数据用的  content 一般是  x100 这样类型的，暂时不支持 x100h100  这样连续的
# return 数据里包括 room_name,  bac_num, money, yuemoney, xiazhu_type

def message_parse(message):
    # message = json.loads(message)
    ret = {}
    user_zx_min_key = "user_zx_min_setting"
    user_zx_max_key = "user_zx_max_setting"
    user_d_max_key = "user_d_max_setting"
    user_h_max_key = "user_h_max_setting"
    user_sb_max_key = "user_sb_max_setting"
    user_sb_min_key = "user_sb_min_setting"
    user_d_min_key = "user_d_min_setting"
    user_h_min_key = "user_h_min_setting"
    user_zx_max = 1000000
    user_zx_min = 100
    user_d_max = 100000
    user_d_min = 100
    user_h_max = 100000
    user_h_min = 100
    user_sb_max = 100000
    user_sb_min = 100
    if r.exists(user_zx_max_key):
        user_zx_max = int(r.get(user_zx_max_key))
    if r.exists(user_zx_min_key):
        user_zx_min = int(r.get(user_zx_min_key))
    if r.exists(user_d_max_key):
        user_d_max = int(r.get(user_d_max_key))
    if r.exists(user_d_min_key):
        user_d_min = int(r.get(user_d_min_key))
    if r.exists(user_h_max_key):
        user_h_max = int(r.get(user_h_max_key))
    if r.exists(user_h_min_key):
        user_h_min = int(r.get(user_h_min_key))
    if r.exists(user_sb_max_key):
        user_sb_max = int(r.get(user_sb_max_key))
    if r.exists(user_sb_min_key):
        user_sb_min = int(r.get(user_sb_min_key))

    allvalue = 0
    username = message['from_username']
    room_name = message['room_name']
    bac_num = message['bac_num']
    content = message['content']
    msg_type = message['msg_type']
    # myuser_bi = MyBi.objects.filter(username=username)
    user_key = username + "_money"
    try:
        if msg_type == 2:
            # 撤销操作
            if content.lower() == "c":
                myrediskey = "xiazhu_" + room_name + '_' + bac_num + '_' + username
                mytotal_money = 0
                if r.exists(myrediskey):
                    mytouzhu = json.loads(r.get(myrediskey))
                    for mykeyv, myval in mytouzhu["userbacc"].items():
                        if mykeyv == "sb":
                            mytotal_money = mytotal_money + int(myval) * 3
                        else:
                            mytotal_money = mytotal_money + int(myval)
                    if r.exists(user_key):
                        yue_moeny = int(mytouzhu["usermoney"]) + mytotal_money
                        r.set(user_key, yue_moeny)
                    r.delete(myrediskey)
                    ret["code"] = 1
                    ret["msg"] = '撤销成功'
                    return ret
                else:
                    ret["code"] = 1
                    ret["msg"] = '没有需要撤销的投注'
                    return ret
            # 投注操作
            baccparse_ret = bacc_parse(content)
            if baccparse_ret == 1:
                ret["code"] = 1
                ret["msg"] = "下注格式错误"
                return ret
            valuealllist = re.findall(valuematch, content.lower())
            for vl in valuealllist:
                allvalue += int(vl)
            if r.exists(user_key):
                user_money = r.get(user_key)
                if int(allvalue) > int(user_money):
                    ret["code"] = 1
                    ret["msg"] = "余额不足"
                    return ret
            alllist = re.findall(xiazhumatch, content.lower())

            for xz in alllist:

                for xiazhulist in re.findall(parsematch, xz):
                    xiazhu_type, money = xiazhulist
                    print(xiazhu_type, money)
                    if xiazhu_type == "z" or xiazhu_type == "x":
                        if int(money) < int(user_zx_min):
                            ret["code"] = 1
                            ret["msg"] = "庄闲金额没有达到下线"
                            return ret

                        elif int(money) > int(user_zx_max):
                            ret["code"] = 1
                            ret["msg"] = "庄闲金额超出上线"
                            return ret
                    elif xiazhu_type == "h":
                        if int(money) < int(user_h_min):
                            ret["code"] = 1
                            ret["msg"] = "押和的金额没有达到下线"
                            return ret

                        elif int(money) > int(user_h_max):
                            ret["code"] = 1
                            ret["msg"] = "押和的金额超出上线"
                            return ret
                    elif xiazhu_type == "zd" or xiazhu_type == "xd":
                        if int(money) < int(user_d_min):
                            ret["code"] = 1
                            ret["msg"] = "庄对或闲对金额没有达到下线"
                            return ret

                        elif int(money) > int(user_d_max):
                            ret["code"] = 1
                            ret["msg"] = "庄对或闲对金额超出上线"
                            return ret
                    elif xiazhu_type == "sb":
                        if int(money) < int(user_sb_min):
                            ret["code"] = 1
                            ret["msg"] = "三宝金额没有达到下线"
                            return ret

                        elif int(money) > int(user_sb_max):
                            ret["code"] = 1
                            ret["msg"] = "三宝金额超出上线"
                            return ret
                    if r.exists(user_key):
                        user_money = r.get(user_key)
                    else:
                        ret["code"] = 1
                        ret["msg"] = "余额不足"
                        return ret
                    if xiazhu_type == 'sb':
                        yue_money = int(user_money) - int(money) * 3
                        if yue_money < 0:
                            ret["code"] = 1
                            ret["msg"] = "余额不足"
                            return ret
                    else:
                        yue_money = int(user_money) - int(money)
                        if yue_money < 0:
                            ret["code"] = 1
                            ret["msg"] = "余额不足"
                            return ret

                    xiazhu_ret = xiazhu(room_name, bac_num, username, xiazhu_type, money, yue_money)

                    if xiazhu_ret["code"] == 1:
                        ret["code"] = 1
                        ret["msg"] = "下注错误"
                        return ret
                    elif xiazhu_ret["code"] == 2:
                        ret["code"] = 2
                        ret["yue_money"] = r.get(user_key)
                        return ret
            ret["code"] = 0
            ret["yue_money"] = r.get(user_key)
            return ret
    except:
        ret["code"] = 1
        ret["msg"] = "下注错误"
        return ret


# 根据用户 和下注的金额来写入redis
# key的规则 room_几靴_几局_username   value ''
# {
#     'username':username,
#     'usermoney': usermoney,
#     'userbacc': {
#         'z': 0,
#         'x': 0,
#         'zd': 0,
#         'xd': 0,
#     }
# }
#
# key reuslt   room_几靴_几局_pre value '庄#闲####'


def xiazhu(room_id, baccarat_id, username, xiazhu_type, money, yue_money):
    # room_id 是房间号  baccarat_id 是第几靴第几局  username 下注用户
    #  wmoney 下注的庄还是闲   money 下注多少金额  ownmonney 下注完毕后剩余的钱
    ret = {}
    user_key = username + "_money"
    mykey = "xiazhu_" + room_id + '_' + baccarat_id + '_' + username
    if r.exists(mykey):
        try:
            mykeyvalue = r.get(mykey)
            mykeyvalu_json = json.loads(mykeyvalue)
            old_xiazhu_money = int(mykeyvalu_json["userbacc"][xiazhu_type])
            if xiazhu_type == 'sb':
                if old_xiazhu_money > 0:
                    yue_money = int(yue_money) + int(old_xiazhu_money) * 3
            else:
                if old_xiazhu_money > 0:
                    yue_money = int(yue_money) + int(old_xiazhu_money)
            if r.exists(user_key):
                r.set(user_key, yue_money)
            mykeyvalu_json["userbacc"][xiazhu_type] = money
            mykeyvalu_json["usermoney"] = yue_money
            mykeyvalustr = json.dumps(mykeyvalu_json, ensure_ascii=False)
            r.set(mykey, mykeyvalustr)
            r.expire(mykey, 86400)
            # show_bac(room_id, baccarat_id)
            if mykeyvalu_json["userbacc"]["x"] != "0" and mykeyvalu_json["userbacc"]["z"] != "0":
                ret["code"] = 2
            else:
                ret["code"] = 0
            return ret
        except:
            ret["code"] = 1
            return ret
    else:
        try:
            myvalue = {
                "username": username,
                "usermoney": yue_money,
                "userbacc": {
                    "z": 0,
                    "x": 0,
                    "zd": 0,
                    "xd": 0,
                    "h": 0,
                    "sb": 0,
                }
            }
            myvalue["userbacc"][xiazhu_type] = money
            myvaluestr = json.dumps(myvalue, ensure_ascii=False)
            r.set(mykey, myvaluestr)
            r.expire(mykey, 86400)
            if r.exists(user_key):
                r.set(user_key, yue_money)
            # show_bac(room_id, baccarat_id)
            ret["code"] = 0
            return ret
        except:
            ret["code"] = 1
            return ret


# 下注结束后的展示用户下注了多少
# keys showbac + room_name + bac_num
# { username:  用户
#  userbacc:  下注多少 z300，x300
#  usermoney:  下注后剩余多少钱
# }
# 127.0.0.1:6379> get showbac_room123_123xue12ju
# {'justinli': {'usermoney': 1000, 'userbacc': 'z300,zd100000,'}, 'lixiaoding': {'usermoney': 1000, 'userbacc': 'zd100000,'}}
def show_bac(room_name, baccarat_num):
    showbacc = {

    }
    ret = {}
    mykey = "showbac_" + room_name + "_" + baccarat_num
    if r.exists(mykey):
        r.delete(mykey)
        try:
            keystr = "xiazhu_" + room_name + "_" + baccarat_num + "*"
            keys = r.keys(keystr)
            showbacclist = []
            for key in keys:
                showbaccdic = {}
                myvalues = r.get(key)
                myvalues = json.loads(myvalues)
                showbacc_userbacc = ""
                # showbacc[myvalues["username"]] = {
                #     "usermoney": myvalues["usermoney"]
                # }
                showbaccdic["username"] = myvalues["username"]
                showbaccdic["usermoney"] = myvalues["usermoney"]
                for mvkey, mvval in myvalues["userbacc"].items():
                    if mvval != 0:
                        showbacc_userbacc += mvkey + str(mvval) + ","
                # showbacc[myvalues["username"]]["userbacc"] = showbacc_userbacc
                showbaccdic["userbacc"] = showbacc_userbacc
                showbacclist.append(showbaccdic)
            r.set(mykey, json.dumps(showbacclist, ensure_ascii=False))
            r.expire(mykey, 86400)
            strshowbacclist = r.get(mykey)
            ret["code"] = 0
            ret["msg"] = strshowbacclist

        except:
            ret["code"] = 1
            ret["msg"] = "showbacc 生成错误"
    else:
        try:
            keystr = "xiazhu_" + room_name + "_" + baccarat_num + "*"
            keys = r.keys(keystr)
            showbacclist = []
            for key in keys:
                showbaccdic = {}
                myvalues = r.get(key)
                myvalues = json.loads(myvalues)
                showbacc_userbacc = ""
                # showbacc[myvalues["username"]] = {
                #     "usermoney": myvalues["usermoney"]
                # }
                showbaccdic["username"] = myvalues["username"]
                showbaccdic["usermoney"] = myvalues["usermoney"]
                for mvkey, mvval in myvalues["userbacc"].items():
                    if mvval != 0:
                        showbacc_userbacc += mvkey + str(mvval) + ","
                # showbacc[myvalues["username"]]["userbacc"] = showbacc_userbacc
                showbaccdic["userbacc"] = showbacc_userbacc
                showbacclist.append(showbaccdic)

            r.set(mykey, json.dumps(showbacclist, ensure_ascii=False))
            r.expire(mykey, 86400)
            strshowbacclist = r.get(mykey)
            ret["code"] = 0
            ret["msg"] = strshowbacclist
        except:
            ret["code"] = 1
            ret["msg"] = "showbacc 生成错误"
    return ret


# key room_几靴_几局_result:  value: '庄'
# 结果出来后的结算
# 根据 结果 来算各个玩家的输赢情况，生成报表json数据，并写入数据库


def jiesuan(room_name, baccarat_num, results, change=None):
    betinfo = {
        "z": 1.95,
        "x": 2,
        "zd": 12,
        "xd": 12,
        "h": 9,
        "sb": 1,
    }
    change = change
    ret = {}
    jiesuanlist = []
    mykey = "jiesuan_" + room_name + '_' + baccarat_num
    if "sb" in results.split(','):
        new_reuslts = ['zd', 'xd', 'h']
    elif "sd" in results.split(','):
        new_reuslts = [results.split(',')[0], 'zd', 'xd']
    else:
        new_reuslts = results.split(',')

    if r.exists(mykey):
        r.delete(mykey)

    keystr = "showbac_" + room_name + "_" + baccarat_num

    if r.exists(keystr):
        mybets = r.get(keystr)
        mybet = ast.literal_eval(mybets)
        sb_total = 0
        com_sb_add_total = 0
        com_sb_reduce_total = 0
        sb_total_keys = room_name + "_sb_total" + time.strftime('%Y-%m-%d')
        com_sb_reduce_key = room_name + "_sb_reduce_total" + time.strftime('%Y-%m-%d')
        com_sb_add_key = room_name + "_sb_add_total" + time.strftime('%Y-%m-%d')
        for users in mybet:
            bet_add_total = 0
            bet_reduce_total = 0
            jiesuandict = {}
            betlist = users["userbacc"].split(',')
            zx_add_total = 0
            zx_reduce_total = 0
            sb_reduce_total = 0
            sb_add_total = 0

            user_reduce_total_keys = users["username"] + "_reduce_total" + time.strftime('%Y-%m-%d')
            user_add_total_keys = users["username"] + "_add_total" + time.strftime('%Y-%m-%d')
            usersb_reduce_total_keys = users["username"] + "_sb_reduce_total" + time.strftime('%Y-%m-%d')
            usersb_add_total_keys = users["username"] + "_sb_add_total" + time.strftime('%Y-%m-%d')

            results_dict = results.split(",")
            for betone in betlist:
                if len(betone) > 0:
                    (betwhich, betnumber) = bet_parse(betone)

                    if betwhich == "z" and betwhich not in results_dict and "h" not in results_dict:
                        zx_reduce_total = zx_reduce_total + int(betnumber)
                        zx_add_total = zx_add_total - int(betnumber)
                    elif betwhich == "z" and betwhich in results_dict:
                        zx_add_total = zx_add_total + int(int(betnumber) * 0.95)
                    elif betwhich == "x" and betwhich not in results_dict and "h" not in results_dict:
                        zx_reduce_total = zx_reduce_total + int(betnumber)
                        zx_add_total = zx_add_total - int(betnumber)
                    elif betwhich == "x" and betwhich in results_dict:
                        zx_add_total = zx_add_total + int(betnumber)
                    elif betwhich == "sb":
                        sb_total = sb_total + int(betnumber) * 3
                        if "sb" in results_dict:
                            sb_add_total = sb_add_total + int(betnumber) * 30
                        elif "h" in results_dict and "zd" in results_dict:
                            sb_add_total = sb_add_total + int(betnumber) * 19 - int(betnumber)
                            sb_reduce_total = int(betnumber)
                        elif "h" in results_dict and "xd" in results_dict:
                            sb_add_total = sb_add_total + int(betnumber) * 19 - int(betnumber)
                            sb_reduce_total = int(betnumber)
                        elif "zd" in results_dict:
                            sb_add_total = sb_add_total + int(betnumber) * 11 - int(betnumber) * 2
                            sb_reduce_total = int(betnumber) * 2
                        elif "xd" in results_dict:
                            sb_add_total = sb_add_total + int(betnumber) * 11 - int(betnumber) * 2
                            sb_reduce_total = int(betnumber) * 2
                        elif "h" in results_dict:
                            sb_add_total = sb_add_total + int(betnumber) * 8 - int(betnumber) * 2
                            sb_reduce_total = int(betnumber) * 2
                        elif "sd" in results_dict:
                            sb_add_total = sb_add_total + int(betnumber) * 22 - int(betnumber)
                            sb_reduce_total = int(betnumber)
                        else:
                            sb_reduce_total = int(betnumber) * 3
                            sb_add_total = sb_add_total - int(betnumber) * 3
                        com_sb_add_total = com_sb_add_total + sb_reduce_total
                        com_sb_reduce_total =com_sb_reduce_total - sb_add_total

                    # for result in new_reuslts:
                    #     if betwhich == result:
                    #         bet_add_total = int(betnumber) * int(betinfo[result]) + int(betnumber) + bet_add_total
                    #     else:
                    #         bet_reduce_total = int(betnumber) + bet_reduce_total
                    if betwhich != "sb" and betwhich in new_reuslts:
                        bet_add_total = int(int(betnumber) * betinfo[betwhich]) + bet_add_total
                    elif betwhich != "sb" and betwhich not in new_reuslts:
                        if betwhich == "z" and "h" in results_dict:
                            bet_add_total = bet_add_total + int(betnumber)
                        elif betwhich == "x" and "h" in results_dict:
                            bet_add_total = bet_add_total + int(betnumber)
                        else:
                            bet_reduce_total = int(betnumber) + bet_reduce_total

                    if betwhich == 'sb':
                        for sb_betwhich in ['zd', 'xd', 'h']:
                            # for result in new_reuslts:
                            #     if sb_betwhich == result:
                            #         bet_add_total = int(betnumber) * int(betinfo[result]) + int(betnumber) + bet_add_total
                            #     else:
                            #         bet_reduce_total = int(betnumber) + bet_reduce_total
                            if sb_betwhich in new_reuslts:
                                bet_add_total = int(betnumber) * int(betinfo[sb_betwhich]) + bet_add_total
                            else:
                                bet_reduce_total = int(betnumber) + bet_reduce_total
                else:
                    continue
            jiesuandict["username"] = users["username"]
            jiesuandict["bet_add"] = bet_add_total
            jiesuandict["bet_reduce"] = bet_reduce_total
            jiesuandict["result"] = results
            jiesuandict["usermoney"] = bet_add_total + int(users["usermoney"])
            jiesuanlist.append(jiesuandict)

            if r.exists(usersb_reduce_total_keys):
                usersb_reduce = r.get(usersb_reduce_total_keys)
                r.set(usersb_reduce_total_keys, int(usersb_reduce) + sb_reduce_total)
                r.expire(usersb_reduce_total_keys, 172800)
            else:
                r.set(usersb_reduce_total_keys, sb_reduce_total)
                r.expire(usersb_reduce_total_keys, 172800)

            if r.exists(usersb_add_total_keys):
                usersb_add = r.get(usersb_add_total_keys)
                r.set(usersb_add_total_keys, int(usersb_add) + sb_add_total)
                r.expire(usersb_add_total_keys, 172800)
            else:
                r.set(usersb_add_total_keys, sb_add_total)
                r.expire(usersb_add_total_keys, 172800)

            if r.exists(user_reduce_total_keys):
                reduce_total = int(r.get(user_reduce_total_keys)) + zx_reduce_total
                r.set(user_reduce_total_keys, reduce_total)
                r.expire(user_reduce_total_keys, 172800)
            else:
                r.set(user_reduce_total_keys, zx_reduce_total)
                r.expire(user_reduce_total_keys, 172800)

            if r.exists(user_add_total_keys):
                add_total = int(r.get(user_add_total_keys)) + zx_add_total
                r.set(user_add_total_keys, add_total)
                r.expire(user_add_total_keys, 172800)
            else:
                r.set(user_add_total_keys, zx_add_total)
                r.expire(user_add_total_keys, 172800)

            money_key = users["username"] + "_money"
            if change is not None:
                if r.exists(money_key):
                    change_money = int(r.get(money_key)) + bet_add_total
                    r.set(money_key, change_money)
                    async_db(users["username"], change_money)
                else:
                    ret["code"] = 1
                    ret["msg"] = users["username"] + "该用户没有money_key,疑似非法用户"
                    return ret
                userOperatorLog(users["username"], baccarat_num, users["userbacc"], users["usermoney"], results,
                                change_money)
            else:
                if r.exists(money_key):
                    r.set(money_key, jiesuandict["usermoney"])
                    async_db(users["username"], jiesuandict["usermoney"])
                else:
                    ret["code"] = 1
                    ret["msg"] = users["username"] + "该用户没有money_key,疑似非法用户"
                    return ret
                userOperatorLog(users["username"], baccarat_num, users["userbacc"], users["usermoney"], results,
                            jiesuandict["usermoney"])

        if r.exists(sb_total_keys):
            sbtotal = r.get(sb_total_keys)
            r.set(sb_total_keys, int(sbtotal) + sb_total)
            r.expire(sb_total_keys, 172800)
        else:
            r.set(sb_total_keys, sb_total)
            r.expire(sb_total_keys, 172800)

        if r.exists(com_sb_reduce_key):
            comsbreduce = r.get(com_sb_reduce_key)
            r.set(com_sb_reduce_key, int(comsbreduce) + com_sb_reduce_total)
            r.expire(com_sb_reduce_key, 172800)
        else:
            r.set(com_sb_reduce_key, com_sb_reduce_total)
            r.expire(com_sb_reduce_key, 172800)

        if r.exists(com_sb_add_key):
            comsbadd = r.get(com_sb_add_key)
            r.set(com_sb_add_key, int(comsbadd) + com_sb_add_total)
            r.expire(com_sb_add_key, 172800)
        else:
            r.set(com_sb_add_key, com_sb_add_total)
            r.expire(com_sb_add_key, 172800)
        r.set(mykey, json.dumps(jiesuanlist, ensure_ascii=False))
        r.expire(mykey, 86400)
        strjiesuanlist = r.get(mykey)
        ret["code"] = 0
        ret["msg"] = strjiesuanlist
        return ret
    else:
        ret["code"] = 1
        ret["msg"] = "jiesuan error!"
        logger.info(ret["msg"])
        print(ret["msg"])
        return ret


# 对类似 x1000 这样的下注格式进行解析, 返回  x  1000 这样的格式
def bet_parse(bet):
    betnum = len(bet)
    if bet[0:2].isalpha():
        return bet[0:2], bet[2:]
    else:
        return bet[0], bet[1:]


# 解析 下注字符串是否符合规则 x100z100sb100  不符合返回1 符合返回0
def bacc_parse(content):
    if content.isalnum():
        zwmatch = zhmodel.search(content)
        if zwmatch:
            return 1
        else:
            if content[0:2].lower() not in allow_list and content[0].lower() not in allow_list:
                return 1
            reslist = re.findall(zfmatch, content.lower())
            if len(reslist) > 0:
                for ivalue in reslist:
                    if len(ivalue) > 2 or ivalue.lower() not in allow_list:
                        return 1
                    else:
                        continue
            else:
                return 1
        return 0
    else:
        return 1