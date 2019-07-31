#!/usr/bin/env python
#-*- coding: UTF-8 -*-

"""
@version: Python2.7.10
@author:  Justinli

"""
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from myauth.models import MyAgent, UserOperator, MyBi, Rooms
from django.contrib.auth import get_user_model
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage, InvalidPage
from chat.utils.tool import getredis, betparse, getRoadFromRedis, change_jiesuan_admin
from .utils.tools import addChargeHistory
from chat.utils.baccarat import jiesuan
import time
import hashlib
from django.contrib.auth.hashers import make_password
import pickle
import json
from .utils.tools import getuserbifromdb, getcombifromdb, getuserbifromredis, getcombifromredis
import ast

r = getredis()

MyUsers = get_user_model()


def index(request):
    return render(request, 'index.html', {})


@login_required
def agentlist(request):
    username = request.user.username
    if request.user.is_admin:
        request.session["is_admin"] = request.user.is_admin
    else:
        request.session["is_admin"] = False


    agent_res = MyAgent.objects.filter(username=username)
    userlist = []
    if len(agent_res) > 0:
        agent_id = agent_res[0].agent_id
        user_res = MyUsers.objects.filter(agent_id=agent_id)
        if len(user_res) > 0:
            for i in user_res:
                bi_res = MyBi.objects.filter(user_id=i)
                if len(bi_res) > 0:
                    userlist.append(bi_res[0])
            paginator = Paginator(userlist, 15)
            if request.method == "GET":
                page = request.GET.get('page')
                try:
                    userlist = paginator.page(page)
                except PageNotAnInteger:
                    userlist = paginator.page(1)
                except InvalidPage:
                    userlist = paginator.page(1)
                except EmptyPage:
                     userlist = paginator.page(paginator.num_pages)
            return render(request, 'agent.html', {'userlist': userlist, "is_staff": request.session.get("is_admin", None)})
        else:
            return render(request, 'agent.html', {'userlist': userlist, "is_staff": request.session.get("is_admin", None)})
    else:
        return HttpResponse("你无权登录!")


@login_required
def oplists(request):
    username = request.GET.get('username')
    oplist = []
    if username is not None and username != "":
        request.session['opusername'] = username
    elif request.session.get('opusername', None) is not None:
        username = request.session.get('opusername')
    else:
        return render(request, 'agent_operator.html', {'oplist': oplist, "is_staff": request.session.get("is_admin", None)})
    op_res = UserOperator.objects.filter(username=username)
    if len(op_res) > 0:
        # for op in op_res:
        #     oplist.append(op)
        paginator = Paginator(op_res, 15)
        if request.method == "GET":
            page = request.GET.get('page')
            try:
                oplist = paginator.page(page)
            except PageNotAnInteger:
                oplist = paginator.page(1)
            except InvalidPage:
                oplist = paginator.page(1)
            except EmptyPage:
                 oplist = paginator.page(paginator.num_pages)
    return render(request, 'agent_operator.html', {'oplist': oplist, "is_staff": request.session.get("is_admin", None)})



@login_required
def searchuser(request):
    user = request.GET.get("username")
    username = request.user.username
    userlist = []
    if request.user.is_admin:
        user_obj = MyUsers.objects.filter(username=user)
        if len(user_obj) > 0:
            root_user_res = MyBi.objects.filter(user_id=user_obj[0])
            if len(root_user_res) > 0:
                return render(request, 'agent.html', {'userlist': root_user_res, "is_staff": request.session.get("is_admin", None)})
        else:
            return render(request,'error.html',{'errorMessage':"你查找的用户不存在"})
    agent_res = MyAgent.objects.filter(username=username)
    if len(agent_res) > 0 and user is not None and user != "":
        agent_id = agent_res[0].agent_id
        user_res = MyUsers.objects.filter(username=user)
        if len(user_res) > 0 and user_res[0].agent_id == agent_id:
            bi_res = MyBi.objects.filter(user_id=user_res[0])
            userlist.append(bi_res[0])
            return render(request, 'agent.html', {'userlist': userlist, "is_staff": request.session.get("is_admin", None)})
        else:
            return render(request, 'agent.html', {'userlist': userlist, "is_staff": request.session.get("is_admin", None)})
    else:
        return render(request, 'agent.html', {'userlist': userlist, "is_staff": request.session.get("is_admin", None)})



