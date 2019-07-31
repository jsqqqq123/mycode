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