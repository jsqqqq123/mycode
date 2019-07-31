import requests
import json
import redis
import time
from websocket import create_connection
r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True, db=0)
token_key = "room_token"
sec_token = "room_secureToken"

admin_msg = {
                    "msg_type": 2,
                    "msg_id": hash,
                    "from_username": "admin",
                    "secureToken": ""
                }

def websocket_admin(message):
    # message = json.dumps(message)
    ws = create_connection("ws://127.0.0.1/ws/admin/admin/")
    ws.send(message)
    ws.close()


if __name__ == "__main__":
    ulimit = 5
    loginurl = "http://154.92.9.18:5001/api/users/login?username=123456&password=123456"
    for i in range(0, ulimit):
        res = requests.get(loginurl)
        res = json.loads(res.text)
        if res['error'] == False:
            token = res['token']
            secureToken = res['secureToken']
            try:
                r.set(token_key, token)
                r.set(sec_token, secureToken)
                admin_msg["secureToken"] = secureToken
                websocket_admin(admin_msg)
                break
            except:
                time.sleep(10)
                continue
        else:
            time.sleep(10)
            continue
        
