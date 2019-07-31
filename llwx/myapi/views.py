from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .utils.mypermissions import MyPermission
from .utils.serializers import UserSerializer, UserAdminSerializer , RoomSerializer, UserOperatorSerializer, AgentUserSerializer
from .utils.mypagination import MyPagination
from rest_framework_jwt.views import JSONWebTokenSerializer
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from myauth.models import MyAgent, Rooms, MyBi, UserOperator
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
import os.path
import json
# import rsa
import hashlib
# import redis
import time
from chat.utils.tool import getredis, getRoadFromRedisAPI

r = getredis()
MyUsers = get_user_model()

# try:
#     r = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True, db=0)
# except:
#     print("redis链接失败！")
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER

# def index(request):
#    pass

#用户登陆后生成token 用于login接口的登录生成token
class MyJSONWebTokenSerializer(JSONWebTokenSerializer):
    def validate(self, username, passwd):
        credentials = {
            'username': username,
            'password': passwd
        }

        if all(credentials.values()):
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)


class UserView(APIView):

    def get(self, request, *args, **kwargs):
        res = MyUsers.objects.all()
        ser = UserSerializer(instance=res, many=True)

        return Response(ser.data)


class UserAdminView(APIView):
    permission_classes = [MyPermission]

    def post(self, request, *args, **kwargs):
        res = MyUsers.objects.all()
        ser = UserAdminSerializer(instance=res, many=True)

        return Response(ser.data)


#用户登陆，并将token写入redis
class UserLogin(APIView):
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        ret ={}
        tb_keys = ""
        username = request.POST.get('username')
        passwd = request.POST.get('passwd').replace(' ','+')
        money_key = username + "_money"

        if username is None or passwd is None or username == "" or passwd == "":
            ret['code'] = 1
            ret['msg'] = '用户名或者密码不能为空'
            return Response(ret)
        tb = request.POST.get('tb')

        if tb is not None and tb != "":
            tb_keys = "private" + "_" + tb
            if r.exists(tb_keys):
                default_length = 128
                prikey = r.get(tb_keys)
                rsakey_p = RSA.importKey(prikey)

                # cipher_p = PKCS1_v1_5.new(rsakey_p)
                # passwd = cipher_p.decrypt(base64.b64decode(passwd), "ERROR")
                encrypt_byte = base64.b64decode(passwd.encode())
                length = len(encrypt_byte)
                cipher = PKCS1_v1_5.new(rsakey_p)
                if length < default_length:
                    passwd = cipher.decrypt(encrypt_byte, 'failure')
                else:
                    offset = 0
                    res = []
                    while length - offset > 0:
                        if length - offset > default_length:
                            res.append(cipher.decrypt(encrypt_byte[offset: offset +
                                default_length], 'failure'))
                        else:
                            res.append(cipher.decrypt(encrypt_byte[offset:], 'failure'))
                        offset += default_length
                    passwd = b''.join(res)
            else:
                ret['code'] = 1
                ret['msg'] = '登陆失败, rsa private key 不存在'
                return Response(ret)
        else:
            ret['code'] = 1
            ret['msg'] = '没有tb参数'
            return Response(ret)


        authenuser = authenticate(request, username=username, password=passwd)
        if authenuser is not None:
            login(request=request, user=authenuser)
            mytoken = MyJSONWebTokenSerializer()
            token = mytoken.validate(username, passwd).get('token')
            query = MyUsers.objects.get(username=username)
            ser = UserAdminSerializer(instance=query, many=False)
            rkeys = 'JWT' + username
            try:
                r.set(rkeys, token)
                ret['code'] = 0
                ret['msg'] = ser.data
                ret['token'] = token
            except:
                ret['code'] = 1
                ret['msg'] = '设置redis的token失败'
                return Response(ret)
            try:
                myuser = MyUsers.objects.get(username=username)
                mybi = MyBi.objects.filter(user_id=myuser)
                if len(mybi) > 0:
                    print("have mybi")
                    if r.exists(money_key):
                        my_money = r.get(money_key)
                        if mybi[0].cur_m != my_money:
                            mybi[0].cur_m = my_money
                            mybi[0].save()
                            print("save success")

                        ret['code'] = 0
                        ret['money'] = my_money
                    else:
                        print("no money_key one")
                        r.set(money_key, mybi[0].cur_m)
                        ret['code'] = 0
                        ret['money'] = mybi[0].cur_m
                else:
                    print("no money_key two")
                    r.set(money_key, 0)
                    ret['code'] = 0
                    ret['money'] = 0

            except:
                ret['code'] = 0
                if r.exists(money_key):
                    ret['money'] = r.get(money_key)
                    return Response(ret)
                else:
                    r.set(money_key, 0)
                    ret['money'] = 0
                    return Response(ret)

            if r.exists(tb_keys):
                try:
                    r.delete(tb_keys)
                except:
                    ret['code'] = 1
                    ret['msg'] = 'redis prikey delete error!'

        else:
            ret['code'] = 1
            ret['msg'] = '登陆失败，用户名或密码错误'
        return Response(ret)


