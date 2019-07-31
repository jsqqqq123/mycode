/**
 * Created by apple on 2018/12/31.
 */

var adminsocket = new WebSocket(
    "ws://" + window.location.host +
    "/ws/admin/admin/");

//adminsocket.onmessage = function (e) {
//    console.log(e.data);
//    var data = JSON.parse(e.data);
//    var message = data["content"];
//    var username = data["from_nickname"];
//    document.querySelector("#textarearoom001").innerHTML += ("[" + username + ": ]" + ": " + message + "<br />");
//    document.querySelector("#textarearoom001").scrollTop = document.querySelector("#textarearoom001").scrollHeight;
//}
adminsocket.onclose = function (e) {
    console.error("Chat socket closed unexpectedly");
};

document.querySelector("#forbbiden").onclick = function(e){
    var username = document.querySelector("#admintext").value
    var timestamp = Date.parse(new Date());
    var md5value = "admin" + timestamp + ""
    var hash = md5(md5value)
    adminsocket.send(JSON.stringify({
        "msg_type": 0,
        "msg_id": hash,
        "from_username": "admin",
        "user_bev": 0,
        "to_username": username,
        "content": "您已被禁言,请联系管理员"
    }));
    document.querySelector("#admintext").value = ""
};

document.querySelector("#nologgin").onclick = function(e){
    var username = document.querySelector("#admintext").value
    var timestamp = Date.parse(new Date());
    var md5value = "admin" + timestamp + ""
    var hash = md5(md5value)
    adminsocket.send(JSON.stringify({
        "msg_type": 0,
        "msg_id": hash,
        "from_username": "admin",
        "user_bev": 1,
        "to_username": username,
        "content": "您已被禁止登陆,请联系管理员"
    }));
    document.querySelector("#admintext").value = ""
};