@login_required
def charge(request):
    is_admin = request.user.is_admin
    user = request.user
    username = request.GET.get("username")
    print(is_admin)
    bilist = []
    if is_admin:
        if username is not None and username != "":
            user_1 = MyUsers.objects.filter(username=username)
            if len(user_1) > 0:
                userbi = MyBi.objects.filter(user_id=user_1[0])
                return render(request, "charge.html", {"bilist": userbi, "is_staff": request.session.get("is_admin", None)})
            else:
                return render(request,'error.html',{'errorMessage': "用户名错误"})
        elif username == "":
            return render(request,'error.html',{'errorMessage': "用户名错误"})
        else:
            all_bi = MyBi.objects.all()
            print(all_bi)
            paginator = Paginator(all_bi, 15)
            if request.method == "GET":
                page = request.GET.get('page')
                try:
                    bilist = paginator.page(page)
                except PageNotAnInteger:
                    bilist = paginator.page(1)
                except InvalidPage:
                    bilist = paginator.page(1)
                except EmptyPage:
                     bilist = paginator.page(paginator.num_pages)
            return render(request, "charge.html", {"bilist": bilist, "is_staff": request.session.get("is_admin", None)})
    else:
        return HttpResponse("你无权访问")


@login_required
def addcharge(request):
    is_admin = request.user.is_admin
    username = request.GET.get("username")
    money = request.GET.get("money")
    money_key = username + "_money"
    if is_admin:
        if username is not None and username != "" and money is not None and money != "":
            user = MyUsers.objects.filter(username=username)
            if len(user) > 0:
                try:
                    mybi = MyBi.objects.filter(user_id=user[0])
                    if len(mybi) > 0:
                        if r.exists(money_key):
                            rmoney = r.get(money_key)
                            rmoney = int(rmoney) + int(money)
                            r.set(money_key, rmoney)
                            mybi[0].cur_m = rmoney
                        else:
                            rmoney = int(mybi[0].cur_m) + int(money)
                            r.set(money_key, rmoney)
                            mybi[0].cur_m = rmoney

                        mybi[0].total_m = str(int(mybi[0].total_m) + int(money))
                        mybi[0].recharge_lasttime = time.strftime("%Y-%m-%d")
                        mybi[0].save()
                        loggerMessage = user[0].username + "  [充值]: " + money + ", [现在剩余金额]: " + money
                        opusername = request.user.username
                        addChargeHistory(opusername, username, "充值", loggerMessage)
                    else:
                        newbi = MyBi(user_id=user[0], total_m=money, cur_m=money, get_m=0, recharge_lasttime=time.strftime("%Y-%m-%d"), withdraw_lastime=time.strftime("%Y-%m-%d"))
                        newbi.save()
                        loggerMessage = username + "  [充值]: " + str(money) + ", [现在剩余金额]: " + str(money)
                        opusername = request.user.username
                        addChargeHistory(opusername, username, "充值", loggerMessage)
                        if r.exists(money_key):
                            rmoney = r.get(money_key)
                            rmoney = int(rmoney) + int(money)
                            r.set(money_key, rmoney)

                        else:
                            r.set(money_key, money)
                    url = "/getuser/?username=" + username
                    return redirect(url)
                except:
                    return render(request,'error.html',{'errorMessage': "充值错误,请重新尝试", "is_staff": request.session.get("is_admin", None)})
            else:
                return render(request,'error.html',{'errorMessage': "要充值的用户不正确", "is_staff": request.session.get("is_admin", None)})
        else:
            return render(request,'error.html',{'errorMessage': "要充值的参数不正确", "is_staff": request.session.get("is_admin", None)})
    else:
        return HttpResponse("你无权充值")


@login_required
def getuser(request):
    is_admin = request.user.is_admin
    username = request.GET.get("username")
    if is_admin:
        if username is not None and username != "":
            users = MyUsers.objects.filter(username=username)
            if len(users) > 0:
                return render(request, "user.html", {"userlist":users, "is_staff": request.session.get("is_admin", None)})
            else:
                return render(request,'error.html',{'errorMessage': "用户名错误", "is_staff": request.session.get("is_admin", None)})
        elif username == "":
            return render(request,'error.html',{'errorMessage': "用户名错误", "is_staff": request.session.get("is_admin", None)})
        else:
            users = MyUsers.objects.all()
            paginator = Paginator(users, 15)
            if request.method == "GET":
                page = request.GET.get('page')
                try:
                    userlist = paginator.page(page)
                except PageNotAnInteger:
                    userlist = paginator.page(1)
                except InvalidPage:
                    userlist = paginator.page(1)
                except EmptyPage:
                     userlist = paginator.page(paginator.num_pages)
            return render(request, "user.html", {"userlist":userlist, "is_staff": request.session.get("is_admin", None)})
    else:
        return HttpResponse("你无权查看")


@login_required
def getqcorde(request):
    is_admin = request.user.is_admin
    username = request.user.username
    if is_admin:
        return render(request, "qcorde.html", {"username":username, "is_staff": request.session.get("is_admin", None)})
    else:
        return render(request, "qcorde.html", {"username":username})