#用户注销， 并删除token
class UserLogout(APIView):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            username = request.user.username
            tkey = 'JWT' + username
            money_key = username + "_money"
            print(money_key)

            #判断是否有token 有的话退出时删除token
            if r.exists(tkey):
                r.delete(tkey)

            # 判断是否有 当前money的key 如果有 退出的时候 保存到数据库 并删除key
            if r.exists(money_key):
                cur_money =r.get(money_key)
                try:
                    myuser = MyUsers.objects.get(username=username)
                    mybi = MyBi.objects.filter(user_id=myuser)
                    if len(mybi) > 0:
                        mybi[0].cur_m = cur_money
                        mybi[0].save()
                except:
                    error_key = username + "_money" + "_error"
                    r.set(error_key, cur_money)
                    logout(request)
                    return Response({"ret": "None"})
            logout(request)

            return Response({"ret": "ok"})
        else:
            return Response({"ret": "None"})

        # ret= {}
        # username = request.POST.get['username']
        # print(username)
        # if username.is_authenticated():
        #     logout(request)
        #     rkeys = 'JWT' + username
        #     try:
        #         if r.exists(rkeys):
        #             r.delete(rkeys)
        #         ret['code'] = 7001
        #         ret['error'] = '退出成功'
        #         return Response(ret)
        #     except:
        #         raise "token is not valid"
        # else:
        #     raise "用户未登陆"


#用户注册
class UserRegister(APIView):
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        ret ={}
        tb_keys = ""
        username = request.POST.get('username')
        passwd = request.POST.get('passwd').replace(' ','+')
        agent_id = request.POST.get('agent_id')
        nickname = request.POST.get('nickname')
        tb = request.POST.get('tb')
        if tb is not None and tb != "":
            tb_keys = "private" + "_" + tb
            if r.exists(tb_keys):
                prikey = r.get(tb_keys)
                rsakey_p = RSA.importKey(prikey)
                cipher_p = PKCS1_v1_5.new(rsakey_p)
                passwd = cipher_p.decrypt(base64.b64decode(passwd), "ERROR")
            else:
                ret['code'] = 1
                ret['msg'] = '注册失败, publickey error'
                return Response(ret)
        else:
            ret['code'] = 1
            ret['msg'] = '没有tb'
            return Response(ret)
        #这里的passwd 是经过rsa加密过的 所以需要解密
        # try:
        #     passwd = rsa.decrypt(passwd, prikey).decode()
        # except:
        #     ret['code'] =1
        #     ret['msg'] = '密码错误'
        #     return Response(ret)

        if username != "" and passwd != "" and agent_id != "" and nickname != "":
            try:
                myagent = MyAgent.objects.filter(agent_id=agent_id)
                if len(myagent) > 0:
                    try:
                        authuser = MyUsers.objects.filter(username=username)
                        if len(authuser) > 0:
                            ret['code'] = 1
                            ret['msg'] = '用户已经存在'
                            return Response(ret)
                        authnick = MyUsers.objects.filter(nickname=nickname)
                        if len(authnick) > 0:
                            ret['code'] = 1
                            ret['msg'] = '昵称已经存在'
                            return Response(ret)
                        md5str = username + str(time.time())
                        md5str = md5str.encode('utf-8')
                        hmd5 = hashlib.md5()
                        hmd5.update(md5str)
                        user_id_md5 = hmd5.hexdigest()
                        user = MyUsers(username=username, nickname=nickname, password=make_password(passwd), user_id=user_id_md5,
                                       agent_id=agent_id)
                        user.save()

                        if r.exists(tb_keys):
                            try:
                                r.delete(tb_keys)
                            except:
                                ret['code'] = 1
                                ret['msg'] = 'redis prikey delete error!'

                        ret['code'] = 0
                        ret['msg'] = '用户创建成功'
                    except:
                        ret['code'] = 1
                        ret['msg'] = '用户创建失败'
                else:
                    ret['code'] = 1
                    ret['msg'] = '代理不存在'
            except:
                ret['code'] = 1
                ret['msg'] = '代理不存在'
        else:
            ret['code'] = 1
            ret['msg'] = '创建用户所需要的信息不完全'
        return Response(ret)


