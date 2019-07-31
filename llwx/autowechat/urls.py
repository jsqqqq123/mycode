#!/usr/bin/env python
#-*- coding: UTF-8 -*-

"""
@version: Python2.7.10
@author:  Justinli

"""

from django.urls import path
from . import views
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

urlpatterns = [
    path('', views.index, name='index'),
    path('test', views.test, name='test'),
    path('jwttest', views.jwttest, name='jwttest'),
    path('index_2', views.index_2, name='index_2'),
    path('get_enable_list', views.get_enable_list, name='get_enable_list'),

]