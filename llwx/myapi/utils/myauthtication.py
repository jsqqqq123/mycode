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
            result = MyUsers.objects.get(username=username)
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
            raise exceptions.AuthenticationFailed('用户未认证')
            # return None

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
        else:
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