#获取单个用户的信息
class UserInfo(APIView):
    def post(self, request, *args, **kwargs):
        ret ={}
        try:
            username = request.POST.get('username')
            query = MyUsers.objects.get(username=username)
            ser = UserAdminSerializer(instance=query, many=False)
            money_key = username + "_money"
            if r.exists(money_key):
                my_money = r.get(money_key)

            ret['code'] = 0
            ret['msg'] = ser.data
            ret['money'] = my_money
        except:
            ret['code'] = 0
            ret['msg'] = '用户名不存在或者redis中不存在用户余额数据，请确认后重新提交'
        return Response(ret)


#更改用户的密码
class UserChangePasswd(APIView):
    def post(self, request, *args, **kwargs):
        ret ={}
        tb_keys = ""
        username = request.POST.get('username')
        old_passwd = request.POST.get('passwd').replace(' ','+')
        new_passwd = request.POST.get('newpasswd').replace(' ','+')
        try:
            tb = request.POST.get('tb')
            if tb is not None and tb != "":
                tb_keys = "private" + "_" + tb
                if r.exists(tb_keys):
                    prikey = r.get(tb_keys)
                    rsakey_p = RSA.importKey(prikey)
                    cipher_p = PKCS1_v1_5.new(rsakey_p)
                    old_passwd = cipher_p.decrypt(base64.b64decode(old_passwd), "ERROR")
                    new_passwd = cipher_p.decrypt(base64.b64decode(new_passwd), "ERROR")
                else:
                    ret['code'] = 1
                    ret['msg'] = '注册失败, publickey error'
                    return Response(ret)
            else:
                ret['code'] = 1
                ret['msg'] = '没有tb'
                return Response(ret)

            #
            # try:
            #     old_passwd = rsa.decrypt(old_passwd, prikey).decode()
            #     new_passwd = rsa.decrypt(new_passwd, prikey).decode()
            # except:
            #     ret['code'] =1
            #     ret['msg'] = '密码错误'
            #     return Response(ret)

            authenuser = authenticate(request, username=username, password=old_passwd)
            if authenuser is not None:
                authenuser.set_password(new_passwd)
                authenuser.save()
                ret['code'] = 0
                ret['msg'] = '更改密码成功'
                if r.exists(tb_keys):
                    try:
                        r.delete(tb_keys)
                    except:
                        ret['code'] = 1
                        ret['msg'] = 'redis prikey delete error!'
            else:
                ret['code'] = 1
                ret['msg'] = '旧密码不正确'
        except:
            ret['code'] = 1
            ret['msg'] = '密码更改错误'
        return Response(ret)


#获取所有用户的列表， 一次获取10条
class UserList(ModelViewSet):
    authentication_classes = []
    queryset = MyUsers.objects.all()
    pagination_class = MyPagination
    serializer_class = UserAdminSerializer


