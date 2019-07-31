/**
* Created by apple on 2018/12/11.
*/



var startnum = "0ju0xue";
var benxueresult = "";
var websocket003 = new WebSocket(
    "ws://" + window.location.host +
    "/ws/chat/room003/");
websocket003.onmessage = function (e) {
    console.log(e.data);
    var data = JSON.parse(e.data);
    if(data["msg_type"] == 10 || data["msg_type"] == 11){
        alert(data["content"])
    }else{
        var message = data["content"];
        var username = data["from_nickname"];
        document.querySelector("#textarearoom003").innerHTML += ("[" + username + ": ]" + ": " + message + "<br />");
        document.querySelector("#textarearoom003").scrollTop = document.querySelector("#textarearoom003").scrollHeight;
    }

}
websocket003.onclose = function (e) {
    console.error("Chat socket closed unexpectedly");
};

document.querySelector("#room003").onclick = function (e) {
    var messageInputDom003 = document.querySelector("#inroom003");
    var message = messageInputDom003.value;
    var timestamp = Date.parse(new Date());
    var md5value = "admin" + timestamp + ""
    var hash = md5(md5value)
    websocket003.send(JSON.stringify({
        "msg_type": 0,
        "msg_id": hash,
        "from_username": "admin",
        "from_nickname": "admin",
        "to_nickname": "",
        "room_name": "room003",
        "is_group": "true",
        "avatar_url": "9",
        "bac_num": "",
        "content": message
    }));



    messageInputDom003.value = "";
};

document.querySelector("#startroom003").onclick = function (e) {
    expandUrl003();
    $("#startroom003").attr("disabled", true)
}

document.querySelector("#stoproom003").onclick = function (e) {
    //var timestamp = Date.parse(new Date());
    //var md5value = "admin" + timestamp + ""
    //var hash = md5(md5value)
    //websocket003.send(JSON.stringify({
    //    "msg_type": 3,
    //    "msg_id": hash,
    //    "from_username": "admin",
    //    "from_nickname": "admin",
    //    "to_nickname": "",
    //    "room_name": "room003",
    //    "is_group": "true",
    //    "avatar_url": "2",
    //    "image_url": "",
    //    "bac_num": startnum,
    //    "msg_admin": 200,
    //    "content": "停止下注"
    //}));
    stop003();

}
document.querySelector("#showroom003").onclick = function (e) {
    var timestamp = Date.parse(new Date());
    var md5value = "admin" + timestamp + ""
    var hash = md5(md5value)
    websocket003.send(JSON.stringify({
        "msg_type": 3,
        "msg_id": hash,
        "from_username": "admin",
        "from_nickname": "admin",
        "to_nickname": "",
        "room_name": "room003",
        "is_group": "true",
        "avatar_url": "9",
        "image_url": "",
        "bac_num": startnum,
        "msg_admin": 300,
        "content": "确认账单"
    }));
    $("#resultroom003").attr("disabled", false)
}

//document.querySelector("#jiesuanroom003").onclick = function (e) {
//    websocket003.send(JSON.stringify({
//        "msg_type": 3,
//        "msg_id": "12312312398123213",
//        "from_username": "admin",
//        "from_nickname": "admin",
//        "to_nickname": "",
//        "room_name": "room003",
//        "is_group": "true",
//        "avatal_url": "2",
//        "image_url": "https://hear.lelewuxian.com",
//        "bac_num": startnum,
//        "msg_admin": 400,
//        "content": benxueresult
//    }));
//};

document.querySelector("#benxueroom003").onclick = function (e){
    benxueurl003()
};

document.querySelector("#jinriroom003").onclick = function (e){
    jinri003()
};

document.querySelector("#resultroom003").onclick = function(e){
    resutl003()
};



function expandUrl003() {
    const xhr003 = new XMLHttpRequest();
    xhr003.open("GET", "http://13.229.237.142/chat/adminchat/getjunum/?roomnum=room003");
    xhr003.send(null);
    xhr003.onreadystatechange = function () {
        if (xhr003.readyState == 4 && xhr003.status == 200) {
            document.getElementById("spanroom003").innerHTML = xhr003.responseText.replace(/xue/, "靴").replace(/ju/, "局")
            startnum = xhr003.responseText;
            var timestamp = Date.parse(new Date());
            var md5value = "admin" + timestamp + ""
            var hash = md5(md5value)
            websocket003.send(JSON.stringify({
                "msg_type": 3,
                "msg_id": hash,
                "from_username": "admin",
                "from_nickname": "admin",
                "to_nickname": "",
                "room_name": "room003",
                "is_group": "true",
                "avatar_url": "9",
                "image_url": "static/llwx/start70.gif",
                "bac_num": startnum,
                "msg_admin": 100,
                "content": "开始了"
            }));

        }
    }

}