@login_required
def xiafen(request):
    is_admin = request.user.is_admin
    user = request.user
    username = request.GET.get("username")
    bilist = []
    if is_admin:
        if username is not None and username != "":
            user_1 = MyUsers.objects.filter(username=username)
            if len(user_1) > 0:
                userbi = MyBi.objects.filter(user_id=user_1[0])
                return render(request, "xiafen.html", {"bilist": userbi, "is_staff": request.session.get("is_admin", None)})
            else:
                return render(request,'error.html',{'errorMessage': "用户名错误", "is_staff": request.session.get("is_admin", None)})
        elif username == "":
            return render(request,'error.html',{'errorMessage': "用户名错误", "is_staff": request.session.get("is_admin", None)})
        else:
            all_bi = MyBi.objects.all()
            paginator = Paginator(all_bi, 15)
            if request.method == "GET":
                page = request.GET.get('page')
                try:
                    bilist = paginator.page(page)
                except PageNotAnInteger:
                    bilist = paginator.page(1)
                except InvalidPage:
                    bilist = paginator.page(1)
                except EmptyPage:
                     bilist = paginator.page(paginator.num_pages)
            return render(request, "xiafen.html", {"bilist": bilist, "is_staff": request.session.get("is_admin", None)})
    else:
        return HttpResponse("你无权访问")


@login_required
def reducecharge(request):
    is_admin = request.user.is_admin
    username = request.GET.get("username")
    money = request.GET.get("money")
    money_key = username + "_money"
    if is_admin:
        if username is not None and username != "" and money is not None and money != "":
            user = MyUsers.objects.filter(username=username)
            if len(user) > 0:
                try:
                    mybi = MyBi.objects.filter(user_id=user[0])
                    if len(mybi) > 0:
                        rmoney = 0
                        if r.exists(money_key):
                            rmoney = r.get(money_key)
                        if int(money) > int(rmoney):
                            return render(request,'error.html',{'errorMessage': "你的余额不足,请重新更改提取余额", "is_staff": request.session.get("is_admin", None)})

                        mybi[0].cur_m = int(rmoney) - int(money)
                        mybi[0].get_m = int(mybi[0].get_m) + int(money)
                        mybi[0].withdraw_lastime = time.strftime("%Y-%m-%d")
                        mybi[0].save()
                        now_money = int(rmoney) - int(money)
                        r.set(money_key, now_money)
                        loggerMessage = username + "  [提现]: " + str(money) + ", [现在剩余金额]: " + str(now_money)
                        opusername = request.user.username
                        addChargeHistory(opusername, username, "提现", loggerMessage)
                except:
                    return render(request,'error.html',{'errorMessage': "下分错误,请重新尝试", "is_staff": request.session.get("is_admin", None)})
                url = "/xiafen/?username=" + username
                return redirect(url)
            else:
                return render(request,'error.html',{'errorMessage': "要下分的用户不正确", "is_staff": request.session.get("is_admin", None)})
        else:
            return render(request,'error.html',{'errorMessage': "下分的参数不对", "is_staff": request.session.get("is_admin", None)})
    else:
        return HttpResponse("你无权下分")


@login_required
def robot(request):
    is_admin = request.user.is_admin
    username = request.GET.get("username")
    if is_admin:
        if username is not None and username != "":
            users = MyUsers.objects.filter(username=username)
            if len(users) > 0:
                return render(request, "robot.html",
                              {"userlist": users, "is_staff": request.session.get("is_admin", None)})
            else:
                return render(request, 'error.html',
                              {'errorMessage': "用户名错误", "is_staff": request.session.get("is_admin", None)})
        elif username == "":
            return render(request, 'error.html',
                          {'errorMessage': "用户名错误", "is_staff": request.session.get("is_admin", None)})
        else:
            users = MyUsers.objects.filter(is_robot=True)
            paginator = Paginator(users, 15)
            if request.method == "GET":
                page = request.GET.get('page')
                try:
                    userlist = paginator.page(page)
                except PageNotAnInteger:
                    userlist = paginator.page(1)
                except InvalidPage:
                    userlist = paginator.page(1)
                except EmptyPage:
                    userlist = paginator.page(paginator.num_pages)
            return render(request, "robot.html", {"userlist": userlist, "is_staff": request.session.get("is_admin", None)})
    else:
        return HttpResponse("你无权查看")