# 房间列表
class RoomList(APIView):
    def post(self, request, *args, **kwargs):
        ret = {}
        try:
            myrooms = Rooms.objects.all()
            #循环是添加 bac_num到返回的数据中
            # if len(myrooms) > 0:
            #     for i in myrooms:
            #         bkey = i.room_id + "_number"
            #         if r.exists(bkey):
            #             bacnum[i.room_id] = r.get(bkey)
            #         else:
            #             bacnum[i.room_id] = ""
            #     ret['bac_num'] = bacnum
            myres = RoomSerializer(instance=myrooms, many=True)
            ret['code'] = 0
            ret['msg'] = myres.data
        except:
            ret['code'] = 1
            ret['msg'] = '获得房间信息错误'
        return Response(ret)


class test(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        ret = {}
        myuser = MyUsers.objects.get(username='root')
        mybi = MyBi.objects.get(user_id=myuser)
        if mybi is not None:
            ret['code'] = 0
            ret['msg'] = mybi.cur_m
        return Response(ret)


#获取 rsa的 publickey 和privatekey
class PasswdEncrypt(APIView):
    authentication_classes = []
    def post(self, request, *args, **kwargs):
        ret = {}
        tb = request.POST.get('tb')
        print(tb)
        if tb != "" and tb is not None:
            RANDOM_GENERATOR=Random.new().read
            rsa = RSA.generate(1024, RANDOM_GENERATOR)
            PRIVATE_PEM = rsa.exportKey()
            PUBLIC_PEM = rsa.publickey().exportKey()

        #     (pubkey, prikey) = rsa.newkeys(1024)
        #     pubkeys = pubkey.save_pkcs1().decode()
        #     prikeys = prikey.save_pkcs1().decode()
            tb_keys = "private" + "_" + tb
            if r.exists(tb_keys):
                ret['code'] = 1
                return Response(ret)
            else:
                r.set(tb_keys, PRIVATE_PEM)
                r.expire(tb_keys, 600)
                ret['code'] = 0
                ret['msg'] = PUBLIC_PEM
                return Response(ret)
        else:
            ret['code'] = 1
            return Response(ret)


#获取聊天记录, post方式发送 room_name bac_num
class GetHistoryChatRoom(APIView):
    def post(self,request, *args, **kwargs):
        room_name = request.POST.get('room_name')
        bac_num = request.POST.get('bac_num')
        ret = {}
        filename = 'log/h' + room_name + bac_num + '.log'
        if room_name is not None and bac_num is not None:
            return_reuslt = []
            if os.path.isfile(filename):
                with open(filename, 'r') as f:
                    for line in f.readlines():
                        line = line.strip().replace("\\","")
                        return_reuslt.append(line)
                    ret['msg'] = return_reuslt
                    ret['code'] = 0
                print(ret)
                return Response(ret)
            else:
                ret['msg'] = "文件不存在"
                ret['code'] = 1
                return Response(ret)
        else:
            ret['msg'] = "缺少参数"
            ret['code'] = 1
            return Response(ret)


#获取 历史记录的列表
class GetListHistoryChatRoom(APIView):
    def post(self, request, *args, **kwargs):
        room_name = request.POST.get('room_name')
        ret = {}
        if room_name is not None and room_name != "":
            hkey = "historylistkey_" + room_name

            #返回的格式是 '12ju25xue_12ju26xue_12ju27xue' 这样的格式
            result_list = []
            if r.exists(hkey):
                hroomlist = r.get(hkey)
                flist = hroomlist.split('_')
                for i in flist:
                    result_list.append({
                        'bacnum': i.split('#')[0],
                        'time': i.split('#')[1]
                    })
                ret['code'] = 0
                ret['msg'] = result_list
                return Response(ret)
            else:
                ret['code'] = 1
                ret['msg'] = '还没有历史记录'
                return Response(ret)
        else:
            ret['code'] = 1
            ret['msg'] = '参数传递错误'
            return Response(ret)

#获取房间的录单信息
class GetRoad(APIView):
    def post(self, request, *args, **kwargs):
        room_name = request.POST.get('room_name')
        ret = {}
        if room_name is not None and room_name != "":
            result = getRoadFromRedisAPI(room_name)
            if result is not None:
                ret['code'] = 0
                ret['msg'] = result
            else:
                ret['code'] = 1
                ret['msg'] = '获取路单信息错误'
        #     road_key = room_name + "_road"
        #     if r.exists(road_key):
        #        road_result = r.get(road_key)
        #        ret['code'] = 0
        #        ret['msg'] = road_result
        #     else:
        #         ret['code'] = 1
        #         ret['msg'] = 'redis没有该房间路单key的信息'
        else:
            ret['code'] = 1
            ret['msg'] = '参数传递的不对'

        return Response(ret)


#用户信息修改
class ModifyUser(APIView):
    def post(self, request, *args, **kwargs):
        ret = {}
        nickname = request.POST.get('nickname')
        username = request.POST.get('username')
        avatar_url = request.POST.get('avatar_url')
        if username is not None and username != "":
            try:
                muser = MyUsers.objects.get(username=username)
                if nickname is not None and nickname != "":
                    if muser.nickname == nickname:
                        ret['code'] = 1
                        ret['msg'] = "昵称重复！"
                        return Response(ret)
                    else:
                        muser.nickname = nickname
                elif avatar_url is not None and avatar_url != "":
                    muser.avatar_url = avatar_url
                else:
                    ret['code'] = 1
                    ret['msg'] = '缺少参数'
                    return Response(ret)

                ret['code'] = 0
                muser.save()
                return Response(ret)
            except:
                ret['code'] = 1
                ret['msg'] = '用户名不对'
        else:
            ret['code'] = 1
            ret['msg'] = '需要传递用户名'
        return Response(ret)


#房间投注状态获取
class RoomStatus(APIView):
    def post(self, request, *args, **kwargs):
        ret = {}
        room_name = request.POST.get('room_name')
        if room_name is not None and room_name != "":
            statuskey = room_name + "_status"
            if r.exists(statuskey):
                res_list = r.get(statuskey).split(",")
                if len(res_list) == 2:
                    ret["msg"] = res_list[0]
                    ret["bac_num"] = res_list[1]
                else:
                    ret["msg"] = res_list[0]
                    ret["bac_num"] = ""
            else:
                r.set(statuskey, "false")
                ret["msg"] = "false"
                ret["bac_num"] = ""
            ret["code"] = 0
            return Response(ret)
        else:
            ret["code"] = 1
            ret["msg"] = "请传房间号来获取状态"
            return Response(ret)


class GetUserOperator(APIView):
    def post(self, request, *args, **kwargs):
        ret = {}
        username = request.POST.get('username')
        if username is not None and username != "":
            res = UserOperator.objects.filter(username=username)
            if len(res) > 0:
                myres = UserOperatorSerializer(instance=res, many=True)
                ret["code"] = 0
                ret['msg'] = myres.data
            else:
                ret["code"] = 2
                ret['msg'] = "你代理的用户没有下过注"
        else:
            ret['code'] = 1
            ret['msg'] = '请带上用户名'
        return Response(ret)


class GetAgentUser(APIView):
    def post(self, request, *args, **kwargs):
        ret = {}
        agent_id = request.POST.get("agent_id")
        if agent_id is not None and agent_id != "":
            res = MyUsers.objects.filter(agent_id=agent_id)
            if len(res) > 0:
                myres = AgentUserSerializer(instance=res, many=True)
                ret['code'] = 0
                ret['msg'] = myres.data
            else:
                ret['code'] = 2
                ret['msg'] = "你暂时还未发展代理用户,请加油"
        else:
            ret['code'] = 1
            ret['msg'] = "请带上代理id"
        return Response(ret)


class BannerMsg(APIView):
    authentication_classes = []
    def get(self, request, *args, **kwargs):
        ret = {}
        ret["code"] = 0 

        if r.exists("welcome_msg"):
            ret["msg"] = r.get("welcome_msg")
        else:
            ret["msg"] = "欢迎光临，大家玩的开心开心开心啊！！！"
        return Response(ret)