function benxueurl003() {
    const xhr003 = new XMLHttpRequest();
    xhr003.open("GET", "http://13.229.237.142/chat/adminchat/getjunum/?roomnum=room003&benxue=add");
    xhr003.send(null);
    xhr003.onreadystatechange = function () {
        if (xhr003.readyState == 4 && xhr003.status == 200) {
            document.getElementById("spanroom003").innerHTML = xhr003.responseText.replace(/xue/, "靴").replace(/ju/, "局")
            startnum = xhr003.responseText;
            var timestamp = Date.parse(new Date());
            var md5value = "admin" + timestamp + ""
            var hash = md5(md5value)
            websocket003.send(JSON.stringify({
                "msg_type": 0,
                "msg_id": hash,
                "from_username": "admin",
                "from_nickname": "admin",
                "room_name": "room003",
                "is_group": "true",
                "avatar_url": "9",
                "image_url": "",
                "bac_num": startnum,
                "content": "开始新靴"
            }));

        }
    }

}


function jinri003() {
    const xhr003 = new XMLHttpRequest();
    xhr003.open("GET", "http://13.229.237.142/chat/adminchat/getjunum/?roomnum=room003&jinri=over");
    xhr003.send(null);
    xhr003.onreadystatechange = function () {
        if (xhr003.readyState == 4 && xhr003.status == 200) {
            document.getElementById("spanroom003").innerHTML = "本房间今日结束"
            startnum = xhr003.responseText;
            var timestamp = Date.parse(new Date());
            var md5value = "admin" + timestamp + ""
            var hash = md5(md5value)
            websocket003.send(JSON.stringify({
                "msg_type": 0,
                "msg_id": hash,
                "from_username": "admin",
                "from_nickname": "admin",
                "room_name": "room003",
                "is_group": "true",
                "avatar_url": "9",
                "image_url": "",
                "bac_num": "over",
                "content": "本房间今日结束"
            }));

        }
    }

}

function suiji(){
	var str = "bhmf";
	var rand = Math.floor(Math.random() * str.length);
	var s = str.charAt(rand);
	return s
}