@login_required
def addrobot(request):
    is_admin = request.user.is_admin
    username = request.GET.get("username")
    nickname = request.GET.get("nickname")

    if is_admin:
        if username is not None and nickname is not None:
            if username != "" and nickname != "":
                try:
                    authuser = MyUsers.objects.filter(username=username)
                    if len(authuser) > 0:
                        return render(request, 'error.html', {'errorMessage': "用户已经存在",
                                                              "is_staff": request.session.get("is_admin", None)})
                    authnick = MyUsers.objects.filter(nickname=nickname)
                    if len(authnick) > 0:
                        return render(request, 'error.html', {'errorMessage': "昵称已经存在",
                                                              "is_staff": request.session.get("is_admin", None)})
                    md5str = username + str(time.time())
                    md5str = md5str.encode('utf-8')
                    hmd5 = hashlib.md5()
                    hmd5.update(md5str)
                    user_id_md5 = hmd5.hexdigest()

                    user = MyUsers(username=username, nickname=nickname, password=make_password("112233.com"),
                                   user_id=user_id_md5,
                                   agent_id="admin", is_robot=True)
                    user.save()
                except:
                    return render(request, 'error.html',
                                  {'errorMessage': "创建机器人用户失败", "is_staff": request.session.get("is_admin", None)})
                try:
                    myuser = MyUsers.objects.filter(username=username)
                    if len(myuser) > 0:
                        mybi = MyBi(user_id=myuser[0], total_m=200000, cur_m=200000, get_m=0, recharge_lasttime=time.strftime("%Y-%m-%d"), withdraw_lastime=time.strftime("%Y-%m-%d"))
                        mybi.save()
                        url = "/robot/?username=" + username
                        return redirect(url)
                    else:
                        return render(request, 'error.html',
                                      {'errorMessage': "创建机器人用户失败", "is_staff": request.session.get("is_admin", None)})
                except:
                    return render(request, 'error.html',
                                  {'errorMessage': "给机器人充值失败", "is_staff": request.session.get("is_admin", None)})
            else:
                return render(request,'error.html',{'errorMessage': "传递参数错误，不能为空", "is_staff": request.session.get("is_admin", None)})
        else:
            return render(request,'error.html',{'errorMessage': "传递参数错误，不能为空", "is_staff": request.session.get("is_admin", None)})

    else:
        return HttpResponse("你无权操作")

@login_required
def robotset(request):
    robot_key = "robot_room"
    is_admin = request.user.is_admin
    roomlist = Rooms.objects.all()
    query = request.GET.get('query')

    if is_admin:
        robotuser_list = []
        myrobotuser = MyUsers.objects.filter(is_robot=True)
        if len(myrobotuser) > 0:
            for i in range(0, len(myrobotuser)):
                robotuser_dict = {
                    "username": myrobotuser[i].username,
                    "nickname": myrobotuser[i].nickname,
                }
                robotuser_list.append(robotuser_dict)
            r.set("robotuser_list", pickle.dumps(robotuser_list))
        else:
            r.set("robotuser_list", "")

        if r.exists(robot_key):
            robot_str = r.get(robot_key)
        else:
            robot_str = ",".join(['3' for i in range(0, len(roomlist))])
            r.set(robot_key, robot_str)
        robot_str_list = robot_str.split(",")
        if query is not None and query != "":
            room_action = query.split("_")[0]
            room_id = query.split('_')[-1]
            room_index = query.split('_')[-1][-1]
            room_index_int = int(room_index)
            if room_action == "start":
                if robot_str_list[room_index_int - 1] != "0":
                    robot_str_list[room_index_int - 1] = "0"
                    r.set(robot_key, ",".join(robot_str_list))
            elif room_action == "stop":
                if robot_str_list[room_index_int - 1] != "1":
                    robot_str_list[room_index_int - 1] = "1"
                    r.set(robot_key, ",".join(robot_str_list))
            str_1 = ""
            for i in range(0,len(robot_str_list)):
                if robot_str_list[i] == "0":
                    sub_str = "准备开始"
                elif robot_str_list[i] == "1":
                    sub_str = "准备停止"
                elif robot_str_list[i] == "2":
                    sub_str = "机器人投注中"
                elif robot_str_list[i] == "3":
                    sub_str = "暂停投注中"
                str_1 = str_1 + "房间" + str(i + 1) + ":" + sub_str + "#"
            return render(request, 'robotset.html', {'roomlist': roomlist, "roomstate":str_1,  "is_staff": request.session.get("is_admin", None)})
        elif query == "":
            return render(request, 'error.html',
                          {'errorMessage': "传递参数错误，不能为空", "is_staff": request.session.get("is_admin", None)})
        else:
            str_2 = ""
            for i in range(0,len(robot_str_list)):
                if robot_str_list[i] == "0":
                    sub_str = "准备开始"
                elif robot_str_list[i] == "1":
                    sub_str = "准备停止"
                elif robot_str_list[i] == "2":
                    sub_str = "机器人投注中"
                elif robot_str_list[i] == "3":
                    sub_str = "暂停投注中"
                str_2 = str_2 + "房间" + str(i + 1) + ":" + sub_str + "#"
            return render(request, 'robotset.html', {'roomlist': roomlist, "roomstate":str_2, "is_staff": request.session.get("is_admin", None)})
    else:
        return HttpResponse("你无权操作")



