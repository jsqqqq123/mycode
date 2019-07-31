#Minturnaeque oculos minus ipsa

##Django 的安装

* Django的安装
* Django的设置


##自定义Django的User表



##Django Rest Framework的使用

#### Django RestFramework安装
`pip install restframework`

`注:  如果要用jwt 还需要安装  pip install restframework-jwt`

安装好后, 在 `settings`里的 `INSTALL_APP`进行注册:

        INSTALLED_APPS = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'rest_framework',
            ]

同时在`settings`里添加 `REST_FRAMEWORK`字典 里面的内容可以自己定义,不过健是安装固定来来做

        REST_FRAMEWORK = {
            # rest_framework 默认授权的key  可以改他的value为自己的class类
            'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
            ),
            # rest_framework 默认认证的key  可以改他的value为自己的class类, 也可以删除一些类,比如自己定义的类
            #  mysite.myauth.myauthentication.myclass, 这样的就是自己定义的类 在写mysite.myauth 下的 myautehntication.py下的myclass
            'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.BasicAuthentication',
            ),
        }


操作完上面的配置后, 可以在你的app的views里写你的试图了! 一般情况下, views里的视图都会用 def 的模式建立试图方法, 然后为了要访问
需要在 url里设置他的url路径!

但是我们用rest_framework 的时候  views 视图里基本都是用 class类来建立操作视图! 
比如你这时候views下面的class 是  class UserView(APIView)
这时候 url里的路径则有所变化:

        from django.urls import path
        from . import views
        from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

        urlpatterns = [
            path(r'^getapiview/$', views.UserView.as_view(), name='userviews'),

        ]

用 APIView 类中的 as_view()来创建视图!

我们在views里的 class类如下:

        from rest_framework.views import APIView

        class UserView(APIView):
            # authentication_class 表示我这个view所指定的authentication类用的是哪个, 如果不写,默认去读取 `settings`里的设置 
            # 如果写了,则使用列表里的类, 当然也可以多个类,会按顺序执行验证! 同理授权也有个 `permission_class = []` 这么一个列表
            #authentication_class = [myAuthentication,]   别忘记了导入myAuthencication的类模块

            def get(self, request, *args, **kwargs):
                return HttpResponse('thank you for you visit')


继承APIView, 写一个get方法!

#### Django RestFramework基本使用

上部分我们讲了安装和最简单的使用例子,下面我们完整的来一遍 rest_framework 做api的各项class模块

* `class BaseAuthentication` 认证的基类, 我们建立在定义认证class的时候需要继承它

        from rest_framework.authentication import BaseAuthentication
        from rest_framework import exceptions

        class myAuthentication(BaseAuthentication):
            def authenticate(self, request):
                """
                Authenticate the request and return a two-tuple of (user, token).
                """
                raise NotImplementedError(".authenticate() must be overridden.")

            def authenticate_header(self, request):
                """
                Return a string to be used as the value of the `WWW-Authenticate`
                header in a `401 Unauthenticated` response, or `None` if the
                authentication scheme should return `403 Permission Denied` responses.
                """
                pass

上面两个函数是BaseAuthentication里两个最基本的函数, 我们自定义类中需要实现这两个函数

上面认证类的 authenticate 函数可以有以下几种返回值:

    1. None    表示交给下一个认证类去处理, 如果你有定义多个认证类的话.
    2. 异常,  我们可以在函数里定义   raise exceptions.AuthenticationFailed('用户认证失败')
    3. 元组(user, token)   元素1 复制给request.user    元素2 可以赋值给 request.auth



* `class BasePermission` 授权的基类, 我们建立自己的授权class的时候需要继承它

        from rest_framework.permissions import BasePermission

        class MyPermission(BasePermission):
            def has_permission(self, request, view):
                """
                Return `True` if permission is granted, `False` otherwise.
                """
                return True

            def has_object_permission(self, request, view, obj):
                """
                Return `True` if permission is granted, `False` otherwise.
                """
                return True
 
 上面两个函数是BasePermission里两个最基本的函数, 我们自定义类中需要实现这两个函数


