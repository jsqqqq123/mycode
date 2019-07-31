from django.shortcuts import render, render_to_response
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from django.http import HttpResponse
from django.contrib.auth import logout
from myauth.models import Rooms
from .utils.tool import fromStrParseInt
import json
# import redis
from .utils.tool import getredis
from django.contrib.auth.decorators import login_required


r = getredis()


# r = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True, db=0)


def index(request):
    room_list = {
        'one': {
            'name': '大上海',
            'id': 'room001'
        },
        'two': {
            'name': '香港',
            'id': 'room002'
        },
    }

    return render(request, 'chat/index.html', {'room_list': room_list})


def room(request, room_name):
    # if room_name == "":
    #     return HttpResponse("must have room_name")
    # return render(request, 'chat/room.html', {'room_name_json': mark_safe(json.dumps(room_name))})

    room_name = room_name
    username = request.user
    return render(request, 'chat/room.html', {'room_name_json': room_name, 'username': username})


def admin(request, room_name):
    room_name = room_name
    username = request.user
    return render(request, 'chat/admin.html', {'admin_name_json': room_name, 'username': username})

def test(request):
    return render(request, 'chat/adminchat.html',{})

@login_required
def adminchat(request):
    username = request.user.username
    print(username)
    rooms = Rooms.objects.filter(room_admin=username)
    print(rooms)
    roomlist = []
    if len(rooms) > 0:
        for roominfo in rooms:
            data = {
                'room_name': roominfo.room_name,
                'room_id': roominfo.room_id,
            }
            roomlist.append(data)
    print(roomlist)
    return render(request, 'chat/adminchat.html', {'roomlist': roomlist})


def juNumber(request):
    room_id = request.GET.get('roomnum')
    if room_id is None or room_id == "":
        return HttpResponse('error')
    benxue = request.GET.get('benxue')
    jinri = request.GET.get('jinri')
    keys = room_id + "_number"
    pre_juresult = room_id + "_pre_result"
    roomroad = room_id + "_road"
    if benxue is not None and benxue == 'add':
        if r.exists(roomroad):
            r.set(roomroad, "")
        if r.exists(pre_juresult):
            r.set(pre_juresult, "")
        if r.exists(keys):
            roomnum = r.get(keys)
            numlist = fromStrParseInt(roomnum)
            room_str = str(int(numlist[0]) + 1) + 'xue0ju'
            r.set(keys, room_str)
            return HttpResponse(room_str)
        else:
            roomnum = "1xue0ju"
            r.set(keys, roomnum)
            return HttpResponse(roomnum)
    elif jinri is not None and jinri == 'over':
        if r.exists(roomroad):
            r.set(roomroad, "")
        if r.exists(pre_juresult):
            r.set(pre_juresult, "")
        if r.exists(keys):
            roomnum = r.get(keys)
            numlist = fromStrParseInt(roomnum)
            room_str = str(int(numlist[0]) + 1) + 'xue0ju'
            r.set(keys, room_str)
            return HttpResponse(room_str)
        else:
            roomnum = "1xue0ju"
            r.set(keys, roomnum)
            # return HttpResponse(roomnum)
            return HttpResponse('今日结束')
       # if r.exists(keys):
        #    r.delete(keys)
        #    roomnum = "1xue0ju"
        #    return HttpResponse('今日结束')
    else:
        if r.exists(keys):
            roomnum = r.get(keys)
            numlist = fromStrParseInt(roomnum)
            room_str = str(numlist[0]) + 'xue' + str(int(numlist[1]) + 1) + 'ju'
            r.set(keys, room_str)
            print(room_str)
            return HttpResponse(room_str)
        else:
            roomnum = "1xue1ju"
            r.set(keys, roomnum)
            print(roomnum)
            return HttpResponse(roomnum)

#将redis里的 本靴的所有用户聊天信息 写入到文件中 文件以 hroom00125ju11xue.log 这样的格式
def historyChatRoom(request):
    room_name = request.POST.get('room_name')
    bac_num = request.POST.get('bac_num')
    ret = {}
    if room_name is not None and bac_num is not None:
        hkeys = 'h' + room_name + bac_num + '*'
        filename = './chatlog/h' + room_name + bac_num + '.log'

        keys = r.keys(hkeys)
        if len(keys) > 0:
            with open(filename, 'a+') as f:
                for key in keys:
                    f.writeline(r.get(key))
            ret['code'] = 0
            ret['msg'] = "历史记录写入成功"
        else:
            ret['code'] = 1
            ret['msg'] = "没有历史记录"
    else:
        ret['code'] = 1
        ret['msg'] = "没有历史记录"

    return HttpResponse(json.dumps(ret))

def getroomjunum(request):
    room_name = request.GET.get('roomnum')
    if room_name is not None and room_name != "":
        rkeys = room_name + "_number"
        if r.exists(rkeys):
            room_bacc = r.get(rkeys)
            return HttpResponse(room_bacc)
        else:
            room_bacc = "0ju0xue"
            return HttpResponse(room_bacc)
    else:
        return HttpResponse("0ju0xue")