@login_required
def ubi(request):
    is_admin = request.user.is_admin
    date_time = request.GET.get("date_time")

    if is_admin:
        if date_time is not None and date_time != "":
            ubi = getuserbifromdb(date_time)
        else:
            ubi = getuserbifromdb()
        print(ubi)
        if ubi is not None:
            paginator = Paginator(ubi, 30)
            if request.method == "GET":
                page = request.GET.get('page')
                try:
                    userbilist = paginator.page(page)
                except PageNotAnInteger:
                    userbilist = paginator.page(1)
                except InvalidPage:
                    userbilist = paginator.page(1)
                except EmptyPage:
                    userbilist = paginator.page(paginator.num_pages)
            return render(request, "ubi.html", {"userbilist":userbilist, "is_staff": request.session.get("is_admin", None)})
        else:
            print("what is None")
            return render(request, "ubi.html", {"userbilist": None, "is_staff": request.session.get("is_admin", None)})
    else:
        return HttpResponse("你无权操作")


@login_required
def cbi(request):
    is_admin = request.user.is_admin
    date_time = request.GET.get("date_time")

    if is_admin:
        if date_time is not None and date_time != "":
            cbi = getcombifromdb(date_time)
        else:
            cbi = getcombifromdb()
        if cbi is not None:
            paginator = Paginator(cbi, 30)
            if request.method == "GET":
                page = request.GET.get('page')
                try:
                    combilist = paginator.page(page)
                except PageNotAnInteger:
                    combilist = paginator.page(1)
                except InvalidPage:
                    combilist = paginator.page(1)
                except EmptyPage:
                    combilist = paginator.page(paginator.num_pages)
            return render(request, "cbi.html", {"combilist":combilist, "is_staff": request.session.get("is_admin", None)})
            # return HttpResponse(len(cbi))
        else:
            return render(request, "cbi.html", {"combilist": None, "is_staff": request.session.get("is_admin", None)})
            # return HttpResponse("cbi is None")
    else:
        return HttpResponse("你无权操作")


# def cbi(request):
#     import json
#     res = getcombifromredis()
#     return HttpResponse(json.dumps(res))


@login_required
def mysetting(request):
    is_admin = request.user.is_admin
    zxmin = request.GET.get("zxmin")
    zxmax = request.GET.get("zxmax")
    dmin = request.GET.get("dmin")
    dmax = request.GET.get("dmax")
    hmin = request.GET.get("hmin")
    hmax = request.GET.get("hmax")
    sbmin = request.GET.get("sbmin")
    sbmax = request.GET.get("sbmax")
    tuiset = request.GET.get("tuiset")
    tui_total_set_key = "com_tui_total_setting"
    user_zx_min_key = "user_zx_min_setting"
    user_zx_max_key = "user_zx_max_setting"
    user_d_max_key = "user_d_max_setting"
    user_d_min_key = "user_d_min_setting"
    user_h_min_key = "user_h_min_setting"
    user_h_max_key = "user_h_max_setting"
    user_sb_max_key = "user_sb_max_setting"
    user_sb_min_key = "user_sb_min_setting"

    tui_total_set = 5000
    user_zx_max = 1000000
    user_zx_min = 100
    user_d_min = 100
    user_d_max = 10000
    user_h_min = 100
    user_h_max = 10000
    user_sb_min = 100
    user_sb_max = 10000

    if is_admin:
        if zxmin is not None and zxmin.isdigit():
            r.set(user_zx_min_key, zxmin)
        else:
            r.set(user_zx_min_key, user_zx_min)
        if zxmax is not None and zxmax.isdigit():
            r.set(user_zx_max_key, zxmax)
        else:
            r.set(user_zx_max_key, user_zx_max)
        if dmin is not None and dmin.isdigit():
            r.set(user_d_min_key, dmin)
        else:
            r.set(user_d_min_key, user_d_min)
        if dmax is not None and dmax.isdigit():
            r.set(user_d_max_key, dmax)
        else:
            r.set(user_d_max_key, user_d_max)
        if hmin is not None and hmin.isdigit():
            r.set(user_h_min_key, hmin)
        else:
            r.set(user_h_min_key, user_h_min)
        if hmax is not None and hmax.isdigit():
            r.set(user_h_max_key, hmax)
        else:
            r.set(user_h_max_key, user_h_max)
        if sbmin is not None and sbmin.isdigit():
            r.set(user_sb_min_key, sbmin)
        else:
            r.set(user_sb_min_key, user_sb_min)
        if sbmax is not None and sbmax.isdigit():
            r.set(user_sb_max_key, sbmax)
        else:
            r.set(user_sb_max_key, user_sb_max)

        if tuiset is not None and tuiset.isdigit():
            r.set(tui_total_set_key, tuiset)
        else:
            r.set(tui_total_set_key, tui_total_set)

        if r.exists(tui_total_set_key):
            tui_total_set = r.get(tui_total_set_key)
        if r.exists(user_zx_max_key):
            user_zx_max = r.get(user_zx_max_key)
        if r.exists(user_zx_min_key):
            user_zx_min = r.get(user_zx_min_key)

        return render(request, "mysetting.html", {"tui_total_set":tui_total_set, "user_zx_max":user_zx_max,
                                                  "user_h_max": user_h_max, "user_h_min": user_h_min,
                                                  "user_d_max": user_d_max, "user_d_min": user_d_min,
                                                  "user_sb_max": user_sb_max, "user_sb_min": user_sb_min,
                                                  "user_zx_min":user_zx_min, "is_staff": request.session.get("is_admin", None)})