function resutl003(){
    //var zhuang = document.getElementById("zresultroom003").value
    //var xian = document.getElementById("xresultroom003").value
    //var whowin = document.getElementById("resultroom003").value
    //var content = new Array()
    //websocket003.send(JSON.stringify({
    //            "msg_type": 4,
    //            "msg_id": "12312312398123213",
    //            "from_username": "admin",
    //            "from_nickname": "admin",
    //            "room_name": "room003",
    //            "is_group": "True",
    //            "avatal_url": "https://hear.lelewuxian.com",
    //            "image_url": "https://hear.lelewuxian.com",
    //            "bac_num": startnum,
    //            "content": content
    //        }));
    //
    //benxueresult = whowin
    var z1 = suiji() + document.querySelector("#z1troom003").value;
    var z2 = suiji() + document.querySelector("#z2troom003").value;
    var z3 = suiji() + document.querySelector("#z3troom003").value;

    var x1 = suiji() + document.querySelector("#x1troom003").value;
    var x2 = suiji() + document.querySelector("#x2troom003").value;
    var x3 = suiji() + document.querySelector("#x3troom003").value;

    var zall = "";
    var xall = "";
    var zxresult = document.querySelector("#zxresultroom003").value;
    var content = new Array();
    if( document.querySelector("#z3troom003").value != "" ){
        zall = z1 + z2 + z3
    }else{
        zall = z1 + z2
    }
    if(document.querySelector("#x3troom003").value != ""){
        xall = x1 + x2 + x3
    }else{
        xall = x1 + x2
    }

    if (document.querySelector("#z1troom003").value == "" || document.querySelector("#z2troom003").value == ""){
        alert("结果不能为空");
        return 0;
    }

    if(document.querySelector("#x1troom003").value == "" || document.querySelector("#x2troom003").value == ""){
        alert("结果不能为空");
        return 0;
    }

    content.push(zall);
    content.push(xall);
    content.push(zxresult);
    var timestamp_1 = Date.parse(new Date());
    var md5value1_1 = "admin" + timestamp_1 + ""
    var hash_1 = md5(md5value1_1)

    websocket003.send(JSON.stringify({
                "msg_type": 4,
                "msg_id": hash_1,
                "from_username": "admin",
                "from_nickname": "admin",
                "room_name": "room003",
                "is_group": "true",
                "avatar_url": "9",
                "image_url": "",
                "bac_num": startnum,
                "content": content
            }));
    var timestamp_2 = Date.parse(new Date());
    var md5value1_2 = "admins" + timestamp_2 + ""
    var hash_2 = md5(md5value1_2)
    websocket003.send(JSON.stringify({
        "msg_type": 3,
        "msg_id": hash_2,
        "from_username": "admin",
        "from_nickname": "admin",
        "to_nickname": "",
        "room_name": "room003",
        "is_group": "true",
        "avatar_url": "9",
        "image_url": "",
        "bac_num": startnum,
        "msg_admin": 400,
        "content": zxresult
    }));

    $("#resultroom003").attr("disabled", true)
    $("#startroom003").attr("disabled", false)
    document.querySelector("#z1troom003").value = "";
    document.querySelector("#z2troom003").value = "";
    document.querySelector("#z3troom003").value = "";
    document.querySelector("#x1troom003").value = "";
    document.querySelector("#x2troom003").value = "";
    document.querySelector("#x3troom003").value = "";
}

function stop003() {
    const xhr003 = new XMLHttpRequest();
    xhr003.open("GET", "http://13.229.237.142/chat/adminchat/getroomjunum/?roomnum=room003");
    xhr003.send(null);
    xhr003.onreadystatechange = function () {
        if (xhr003.readyState == 4 && xhr003.status == 200) {
            startnum = xhr003.responseText;
            var timestamp = Date.parse(new Date());
            var md5value = "admin" + timestamp + ""
            var hash = md5(md5value)
            websocket003.send(JSON.stringify({
                "msg_type": 3,
                "msg_id": hash,
                "from_username": "admin",
                "from_nickname": "admin",
                "to_nickname": "",
                "room_name": "room003",
                "is_group": "true",
                "avatar_url": "9",
                "image_url": "",
                "bac_num": startnum,
                "msg_admin": 200,
                "content": "停止下注"
            }));
        }
    }

}


$("#changeroom003").click(function(){
    $("#myModalLabel").text("更改结果");
    $("#myModal").modal();
    console.log("hkfhsfkj")
    $("#change_submit").click(function(){
        change_result()
    });
})



function change_result(){
    const xhr003 = new XMLHttpRequest();
    var bac_num = document.querySelector("#bac_num").value
    var r_result = document.querySelector("#txt_r").value
    var x_result = document.querySelector("#txt_x").value
    var z_result = document.querySelector("#txt_z").value
    if (bac_num == "" || r_result == "" || x_result == "" || z_result == "" ){
        alert("参数不正确")
        return 1
    }
    xhr003.open("GET", "http://13.229.237.142/bacchange/?bac_num=" + bac_num + "&r_result=" + r_result + "&x_result=" + x_result + "&z_result=" + z_result + "&room_id=room003");
    xhr003.send(null);
    xhr003.onreadystatechange = function () {
        if (xhr003.readyState == 4 && xhr003.status == 200) {
            var return_res = JSON.parse(xhr003.responseText);
            console.log(xhr003.responseText)
            if (return_res.code == 0){
                var timestamp = Date.parse(new Date());
                var md5value = "admin" + timestamp + ""
                var hash = md5(md5value)
                websocket003.send(JSON.stringify({
                    "msg_type": 7,
                    "msg_id": hash,
                    "from_username": "admin",
                    "from_nickname": "admin",
                    "room_name": "room003",
                    "avatar_url": "9",
                    "bac_num": bac_num,
                    "content": return_res.msg
                }));
            }else{
                alert("更改结果出错！")
            }

        }
    }
}


