from django.shortcuts import render

# Create your views here.
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from .models import MyBi, Combi, UserBi
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
import json
import time
import hashlib
import django.utils.timezone as timezone

MyUsers = get_user_model()

@login_required
def index(request):
    userinfo = MyUsers.objects.filter(agent_id="aaaaaaaaaaaaaaaa")
    my_monel = []
    for i in range(0, len(userinfo)):
        print(type(i))
        print(userinfo[i])
        userbi = MyBi.objects.get(user_id=userinfo[i])
        print(userbi.cur_m)
        my_monel.append(userbi.cur_m)


    return HttpResponse(my_monel)


def myloginapi(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            password = request.POST['password']
            if username != "" and password != "":
                authuser = authenticate(request, username=username, password=password)
                if authuser is not None:
                    login(request, authuser)
                    ret = {'code': 200, 'message': '', 'data': None}

                    try:
                        res_user = MyUsers.objects.filter(username=username)
                        if res_user is not None:
                            myinfo = {}
                            myinfo['username'] = res_user[0].username
                            myinfo['user_id'] = res_user[0].user_id
                            myinfo['nickname'] = res_user[0].nickname
                            myinfo['avatar_url'] = res_user[0].avatar_url
                            myinfo['is_admin'] = res_user[0].is_admin
                            myinfo['state'] = res_user[0].state
                            myinfo['is_vip'] = res_user[0].is_vip
                            myinfo['is_active'] = res_user[0].is_active
                            myinfo['is_talke'] = res_user[0].is_talke
                            myinfo['is_robot'] = res_user[0].is_robot
                            myinfo['last_login'] = res_user[0].last_login
                            myinfo['register_time'] = res_user[0].register_time
                            myinfo['type_1'] = res_user[0].type_1
                            myinfo['type_2'] = res_user[0].type_2
                            myinfo['type_3'] = res_user[0].type_3
                            ret['data'] = myinfo
                            return JsonResponse(ret)

                    except:
                        ret = {'code': 402, 'message': '用户信息读取错误', 'data': None}
                        return JsonResponse(ret)
                else:
                    ret = {'code': 401, 'message': '用户名密码错误', 'data': None}
                    return JsonResponse(ret)
        except:
            ret = {'code': 400, 'message': '缺少用户名否则密码', 'data': None}
            return JsonResponse(ret)


def myRegisterapi(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username != "" and password != "":
            authuser = MyUsers.objects.filter(username=username)
            if len(authuser) > 0:
                ret = {'code': 400, 'message': '用户已存在', 'data': None}
                return JsonResponse(ret)
            md5str = username + str(time.time())
            md5str = md5str.encode('utf-8')
            hmd5 = hashlib.md5()
            hmd5.update(md5str)
            user_id_md5 = hmd5.hexdigest()

            user = MyUsers(username=username, password=password, user_id=user_id_md5,
                           agent_id='aaaaaaaaaaaaaaa')
            user.save()
            ret = {'code': 200, 'message': '用户创建成功', 'data': None}

            return JsonResponse(ret)


def test(rquest):
    import datetime
    now = datetime.datetime.now()
    start = now - datetime.timedelta(hours=23, minutes=59, seconds=59)
    #start = now - datetime.timedelta(hours=23)
    combi = Combi.objects.filter(date_time__year="2019",date_time__month="02", date_time__day="18")
    #combi = Combi.objects.filter(date_time__range=["2019-02-19","2019-02-20"])
    rest = []
    #rest.append(combi[0].date_time)
    rest.append(now)
    rest.append(start)
    return HttpResponse(combi[0].date_time)