def bacchange(request):
    #is_admin = request.user.is_admin
    # z_result = request.GET.get("z_result")
    # x_result = request.GET.get("x_result")
    r_result = request.GET.get("r_result")
    room_id = request.GET.get("room_id")
    bac_num = request.GET.get("bac_num")

    if True:
        if r_result is not None and room_id is not None and bac_num is not None:
            showbackey = "showbac_" + room_id + "_" + bac_num
            jiesuankey = "jiesuan_" + room_id + "_" + bac_num
            jiesuankeybak = jiesuankey + "_bak" + time.strftime("%Y%m%d")
            oldresult = ""
            if r.exists(jiesuankey):
                jiesuanlist = ast.literal_eval(r.get(jiesuankey))
            else:
                return HttpResponse(1)
            if r.exists(showbackey):
                showbaclist = ast.literal_eval(r.get(showbackey))
            else:
                return HttpResponse(1)
            for jiesuan_user in jiesuanlist:
                username = jiesuan_user["username"]
                bet_add = jiesuan_user["bet_add"]
                bet_reduce = jiesuan_user["bet_reduce"]
                oldresult = jiesuan_user["result"].split(",")
                money_key = username + "_money"
                change_xiazhu_key = "xiazhu_" + room_id + '_' + bac_num + '_' + username
                change_money = 0
                if r.exists(change_xiazhu_key):
                    pre_xiazhu = ast.literal_eval(r.get(change_xiazhu_key))
                    pre_xiazhu_which = pre_xiazhu['userbacc']
                    for i in oldresult:
                        change_money = change_money + int(pre_xiazhu_which[i])

                if r.exists(money_key):
                    redis_money = int(r.get(money_key))
                    add_money = redis_money - int(bet_add) + int(bet_reduce)
                    r.set(money_key, add_money)
                else:
                    return HttpResponse(1)
            # com_sb_add_total = 0
            # com_sb_reduce_total = 0
            # sb_total = 0
            # sb_total_keys = room_id + "_sb_total" + time.strftime('%Y-%m-%d')
            # com_sb_reduce_key = room_id + "_sb_reduce_total" + time.strftime('%Y-%m-%d')
            # com_sb_add_key = room_id + "_sb_add_total" + time.strftime('%Y-%m-%d')
            results_dict = oldresult.split(',')

            sb_total = 0
            com_sb_add_total = 0
            com_sb_reduce_total = 0
            sb_total_keys = room_id + "_sb_total" + time.strftime('%Y-%m-%d')
            com_sb_reduce_key = room_id + "_sb_reduce_total" + time.strftime('%Y-%m-%d')
            com_sb_add_key = room_id + "_sb_add_total" + time.strftime('%Y-%m-%d')
            for showbac_user in showbaclist:
                bet_add_total = 0
                bet_reduce_total = 0
                betlist = showbac_user["userbacc"].split(',')
                zx_add_total = 0
                zx_reduce_total = 0
                sb_reduce_total = 0
                sb_add_total = 0

                user_reduce_total_keys = showbac_user["username"] + "_reduce_total" + time.strftime('%Y-%m-%d')
                user_add_total_keys = showbac_user["username"] + "_add_total" + time.strftime('%Y-%m-%d')
                usersb_reduce_total_keys = showbac_user["username"] + "_sb_reduce_total" + time.strftime('%Y-%m-%d')
                usersb_add_total_keys = showbac_user["username"] + "_sb_add_total" + time.strftime('%Y-%m-%d')

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
                            elif "h" in results_dict and "xd" in results_dict:
                                sb_add_total = sb_add_total + int(betnumber) * 19 - int(betnumber)
                            elif "zd" in results_dict:
                                sb_add_total = sb_add_total + int(betnumber) * 11 - int(betnumber) * 2
                            elif "xd" in results_dict:
                                sb_add_total = sb_add_total + int(betnumber) * 11 - int(betnumber) * 2
                            elif "h" in results_dict:
                                sb_add_total = sb_add_total + int(betnumber) * 8 - int(betnumber) * 2
                            elif "sd" in results_dict:
                                sb_add_total = sb_add_total + int(betnumber) * 22 - int(betnumber)
                            else:
                                sb_reduce_total = int(betnumber) * 3
                                sb_add_total = sb_add_total - int(betnumber) * 3
                            com_sb_add_total = com_sb_add_total - sb_reduce_total
                            com_sb_reduce_total = com_sb_reduce_total + sb_add_total
                    else:
                        continue
                if r.exists(usersb_reduce_total_keys):
                    usersb_reduce = r.get(usersb_reduce_total_keys)
                    r.set(usersb_reduce_total_keys, int(usersb_reduce) - sb_reduce_total)
                    r.expire(usersb_reduce_total_keys, 172800)

                if r.exists(usersb_add_total_keys):
                    usersb_add = r.get(usersb_add_total_keys)
                    r.set(usersb_add_total_keys, int(usersb_add) - sb_add_total)
                    r.expire(usersb_add_total_keys, 172800)

                if r.exists(user_reduce_total_keys):
                    reduce_total = int(r.get(user_reduce_total_keys)) - zx_reduce_total
                    r.set(user_reduce_total_keys, reduce_total)
                    r.expire(user_reduce_total_keys, 172800)

                if r.exists(user_add_total_keys):
                    add_total = int(r.get(user_add_total_keys)) - zx_add_total
                    r.set(user_add_total_keys, add_total)
                    r.expire(user_add_total_keys, 172800)

            if r.exists(sb_total_keys):
                sbtotal = r.get(sb_total_keys)
                r.set(sb_total_keys, int(sbtotal) - sb_total)
                r.expire(sb_total_keys, 172800)

            if r.exists(com_sb_reduce_key):
                comsbreduce = r.get(com_sb_reduce_key)
                r.set(com_sb_reduce_key, int(comsbreduce) - com_sb_reduce_total)
                r.expire(com_sb_reduce_key, 172800)

            if r.exists(com_sb_add_key):
                comsbadd = r.get(com_sb_add_key)
                r.set(com_sb_add_key, int(comsbadd) - com_sb_add_total)
                r.expire(com_sb_add_key, 172800)
            # for showbac_user in showbaclist:
            #     zx_add_total = 0
            #     zx_reduce_total = 0
            #     sb_reduce_total = 0
            #     sb_add_total = 0
            #     user_reduce_total_keys = showbac_user["username"] + "_reduce_total" + time.strftime('%Y-%m-%d')
            #     user_add_total_keys = showbac_user["username"] + "_add_total" + time.strftime('%Y-%m-%d')
            #     usersb_reduce_total_keys = showbac_user["username"] + "_sb_reduce_total" + time.strftime('%Y-%m-%d')
            #     usersb_add_total_keys = showbac_user["username"] + "_sb_add_total" + time.strftime('%Y-%m-%d')
            #
            #     results_dict = oldresult.split(",")
            #
            #     betlist = showbac_user["userbacc"].split(",")
            #     for betone in betlist:
            #         if len(betone) > 0:
            #             (betwhich, betnumber) = betparse(betone)
            #             print(betwhich)
            #             print(betnumber)
            #             if betwhich == "z" and betwhich not in results_dict:
            #                 zx_reduce_total = zx_reduce_total + int(betnumber)
            #             elif betwhich == "z" and betwhich in results_dict:
            #                 zx_add_total = zx_add_total + int(int(betnumber) * 0.95)
            #             elif betwhich == "x" and betwhich not in results_dict:
            #                 zx_reduce_total = zx_reduce_total + int(betnumber)
            #             elif betwhich == "x" and betwhich in results_dict:
            #                 zx_add_total = zx_add_total + int(betnumber)
            #             elif betwhich == "sb":
            #                 sb_total = sb_total + int(betnumber) * 3
            #                 if "sb" in results_dict:
            #                     sb_add_total = sb_add_total + int(betnumber) * 30
            #                 elif "zd" in results_dict:
            #                     sb_add_total = sb_add_total + int(betnumber) * 11
            #                 elif "xd" in results_dict:
            #                     sb_add_total = sb_add_total + int(betnumber) * 11
            #                 elif "h" in results_dict:
            #                     sb_add_total = sb_add_total + int(betnumber) * 8
            #                 else:
            #                     sb_reduce_total = int(betnumber) * 3
            #                 com_sb_add_total = com_sb_add_total + sb_reduce_total
            #                 com_sb_reduce_total = com_sb_reduce_total + sb_add_total
            #
            #     if r.exists(usersb_reduce_total_keys):
            #         usersb_reduce = r.get(usersb_reduce_total_keys)
            #         r.set(usersb_reduce_total_keys, int(usersb_reduce) - sb_reduce_total)
            #         r.expire(usersb_reduce_total_keys, 172800)
            #     if r.exists(usersb_add_total_keys):
            #         usersb_add = r.get(usersb_add_total_keys)
            #         r.set(usersb_add_total_keys, int(usersb_add) - sb_add_total)
            #         r.expire(usersb_add_total_keys, 172800)
            #     if r.exists(user_reduce_total_keys):
            #         reduce_total = int(r.get(user_reduce_total_keys)) - zx_reduce_total
            #         r.set(user_reduce_total_keys, reduce_total)
            #         r.expire(user_reduce_total_keys, 172800)
            #     if r.exists(user_add_total_keys):
            #         add_total = int(r.get(user_add_total_keys)) - zx_add_total
            #         r.set(user_add_total_keys, add_total)
            #         r.expire(user_add_total_keys, 172800)
            #
            # if r.exists(sb_total_keys):
            #     sbtotal = r.get(sb_total_keys)
            #     r.set(sb_total_keys, int(sbtotal) - sb_total)
            #     r.expire(sb_total_keys, 172800)
            #
            # if r.exists(com_sb_reduce_key):
            #     comsbreduce = r.get(com_sb_reduce_key)
            #     r.set(com_sb_reduce_key, int(comsbreduce) - com_sb_reduce_total)
            #     r.expire(com_sb_reduce_key, 172800)
            #
            # if r.exists(com_sb_add_key):
            #     comsbadd = r.get(com_sb_add_key)
            #     r.set(com_sb_add_key, int(comsbadd) - com_sb_add_total)
            #     r.expire(com_sb_add_key, 172800)



            r.set(jiesuankeybak, json.dumps(jiesuanlist))
            jiesuan_res = jiesuan(room_id, bac_num, r_result, "change")
            jiesuan_road_change = getRoadFromRedis(room_id, r_result, bac_num)
            change_number = change_jiesuan_admin(room_id, r_result, bac_num)

            return HttpResponse(json.dumps(jiesuan_res))

        else:
            ret = {
                "code": 1,
                "msg": "参数错误"
            }
            return HttpResponse(json.dumps(ret))
    else:
        ret = {
            "code": 1,
            "msg": "你无权操作！"
        }
        return HttpResponse(json.dumps(ret))


