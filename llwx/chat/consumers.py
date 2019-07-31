#!/usr/bin/env python
#-*- coding: UTF-8 -*-

"""
@version: Python3.6.4
@author:  Justinli

"""

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .utils import baccarat
from .utils.tool import getredis, getRoadFromRedis, historyChatRoom, parseEndStatus, hashmd5, show_admin_bac, jiesuan_admin, zx_count
import json
import time
import logging


logger = logging.getLogger(__name__)
# from channels.exceptions import (
#     InvalidChannelLayerError,
#     StopConsumer,
# )
# import redis

# r = redis.StrictRedis(host='127.0.0.1', port=6379, decode_responses=True, db=0)
r = getredis()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    TOUZHU = True
    async def connect(self):
        if self.scope["user"].username != "" and self.scope["user"].username is not None and self.scope["user"].username != "AnonymousUser":
            self.username = self.scope['user'].username
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = 'chat_%s' % self.room_name
            ws_login_key = self.username + "wslogin"
            if r.exists(ws_login_key):
                dis_channel_name = r.get(ws_login_key)
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    dis_channel_name
                )
                r.set(ws_login_key, self.channel_name)


            # if self.channel_name in list(self.groups.get(self.room_group_name, set())):
            #     await self.disconnect()
            # else:

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            r.set(ws_login_key, self.channel_name)
        # 发送欢迎消息 待测试
            welcome_msg = {
                'msg_type': 8,
                'from_username': 'admin',
                'from_nickname': 'admin',
                'content': '欢迎' + self.scope["user"].username +'大驾光临',
                'type': 'welcome_msg'
            }

            await self.channel_layer.group_send(
                self.room_group_name,
                welcome_msg,
            )
        elif len(self.scope['query_string']) > 0:
            query_string = self.scope['query_string'].decode()
            auth_username = query_string.split('&')[0].split('=')[1]
            auth_token = query_string.split('&')[1].split('=')[1]
            auth_key = 'JWT' + auth_username
            if r.exists(auth_key):
                if r.get(auth_key) == auth_token:
                    self.username = auth_username
                    self.room_name = self.scope['url_route']['kwargs']['room_name']
                    self.room_group_name = 'chat_%s' % self.room_name
                    # if self.channel_name in list(self.groups.get(self.room_group_name, set())):
                    #     await self.disconnect()
                    # else:
                    ws_login_key = self.username + "wslogin"
                    if r.exists(ws_login_key):
                        dis_channel_name = r.get(ws_login_key)
                        await self.channel_layer.group_discard(
                            self.room_group_name,
                            dis_channel_name
                        )
                        r.set(ws_login_key, self.channel_name)

                    await self.channel_layer.group_add(
                        self.room_group_name,
                        self.channel_name
                    )
                    await self.accept()
                    r.set(ws_login_key, self.channel_name)
                # 发送欢迎消息 待测试
                    welcome_msg = {
                        'msg_type': 8,
                        'from_username': 'admin',
                        'from_nickname': 'admin',
                        'content': '欢迎' + self.username +'大驾光临',
                        'type': 'welcome_msg'
                    }

                    await self.channel_layer.group_send(
                        self.room_group_name,
                        welcome_msg,
                    )
                else:
                    return 1
            else:
                return 1
        else:
            return 1



    async def welcome_msg(self, event):
        print(event)
        message = event
        await self.send_json(message)


    # async def disconnect(self, code):
    #     print(self.username + ": is Disconnect")

    # async def disconnect(self, code):
    #     print(self.usern1ame + ": is Disconnect")
    #     m_return = checkUserMoney(self.username)
    #     if m_return == 1:
    #         print("用户名错误,非法登录用户")
    #     # await self.channel_layer.group_discard(
    #     #     self.room_group_name,
    #     #     self.channel_layer
    #     # )
    #
    #     try:
    #         for group in self.groups:
    #             await self.channel_layer.group_discard(group, self.channel_name)
    #     except AttributeError:
    #         raise InvalidChannelLayerError(
    #             "BACKEND is unconfigured or doesn't support groups"
    #         )
    #     raise StopConsumer()

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        text_data_json['type'] = 'chat_message'
        sendmessage = text_data_json
        logger.info(sendmessage)
        if sendmessage["msg_type"] != 4: 
            hkeys = 'h' + sendmessage['room_name'] + sendmessage['bac_num'] + '_' + sendmessage['msg_id']
            r.set(hkeys, json.dumps(sendmessage, ensure_ascii=False))
            r.expire(hkeys, 600)
        startkey = sendmessage['room_name'] + "_status"
        if sendmessage['msg_type'] == 0:

            await self.channel_layer.group_send(
                    self.room_group_name,
                    sendmessage,
                )

            pret = parseEndStatus(sendmessage['content'])
            if pret == 1:
                content = "@" + sendmessage['from_nickname'] + ": 已经截止投注了,你的此次投注无效!请等待下一靴!"
                msg_id = hashmd5()
                admin_return_msg = {
                    "msg_type": 5,
                    "msg_id": msg_id,
                    "from_username": "admin",
                    "from_nickname": "admin",
                    "to_nickname": sendmessage['from_nickname'],
                    "room_name": sendmessage['room_name'],
                    "avatar_url": "9",
                    "bac_num": sendmessage['bac_num'],
                    "content": content,
                    "type": "chat_message"
                }
                logger.info(admin_return_msg)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    admin_return_msg,
                )

        elif sendmessage['msg_type'] == 2:
            await self.channel_layer.group_send(
                self.room_group_name,
                sendmessage,
            )
            # parse_msg = baccarat.message_parse(sendmessage)
            # if parse_msg['code'] == 0:
            room_name = sendmessage['room_name']
            # bac_num = sendmessage['bac_num']
            # username = sendmessage['username']
            # xiazhu_type = sendmessage['xiazhu_type']
            # money = parse_msg['money']
            # yue_money = parse_msg['yue_money']
            # xiazhu_type_code = baccarat.xiazhu(room_id=room_name, baccarat_id=bac_num, username=username, xiazhu_type=xiazhu_type, money=money, yue_money=yue_money)
            xiazhu_type_code = baccarat.message_parse(sendmessage)
            if xiazhu_type_code['code'] == 0:
                content = "@" + sendmessage['from_nickname'] + ": " + sendmessage['content'] + " 下注成功，剩余金额为：" + str(
                    xiazhu_type_code['yue_money'])
                msg_id = hashmd5()
                admin_return_msg = {
                    "msg_type": 5,
                    "msg_id": msg_id,
                    "from_username": "admin",
                    "from_nickname": "admin",
                    "to_nickname": sendmessage['from_nickname'],
                    "room_name": room_name,
                    "avatar_url": "9",
                    "bac_num": sendmessage['bac_num'],
                    "content": content,
                    "type": "chat_message"
                }
            elif xiazhu_type_code['code'] == 2:
                content = "@" + sendmessage['from_nickname'] + ": " + sendmessage['content'] + " 下注成功，剩余金额为：" + str(
                    xiazhu_type_code['yue_money']) + "【！！！你有庄闲对押的行为，请注意！！！】"
                msg_id = hashmd5()
                admin_return_msg = {
                    "msg_type": 5,
                    "msg_id": msg_id,
                    "from_username": "admin",
                    "from_nickname": "admin",
                    "to_nickname": sendmessage['from_nickname'],
                    "room_name": room_name,
                    "avatar_url": "9",
                    "bac_num": sendmessage['bac_num'],
                    "content": content,
                    "type": "chat_message"
                }
            else:
                content = "@" + sendmessage['from_nickname'] + ":" + xiazhu_type_code['msg']
                msg_id = hashmd5()
                admin_return_msg = {
                    "msg_type": 5,
                    "msg_id": msg_id,
                    "from_username": "admin",
                    "from_nickname": "admin",
                    "to_nickname": sendmessage['from_nickname'],
                    "room_name": room_name,
                    "avatar_url": "9",
                    "bac_num": sendmessage['bac_num'],
                    "content": content,
                    "type": "chat_message"
                }
            hkeys = 'h' + admin_return_msg['room_name'] + admin_return_msg['bac_num'] + '_' + admin_return_msg['msg_id']
            r.set(hkeys, json.dumps(admin_return_msg, ensure_ascii=False))
            r.expire(hkeys, 600)
            logger.info(admin_return_msg)
            await self.channel_layer.group_send(
                self.room_group_name,
                admin_return_msg,
            )
            # else:
            #     content = "@"+ sendmessage['from_username'] + ":" + parse_msg['msg']
            #     admin_return_msg = {
            #         'msg_type': 5,
            #         'msg_id': 12739108239012309,
            #         'from_username': "admin",
            #         'from_nickname': "admin",
            #         "room_name": sendmessage['room_name'],
            #         "avatal_url": "http://lelewuxian.com",
            #         "bac_num": sendmessage['bac_num'],
            #         "content": content,
            #     }
        elif sendmessage['msg_type'] == 3:
            if sendmessage['msg_admin'] is not None and sendmessage['msg_admin'] == 100:
                start_value = "true" + "," + sendmessage['bac_num']
                r.set(startkey, start_value)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    sendmessage,
                )

            elif sendmessage['msg_admin'] is not None and sendmessage['msg_admin'] == 200:
                start_value = "fasle" + "," + sendmessage['bac_num']
                r.set(startkey, start_value)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    sendmessage,
                )

            elif sendmessage['msg_admin'] is not None and sendmessage['msg_admin'] == 300:
                bacc_return_code = baccarat.show_bac(sendmessage['room_name'], sendmessage['bac_num'])
                if bacc_return_code is not None and bacc_return_code['code'] == 0:
                    content = bacc_return_code['msg']
                    msg_id = hashmd5()
                    admin_return_msg = {
                        "msg_type": 6,
                        "msg_id": msg_id,
                        "from_username": "admin",
                        "from_nickname": "admin",
                        "to_nickname": sendmessage['from_nickname'],
                        "room_name": sendmessage['room_name'],
                        "avatar_url": "9",
                        "bac_num": sendmessage['bac_num'],
                        "content": content,
                        "type": "chat_message"
                    }

                else:
                    content = "@ALL 所有人 " + sendmessage['bac_num'] + ":本靴下注错误，请大家稍后，本靴将转人工处理！"
                    msg_id = hashmd5()
                    admin_return_msg = {
                        "msg_type": 5,
                        "msg_id": msg_id,
                        "from_username": "admin",
                        "from_nickname": "admin",
                        "to_nickname": sendmessage["from_nickname"],
                        "room_name": sendmessage['room_name'],
                        "avatar_url": "9",
                        "bac_num": sendmessage['bac_num'],
                        "content": content,
                        "type": "chat_message"
                    }
                hkeys = 'h' + admin_return_msg['room_name'] + admin_return_msg['bac_num'] + '_' + admin_return_msg[
                    'msg_id']
                r.set(hkeys, json.dumps(admin_return_msg, ensure_ascii=False))
                r.expire(hkeys, 600)
                logger.info(admin_return_msg)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    admin_return_msg,
                )

                try:
                    showadminbac = show_admin_bac(sendmessage['room_name'], sendmessage['bac_num'])
                except:
                    showadminbac = None

                if showadminbac is not None and showadminbac["code"] == 0:
                    self.TOUZHU = True
                    msg_id = hashmd5()
                    admin_return_msg = {
                        "msg_type": 11,
                        "msg_id": msg_id,
                        "from_username": "admin",
                        "from_nickname": "admin",
                        "to_nickname": "",
                        "room_name": sendmessage['room_name'],
                        "avatar_url": "9",
                        "bac_num": sendmessage['bac_num'],
                        "content": showadminbac["msg"],
                        "type": "chat_message"
                    }
                    logger.info(admin_return_msg)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        admin_return_msg,
                    )
                # elif showadminbac is not None and showadminbac["code"] == 1:
                #     self.TOUZHU = False
                #     msg_id = hashmd5()
                #     admin_return_msg = {
                #         "msg_type": 10,
                #         "msg_id": msg_id,
                #         "from_username": "admin",
                #         "from_nickname": "admin",
                #         "to_nickname": "",
                #         "room_name": sendmessage['room_name'],
                #         "avatar_url": "9",
                #         "bac_num": sendmessage['bac_num'],
                #         "content": showadminbac["msg"],
                #         "type": "chat_message"
                #     }
                #     logger.info(admin_return_msg)
                #     await self.channel_layer.group_send(
                #         self.room_group_name,
                #         admin_return_msg,
                #     )

                else:
                    msg_id = hashmd5()
                    admin_return_msg = {
                        "msg_type": 10,
                        "msg_id": msg_id,
                        "from_username": "admin",
                        "from_nickname": "admin",
                        "to_nickname": "",
                        "room_name": sendmessage['room_name'],
                        "avatar_url": "9",
                        "bac_num": sendmessage['bac_num'],
                        "content": "出错了",
                        "type": "chat_message"
                    }
                    logger.info(admin_return_msg)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        admin_return_msg,
                    )
            elif sendmessage['msg_admin'] is not None and sendmessage['msg_admin'] == 400:
                if self.TOUZHU:
                    jiesuan_return_code = baccarat.jiesuan(sendmessage['room_name'], sendmessage['bac_num'],
                                                           sendmessage['content'])
                    if jiesuan_return_code['code'] == 0:
                        content = jiesuan_return_code['msg']
                        msg_id = hashmd5()
                        admin_return_msg = {
                            "msg_type": 7,
                            "msg_id": msg_id,
                            "from_username": "admin",
                            "from_nickname": "admin",
                            "room_name": sendmessage['room_name'],
                            "avatar_url": "9",
                            "bac_num": sendmessage['bac_num'],
                            "content": content,
                            "type": "chat_message"
                        }
                        hkeys = 'h' + admin_return_msg['room_name'] + admin_return_msg['bac_num'] + '_' + admin_return_msg[
                            'msg_id']
                        r.set(hkeys, json.dumps(admin_return_msg, ensure_ascii=False))
                        r.expire(hkeys, 600)
                        history_ret = historyChatRoom(admin_return_msg['room_name'], admin_return_msg['bac_num'])
                        if history_ret['code'] == 0:
                            print(history_ret['msg'])
                        else:
                            print(history_ret['msg'])
                        historylistkey = "historylistkey_" + admin_return_msg['room_name']
                        if r.exists(historylistkey):
                            hlist = r.get(historylistkey)
                            if len(hlist.split('_')) < 15:
                                hlists = hlist + "_" + admin_return_msg['bac_num'] + "#" + time.strftime('%m-%d %H:%M')
                                r.set(historylistkey, hlists)
                            else:
                                newlist = hlist.split('_')[1:]
                                hlists = '_'.join(newlist)
                                hlists = hlists + "_" + admin_return_msg['bac_num'] + "#" + time.strftime('%m-%d %H:%M')
                                r.set(historylistkey, hlists)
                        else:
                            hlists = admin_return_msg['bac_num'] + "#" + time.strftime('%m-%d %H:%M')
                            r.set(historylistkey, hlists)
                    elif jiesuan_return_code['code'] == 1:
                        logger.info(jiesuan_return_code["msg"])
                        content = "@ALL 所有人 " + sendmessage['bac_num'] + ":本靴showbac不存在，请大家稍后，本靴将转人工处理！"
                        msg_id = hashmd5()
                        admin_return_msg = {
                            "msg_type": 5,
                            "msg_id": msg_id,
                            "from_username": "admin",
                            "from_nickname": "admin",
                            "room_name": sendmessage['room_name'],
                            "avatar_url": "9",
                            "bac_num": sendmessage['bac_num'],
                            "content": content,
                            "type": "chat_message"
                        }
                    else:
                        logger.info(jiesuan_return_code["msg"])
                        content = "@ALL 所有人 " + sendmessage['bac_num'] + ":本靴结算错误，请大家稍后，本靴将转人工处理！"
                        msg_id = hashmd5()
                        admin_return_msg = {
                            "msg_type": 5,
                            "msg_id": msg_id,
                            "from_username": "admin",
                            "from_nickname": "admin",
                            "room_name": sendmessage['room_name'],
                            "avatar_url": "9",
                            "bac_num": sendmessage['bac_num'],
                            "content": content,
                            "type": "chat_message"
                        }
                    logger.info(admin_return_msg)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        admin_return_msg,
                    )
                    try:
                        jiesuanadmin_result = jiesuan_admin(sendmessage['room_name'], sendmessage['content'], sendmessage['bac_num'])
                    except:
                        jiesuanadmin_result = None
                    print("*****")
                    print(jiesuanadmin_result)
                    print("******")
                    if jiesuanadmin_result is not None and jiesuanadmin_result == 0:
                        pass
                    else:
                        msg_id = hashmd5()
                        admin_return_msg = {
                            "msg_type": 10,
                            "msg_id": msg_id,
                            "from_username": "admin",
                            "from_nickname": "admin",
                            "to_nickname": "",
                            "room_name": sendmessage['room_name'],
                            "avatar_url": "9",
                            "bac_num": sendmessage['bac_num'],
                            "content": "出错了1111",
                            "type": "chat_message"
                        }
                        logger.info(admin_return_msg)
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            admin_return_msg,
                        )

            else:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    sendmessage,
                )

        elif sendmessage['msg_type'] == 4:
            zxpaicount = zx_count(sendmessage['content'][0], sendmessage['content'][1])
            sendmessage['content'].append("x")
            sendmessage['content'].append(zxpaicount)
            hkeys = 'h' + sendmessage['room_name'] + sendmessage['bac_num'] + '_' + sendmessage['msg_id']
            r.set(hkeys, json.dumps(sendmessage, ensure_ascii=False))
            r.expire(hkeys, 600)
            road_reuslt = getRoadFromRedis(sendmessage['room_name'], sendmessage['content'][2], sendmessage['bac_num'])
            if road_reuslt is not None:
                road_reuslt['result'] = sendmessage['content']
                sendmessage['content'] = json.dumps(road_reuslt)
                # conent是数组 第一个是 庄闲对的个数， 第二个是当前局的结果， 第三个是当前靴的结果
            await self.channel_layer.group_send(
                self.room_group_name,
                sendmessage,
            )
        else:
            await self.channel_layer.group_send(
                    self.room_group_name,
                    sendmessage,
                )

    async def chat_message(self, event):
        sendmessage = event
        await self.send_json(sendmessage)


class AdminConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print(self.scope)
        if self.scope["user"].username != "" and self.scope["user"].username is not None and self.scope["user"].username != "AnonymousUser":
            self.username = self.scope["user"].username

            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = 'admin_%s' % self.room_name
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            if r.exists("room_secureToken"):
                secureToken = r.get("room_secureToken")
            secureToken_msg = {
                "msg_type": 2,
                "from_username": "admin",
                "secureToken": secureToken,
                "type": "token_message"
            }

            await self.channel_layer.group_send(
                self.room_group_name,
                secureToken_msg,
            )
        elif len(self.scope['query_string']) > 0:
            query_string = self.scope['query_string'].decode()
            auth_username = query_string.split('&')[0].split('=')[1]
            auth_token = query_string.split('&')[1].split('=')[1]
            auth_key = 'JWT' + auth_username
            if r.exists(auth_key):
                if r.get(auth_key) == auth_token:
                    self.username = auth_username
                    self.room_name = self.scope['url_route']['kwargs']['room_name']
                    self.room_group_name = 'admin_%s' % self.room_name
                    await self.channel_layer.group_add(
                        self.room_group_name,
                        self.channel_name
                    )
                    await self.accept()

                    if r.exists("room_secureToken"):
                        secureToken = r.get("room_secureToken")
                        secureToken_msg = {
                            "msg_type": 2,
                            "from_username": "admin",
                            "secureToken": secureToken,
                            "type": "token_message"
                        }

                        await self.channel_layer.group_send(
                            self.room_group_name,
                            secureToken_msg,
                        )
                else:
                    return 1
            else:
                return 1
        else:
            return 1

        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        # self.room_group_name = 'admin_%s' % self.room_name
        # await self.channel_layer.group_add(
        #     self.room_group_name,
        #     self.channel_name
        # )
        # await self.accept()

    async def token_message(self, event):
        print(event)
        message = event
        await self.send_json(message)


    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        text_data_json['type'] = 'chat_message'

        await self.channel_layer.group_send(
                self.room_group_name,
                text_data_json,
            )

    async def chat_message(self, event):

        sendmessage = event
        # await self.send(text_data=json.dumps(sendmessage))
        await self.send_json(sendmessage)