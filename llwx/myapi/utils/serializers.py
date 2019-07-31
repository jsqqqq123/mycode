#!/usr/bin/env python
#-*- coding: UTF-8 -*-

"""
@version: Python2.7.10
@author:  Justinli

"""
from django.contrib.auth import get_user_model
from rest_framework import serializers
from myauth.models import Rooms, UserOperator
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
        fields = ["user_id","username","nickname","avatar_url","agent_id","is_admin","state","is_vip","is_active","is_robot","last_login","register_time","type_1"]


class RoomSerializer(serializers.ModelSerializer):
    room_id = serializers.CharField(max_length=10)
    room_name = serializers.CharField(max_length=20)

    class Meta:
        model = Rooms
        fields = ["room_id", "room_name", "room_video", "is_active", "is_public", "is_vip", "passwd", "room_admin", "agent_id"]


class UserOperatorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255)

    class Meta:
        model = UserOperator
        fields = ["username", "bacc_num", "xiazhu", "pre_yue", "result", "after_yue", "xiazhu_date"]


class AgentUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    nickname = serializers.CharField(max_length=255)
    agent_id = serializers.CharField(max_length=255)
    register_time = serializers.DateField()