* `class BaseThrottle` 限流的基类, 我们建立自己的限制访问频率的class的时候需要继承它

这个类的操作跟前面两个类的操作类似, 后面我们在继续讨论

* `class BasePagination` 分页操作的类,不过我们一般不会直接继承这个基类, 而是继承 CursorPagination类.


```
class MyPagination(CursorPagination):
    #这个就表示url上的参数  类似于 page=2 这样的功能,表示第几页
    cursor_query_param = 'cursor'
    #表示每页显示的个数
    page_size = 10
    #表示排序
    ordering = 'id'
    #这个表示url上的page_size参数,如果设置了就用这个参数来表示
    #比如 page_size_query_param = page_size 那就是用page_size来代替每页显示的个数
    page_size_query_param = None
    max_page_size = 10
    offset_cutoff = 1000
```
CursorPagination会对你的页码加密,这样人家访问api就无法通过修改page这个参数来跳转了, 当然如果你要让人可以直接修改url来实现跳转,也可以继承其他的类,具体的就可以看BasePagination里面的其他class
以上代码里的参数都是由CursorPagination里定义的我们只是覆盖了.
那么实际的数据从哪里来呢? 

源码里的`def paginate_queryset()`这个函数里面 会有queryset 这个就是数据集


```
# 在views里面写class queryset就在这里设置. 当然如果你名字不叫queryset, 那你就要实现 paginate_queryset() 想办法把queryset传给这个函数

#获取所有用户的列表， 一次获取10条
class UserList(ModelViewSet):
    queryset = MyUsers.objects.all()
    pagination_class = MyPagination
    serializer_class = UserAdminSerializer
```

大致步骤就是以上的一些操作,这里总结一下流程:

首先版本--- authentication 认证--permission 授权--限流--获取数据--分页--最后序列化Serializer--return给client

这里给出总的代码块:

views.py

```
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .utils.mypermissions import MyPermission
from .utils.serializers import UserSerializer, UserAdminSerializer
from .utils.mypagination import MyPagination
from rest_framework_jwt.views import JSONWebTokenSerializer
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
import hashlib
import redis
import time

MyUsers = get_user_model()
try:
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
except:
    print("redis链接失败！")
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER

def index(request):
   pass

#用户登陆后生成token
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


#用户登陆，并将token写入redis
class UserLogin(APIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        ret ={}
        username = request.POST.get('username')
        passwd = request.POST.get('passwd')
        authenuser = authenticate(request, username=username, password=passwd)
        if authenuser is not None:
            login(request=request, user=authenuser)
            mytoken = MyJSONWebTokenSerializer()
            token = mytoken.validate(username, passwd).get('token')
            rkeys = 'JWT' + username
            try:
                r.set(rkeys, token)
                ret['code'] = 2000
                ret['content'] = '登陆成功'
                ret['token'] = token
            except:
                ret['code'] = 7002
                ret['error'] = '设置redis的token失败'

        else:
            ret['code'] = 7001
            ret['error'] = '登陆失败，用户名或密码错误'
        return Response(ret)


#用户注销， 并删除token
class UserLogout(APIView):
    def post(self, request, *args, **kwargs):
        pass

#用户注册
class UserRegister(APIView):
    def post(self, request, *args, **kwargs):
        ret ={}
        username = request.POST.get('username')
        passwd = request.POST.get('passwd')
        agent_id = request.POST.get('agent_id')
        if username != "" and passwd != "" and agent_id != "":
            try:
                authuser = MyUsers.objects.filter(username=username)
                if len(authuser) > 0:
                    ret['code'] = 6001
                    ret['error'] = '用户已经存在'
                    return Response(self.ret)
                md5str = username + str(time.time())
                md5str = md5str.encode('utf-8')
                hmd5 = hashlib.md5()
                hmd5.update(md5str)
                user_id_md5 = hmd5.hexdigest()
                user = MyUsers(username=username, password=make_password(passwd), user_id=user_id_md5,
                               agent_id=agent_id)
                user.save()
                ret['code'] = 2000
                ret['content'] = '用户创建成功'
            except:
                ret['code'] = 6002
                ret['error'] = '用户创建失败'
        else:
            ret['code'] = 6003
            ret['error'] = '创建用户所需要的信息不完全'
        return Response(ret)


#获取单个用户的信息
class UserInfo(APIView):
    def get(self, request, *args, **kwargs):
        ret ={}
        try:
            username = request.GET.get('username')
            query = MyUsers.objects.get(username=username)
            ser = UserAdminSerializer(instance=query, many=False)
            ret['code'] = 2000
            ret['error'] = None
            ret['content'] = ser.data
        except:
            ret['code'] = 3001
            ret['error'] = '用户信息错误，请确认后重新提交'
            ret['content'] = None
        return Response(ret)


#更改用户的密码
class UserChangePasswd(APIView):
    def post(self, request, *args, **kwargs):
        ret ={}
        try:
            username = request.POST.get('username')
            old_passwd = request.POST.get('passwd')
            new_passwd = request.POST.get('newpasswd')
            authenuser = authenticate(request, username=username, password=old_passwd)
            if authenuser is not None:
                authenuser.set_password(new_passwd)
                authenuser.save()
                ret['code'] = 2000
                ret['content'] = '更改密码成功'
            else:
                ret['code'] = 4002
                ret['error'] = '旧密码不正确'
        except:
            ret['code'] = 4001
            ret['error'] = '密码更改错误'
        return Response(ret)


#获取所有用户的列表， 一次获取10条
class UserList(ModelViewSet):
    queryset = MyUsers.objects.all()
    pagination_class = MyPagination
    serializer_class = UserAdminSerializer



```
myauthtication.py


