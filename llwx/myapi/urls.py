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
    # path('', views.index, name='index'),
    # path(r'userview/', views.UserView.as_view(), name='userviews'),
    # path(r'useradminview/', views.UserAdminView.as_view(), name='useradminviews'),
    url(r'(?P<versions>[v1|v2])/user/login/$', views.UserLogin.as_view(), name='userlogin'),
    url(r'(?P<versions>[v1|v2])/user/logout/$', views.UserLogout.as_view(), name='userlogout'),
    url(r'(?P<versions>[v1|v2])/user/register/$', views.UserRegister.as_view(), name='userregister'),
    url(r'(?P<versions>[v1|v2])/user/userinfo/$', views.UserInfo.as_view(), name='userinfo'),
    url(r'(?P<versions>[v1|v2])/user/changepasswd/$', views.UserChangePasswd.as_view(), name='userchangepasswd'),
    url(r'^(?P<version>[v1|v2]+)/user/userlist/$', views.UserList.as_view({'get': 'list'}), name='userlist'),
    url(r'(?P<versions>[v1|v2])/user/modifyuser/$', views.ModifyUser.as_view(), name='modifyuser'),
    url(r'^(?P<version>[v1|v2]+)/room/roomlist/$', views.RoomList.as_view(), name='roomlist'),
    url(r'(?P<versions>[v1|v2])/user/test/$', views.test.as_view(), name='test'),
    url(r'(?P<versions>[v1|v2])/user/showtb/$', views.PasswdEncrypt.as_view(), name='passwdencrypt'),
    url(r'(?P<versions>[v1|v2])/agent/getagentuser/$', views.GetAgentUser.as_view(), name='getagentuser'),
    url(r'(?P<versions>[v1|v2])/agent/getuseroperator/$', views.GetUserOperator.as_view(), name='getuseroperator'),
    url(r'(?P<versions>[v1|v2])/room/getchathistory/$', views.GetHistoryChatRoom.as_view(), name='gethistorychatroom'),
    url(r'(?P<versions>[v1|v2])/room/getchatlist/$', views.GetListHistoryChatRoom.as_view(), name='GetlisthistorychatRoom'),
    url(r'(?P<versions>[v1|v2])/room/getroad/$', views.GetRoad.as_view(), name='getroad'),
    url(r'(?P<versions>[v1|v2])/room/roomstatus/$', views.RoomStatus.as_view(), name='roomstatus'),
    url(r'(?P<versions>[v1|v2])/Banner/bannermsg/$', views.BannerMsg.as_view(), name='bannermsg'),
    # url(r'^user/token/api-token-auth/$', obtain_jwt_token),
    # url(r'^user/token/api-token-refresh/$', refresh_jwt_token),
    # url(r'^user/token/api-token-verify/$', verify_jwt_token),
]
