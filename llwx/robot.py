#!/usr/bin/python
import sys
import io
import websocket
import json
import time
import redis
from threading import Thread
import pickle
import random
import hashlib
import copy

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


USER = "robot"
JWT = 'JWT' + USER
ROOMLIST = ["room001", "room002", "room003"]
THTREADS = [None for i in range(0, len(ROOMLIST))]
WEBSOCKET_LIST = [None for i in range(0, len(ROOMLIST))]
TIME_SET = [3,5]
TZ = [500,600,800,1000,1200,1500,1800,2000,2500,3000]
TZ_RESULT =["x","z"]


def hashmd5():
    randname = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba1234567890',7))
    md5str = randname + str(time.time())
    md5str = md5str.encode('utf-8')
    hmd5 = hashlib.md5()
    hmd5.update(md5str)
    user_id_md5 = hmd5.hexdigest()
    return user_id_md5

def on_message(ws, message):
    message = json.loads(message)
    if message["msg_type"] == 3:
        if message["msg_admin"] == 100:
            for robot in random.sample(robotuser_list, robot_count):
                content = str(random.sample(TZ_RESULT, 1)[0]) + str(random.sample(TZ, 1)[0])
                mes = {
                    "msg_type": 2,
                    "msg_id": hashmd5(),
                    "from_username": robot["username"],
                    "from_nickname": robot["nickname"],
                    "to_nickname": "",
                    "room_name": message["room_name"],
                    "avatar_url": "2",
                    "bac_num": message["bac_num"],
                    "content": content,
                    "type": "chat_message"
                }
                ws.send(json.dumps(mes, ensure_ascii=False))
                timeint = random.sample(TIME_SET, 1)[0]
                time.sleep(timeint)

    else:
        print("no")


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    print("### connect ###")


def tstart(token, room, username, i):
    url = "ws://127.0.0.1/ws/chat/" + room + "/?username=" + username + "&token=" + token
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url, on_message=on_message, on_open=on_open, on_error=on_error,
                                on_close=on_close)
    WEBSOCKET_LIST[i] = ws
    ws.run_forever()


if __name__ == "__main__":
    r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
    token = r.get(JWT)
    while True:
        robots = r.get("robot_room").split(",")
        newrobots = copy.deepcopy(robots)
        for i in range(0, len(robots)):
            if robots[i] == "0":
                if r.exists("robotuser_list"):
                    robotuser_list = pickle.loads(r.get("robotuser_list"))
                    if len(robotuser_list) > 15:
                        #robot_count = len(robotuser_list) - 2
                        robot_count = 15
                    else:
                        robot_count = len(robotuser_list)
                    THTREADS[i] = Thread(target=tstart, args=(token, ROOMLIST[i], USER, i,),  daemon=True)
                    THTREADS[i].start()
                    newrobots[i] = "2"
            elif robots[i] == "1":
                if isinstance(WEBSOCKET_LIST[i], websocket.WebSocketApp): 
                    WEBSOCKET_LIST[i].close()
                    newrobots[i] = "3"
        newrobots = ",".join(newrobots)
        r.set("robot_room", newrobots)
        time.sleep(10)



