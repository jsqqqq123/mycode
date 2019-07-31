#!/usr/bin/env python
#-*- coding: UTF-8 -*-

"""
@version: Python3.6.4
@author:  Justinli

"""

from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer),
    url(r'^ws/admin/(?P<room_name>[^/]+)/$', consumers.AdminConsumer),
]