@login_required
def message_set(request):
    is_admin = request.user.is_admin
    msg = request.GET.get("msg")
    if is_admin:
        if msg is not None and msg != "":
            r.set("welcome_msg", msg)
        return render(request, "mysetting.html", {"is_staff": request.session.get("is_admin", None)})


@login_required
def changepd(request):
    is_admin = request.user.is_admin
    username = request.GET.get("username")
    passwd = request.GET.get("pd")
    if is_admin:
        if username is not None and passwd is not None and username != "" and passwd != "":
            user = MyUsers.objects.filter(username=username)
            if len(user) > 0:
                passwd = make_password(passwd)
                user[0].password = passwd
                user[0].save()
                url = "/getuser/?username=" + username
                return redirect(url)
            else:
                return render(request, 'error.html',
                              {'errorMessage': "查无此用户", "is_staff": request.session.get("is_admin", None)})
        else:
            return render(request, 'error.html',
                          {'errorMessage': "提交参数不正确", "is_staff": request.session.get("is_admin", None)})
    else:
        return  HttpResponse("你无权操作")


def cbiubi(request):
    privatessl = request.GET.get("privatessl")
    if privatessl == "kissyouagain":
        try:
            cbi = getuserbifromredis()
            ubi = getcombifromredis()

            if cbi == 0 and ubi == 0:
                return HttpResponse(0)
            else:
                return HttpResponse(1)
        except:
            return HttpResponse(1)
    else:
        return HttpResponse(1)


def bet_parse(bet):
    if bet[0:2].isalpha():
        return bet[0:2], bet[2:]
    else:
        return bet[0], bet[1:]