```
#!/usr/bin/env python
#-*- coding: UTF-8 -*-

"""
@version: Python3.6.4
@author:  Justinli

"""
import jwt
from rest_framework.authentication import BaseAuthentication
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model, authenticate, login
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import exceptions
from rest_framework_jwt.settings import api_settings
import redis

MyUsers = get_user_model()
try:
    r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)
except:
    print("redis链接失败！")

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class MyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        #raise NotImplementedError(".authenticate() must be overridden.")
        try:
            if request._request.method == 'GET':
                username = request._request.GET['username']
                password = request._request.GET['password']
            if request._request.method == 'POST':
                username = request._request.POST['username']
                password = request._request.POST['password']
        except:
            raise exceptions.AuthenticationFailed('请带上用户名或者密码')

        authuser = authenticate(request._request, username=username, password=password)

        if authuser is not None:
            login(request._request, authuser)
            result = MyUsers.objects.filter(username=username)
            return (username, result)
        else:
            raise exceptions.AuthenticationFailed('用户未认证')
        # user = authenticate(request._request, username, password)
        # if user is not None:
        #     login(request, user)
        #     return (user, user.token)

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        pass


class MyVerificationBaseSerializer(JSONWebTokenAuthentication):
    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        user, mytoken = self.authenticate_credentials(payload)
        if mytoken != jwt_value:
            msg = _('yours token is not allow to access.')
            raise exceptions.AuthenticationFailed(msg)

        return (user, jwt_value)

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        User = get_user_model()
        username = jwt_get_username_from_payload(payload)
        print(username)

        if not username:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            msg = _('Invalid signature.')
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.AuthenticationFailed(msg)
        rkeys = 'JWT' + username
        try:
            mytoken = r.get(rkeys)
            if mytoken is None:
                msg = _('yours token is not allow to access.')
                raise exceptions.AuthenticationFailed(msg)
        except:
            msg = _('yours token is not allow to access.')
            raise exceptions.AuthenticationFailed(msg)

        return (user, mytoken)

```
mypagination.py


```
#!/usr/bin/env python
#-*- coding: UTF-8 -*-

"""
@version: Python2.7.10
@author:  Justinli

"""
from rest_framework.pagination import CursorPagination


class MyPagination(CursorPagination):
    cursor_query_param = 'cursor'
    page_size = 10
    ordering = 'id'
    page_size_query_param = None
    max_page_size = 10
    offset_cutoff = 1000

```

mypermission.py

```
#!/usr/bin/env python
#-*- coding: UTF-8 -*-

"""
@version: Python3.6.4
@author:  Justinli

"""

from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

Users = get_user_model()

class MyPermission(BasePermission):
    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        # try:
        #     vip = request.user.is_vip
        #     if vip == 7 :
        #         return True
        # except:
        #     return False
        # print(ret)
        ret = request.user

        if ret == 'root':
            return True


    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return True
```

serializers.py


```
#!/usr/bin/env python
#-*- coding: UTF-8 -*-

"""
@version: Python2.7.10
@author:  Justinli

"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

MyUsers = get_user_model()


class UserSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=16)
    username = serializers.CharField(max_length=32)
    avatar_url = serializers.CharField()



class UserAdminSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(max_length=16)
    username = serializers.CharField(max_length=32)

    class Meta:
        model = MyUsers
        fields = ["user_id","username","avatar_url","agent_id","is_admin","state","is_vip","is_active","is_robot","last_login","register_time","type_1"]


```

settings.py


```
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'myapi.utils.myauthtication.MyVerificationBaseSerializer',
        # 'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),

}

JWT_AUTH = {
    'JWT_ENCODE_HANDLER':
    'rest_framework_jwt.utils.jwt_encode_handler',

    'JWT_DECODE_HANDLER':
    'rest_framework_jwt.utils.jwt_decode_handler',

    'JWT_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_payload_handler',

    'JWT_PAYLOAD_GET_USER_ID_HANDLER':
    'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'rest_framework_jwt.utils.jwt_response_payload_handler',

    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=300),
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=1),
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
}

```

urls.py


```
#!/usr/bin/env python
#-*- coding: UTF-8 -*-

"""
@version: Python3.6.4
@author:  Justinli

"""
from django.urls import path
from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from rest_framework.views import APIView

urlpatterns = [
    path('', views.index, name='index'),
    # path(r'userview/', views.UserView.as_view(), name='userviews'),
    # path(r'useradminview/', views.UserAdminView.as_view(), name='useradminviews'),
    url(r'(?P<versions>[v1|v2])/user/login/$', views.UserLogin.as_view(), name='userlogin'),
    url(r'(?P<versions>[v1|v2])/user/register/$', views.UserRegister.as_view(), name='userregister'),
    url(r'(?P<versions>[v1|v2])/user/userinfo/$', views.UserInfo.as_view(), name='userinfo'),
    url(r'(?P<versions>[v1|v2])/user/changepasswd/$', views.UserChangePasswd.as_view(), name='userchangepasswd'),
    url(r'^(?P<version>[v1|v2]+)/user/userlist/$', views.UserList.as_view({'get': 'list'}), name='userlist'),
    url(r'^user/token/api-token-auth/$', obtain_jwt_token),
    url(r'^user/token/api-token-refresh/$', refresh_jwt_token),
    url(r'^user/token/api-token-verify/$', verify_jwt_token),

]
```
ok 上面就是主要的代码了,有部分还没有涉及到 就是 JWT这部分放下面总店讲,

其实JWT的流程跟整个api流程是一样的, 都是通过 view的dispatch来分配此任务操作


```
    url(r'^user/token/api-token-auth/$', obtain_jwt_token),
    url(r'^user/token/api-token-refresh/$', refresh_jwt_token),
    url(r'^user/token/api-token-verify/$', verify_jwt_token),
```
上面三个url 就是 JWT的默认流程来,当然你可以自定义类来继承JWT的相关类,从而替换上面三个类 `obtain_jwt_token` 这个是生成auth token的第一步, 我上面就是用自己的类来创建了部分信息操作,但是我不是直接替换这个类, 而是在验证上面更改了一下操作.

创建一个类,继承`JSONWebTokenAuthentication`,这样你就可以更改JWT的部分流程了.

同理,这个也是Authentication的类, 所以肯定也是有 def authenticate()函数的,源码给的很详细了,你主要知道 jwt加密解密的操作步骤就能够明白了.

jwt主要的操作步骤就是一下几个函数:

```
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER
```

这里的api_settings是 rest_framework_jwt.settings里的,所以你需要用

```
from rest_framework_jwt.settings import api_settings
```
导入进来,那么具体的操作就在这几个函数里了.















