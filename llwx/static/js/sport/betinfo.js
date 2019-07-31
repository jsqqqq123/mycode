/**
 * Created by apple on 2018/11/29.
 */


var BetData = {
    maxWin: 1000000,
    wgid: 0,
    wtype: 0,
    evtid: 0,
    gameid: 0,
    wpos: 0,
    winOdds: 0
};

$(document).ready(function () {

    $('#txt_Amount').keyup(function () {
        //alert($(this).val());
        var money = $(this).val();
        var partten = /^[0-9]*$/;
        var result = partten.test(money);
        if (!result)
            $(this).val('');

        if (isNaN(money)) return;
        if (money <= 0) money = 0;
        calWinMoney(money);

        hideBetMsg();

    }).blur(function () {
        calWinMoney($(this).val());
        hideBetMsg();
    });


    $('#txt_Amount').keydown(function (e) {
        if (e.keyCode == 13) {
            //$(this).blur();
            postOrder();
            return false;
        }
    });


    $('#finish_continue').click(function () {

        clearInterval(time_binfo);
        time_binfo = null;
        closebet();
    });


    ///点击赔率投注，定时刷新投注信息
    $('#div_show').on('click', 'td.odds_box,div.more_box', function () {

        var gameId = $(this).attr('gameid');
        if (gameId == '0') {
            return false;
        }

        BetData.gameid = gameId;
        BetData.wtype = $(this).attr('wtype');

        if ($(this).attr('evtid')) {
            BetData.evtid = $(this).attr('evtid');
        }
        else {
            BetData.evtid = evtid;
        }

        BetData.wpos = $(this).attr('wpos');

        showBetInfo();

        time_binfo = setInterval('refreshBetInfo()', 1000);
    });


    $('#order_reload_btn').click(function () {
        showBetInfo();
    });

    $('#btn_bet').click(function () {
        postOrder(); //提交表单
    });


    $('#order_close').click(function (e) {

        clearInterval(time_binfo);

        time_binfo = null;

        closebet();
    });


});

///计算可以赢
function calWinMoney(money) {
    $('#div_WinMoney').html('');
    money = Number(money);
    var odds = Number(BetData.winOdds);

    var wtype120 = false;
    if (isWagerType120 && isWagerType120 == 'True') {
        wtype120 = true;
    }

    ///波膽
    if (wtype120) {
        money = FloatSubtraction(money, FloatMul(money, 0.05));
    }

    if (odds > 0) {
        var win = FloatMul(money, odds);

        win = Math.min(BetData.maxWin, win);
    }
    else {
        win = Math.min(BetData.maxWin, money);
    }
    win = Math.floor(win * 100) / 100;
    $('#div_WinMoney').html(win);
}



///加载json档数据 顯示交易單
function showBetInfo() {

    //正在加载
    if ($('#order_reload_btn').attr("load")) return;

    $('#div_bet').show();
    $('#div_bet_order').show();
    $('#txt_Amount').focus();

    $('#order_reload_btn').attr("load", 1);

    $('#order_reload_btn').css("background-image", "url(/images/loading1.gif)");
    $('#order_reload_btn').css("background-position", "center");
    //$("#order_reload_sec").html('');
    $("#order_reload_sec").hide();

		// appMode Hide it
	$('#bMax').hide();
	$('#span_Max').hide();
	$('#betterOdds').hide();

    var option = {
        sort: $('#sel_sort').val(),
        catid: catid,
        lgid: lgid,
        evtid: BetData.evtid,
        gametype: gametype,
        gameid: BetData.gameid,
        ptype: getPType(),
        wpos: BetData.wpos,
        curr: Currency
    };
    //var url = '/sport/handler/proxy.ashx?cmd=get_game_binfo&wagerType=' + $.getUrlParam('wagerType'); ;
    var url = '/tfball/gamelist/?cmd=get_game_binfo&wagerType=' + $.getUrlParam('wagerType');
    clearBetInfo();
    $.ajax({
        url: url,
        type: 'POST',
        dataType: 'json',
        data: option,
        cache: false,
        async: true,
        timeout: 20000,
        beforeSend: function () {
        },
        success: function (json) {
            if (json.Result == 1) {
                showBetData(json.Data);
                $('#order_reload_sec').css("background-image", "url(/images/bet_refresh.png)");
                $("#order_reload_sec").html($("#order_reload_sec").attr('title'));
                $('#order_reload_btn').attr("load", "");
            } else {
                alert('赛事已关闭 请刷新界面!');
                $('#order_close').click();
            }

        },
        complete: function (XHR, TS) {
            XHR = null;
        },
        error: function () {

        }
    });


    var url = '/sport/handler/balance.ashx';
    $.ajax({
        url: url,
        type: 'POST',
        dataType: 'text',
        data: {},
        cache: false,
        async: true,
        timeout: 10000,
        beforeSend: function () {
        },
        success: function (json) {
            $('#order_credit').text = json;
        },
        complete: function (XHR, TS) {
            XHR = null;
        },
        error: function () {

        }
    });
}

function showBetData(jsonData) {

    $('#order_menutype').html(jsonData.CateName + '/' + jsonData.WTypeName);
    $('#order_league').html($('#league_name').html());

    BetData.wgid = jsonData.WGrpId;
    BetData.maxWin = jsonData.MaxWin;
    BetData.winOdds = jsonData.WinOdds;
    BetData.wtype = jsonData.WType;

    $('#team1').html(jsonData.TeamInfo.Team1);
    $('#team2').html(jsonData.TeamInfo.Team2);

    $('#order_con').html(jsonData.VS);
    $('#order_chose_team').html(jsonData.BetTeam);

    $('#div_odds').html(jsonData.ShowOdds);

    $('#span_Min').html(jsonData.BetMin);
    $('#span_Max').html(jsonData.BetMax);

    $('#order_credit').html(jsonData.CreditSport);

    if (gametype == 2) {  //滚球显示比分
        $('#score1').html(jsonData.TeamInfo.StrScore1);
        $('#score2').html(jsonData.TeamInfo.StrScore2);
    }
    $('#hd_betOdds').html(jsonData.CreditSport);

    var ptype = getPType();

    var wgerStr = [BetData.gameid, BetData.wtype, BetData.wpos, jsonData.Hdppos, jsonData.WcfHdp, jsonData.BetOdds, ptype];

    $('#hd_WagerString').val(wgerStr.join());

    $('#txt_Amount').change();

    $('#btn_bet').show();
    $("#order_reload_sec").show();
    $("#order_reload_btn").show();

}


function clearBetInfo() {
    $('#order_menutype').html("");

    BetData.wgid = 0;
    BetData.hdppos = 0;
    BetData.maxWin = 0;
    BetData.winOdds = '0';

    $('#order_team_h').html('');
    $('#order_team_c').html('');

    $('#order_con').html('');
    $('#order_chose_team').html('');
    $('#div_odds').html('');

    $('#span_Min').html('');
    $('#span_Max').html('');
    $('#order_score').html('');

    $('#txt_Amount').val('');
    $('#div_WinMoney').html('');

}


function validateAmount() {
    var money = $('#txt_Amount').val()
    if (isNaN(money) || money <= 0) {
        showBetMsg(_BetAmountErr);
        return false;
    }
    var max = Number($('#span_Max').html());
    var min = Number($('#span_Min').html());

    if (money > max) {
        showBetMsg(_BeyondMax);
        return false;
    }
    if (money < min) {
        showBetMsg(_NotEnoughMin);
        return false;
    }
    return true;
}


var isBetting = false;
function postOrder() {
    if (isBetting) {
        //alert('please waitting...');
        return;
    }

    if (!validateAmount()) {
        return;
    }

    $("#order_reload_sec").html("90");
    var ckAccept = $('#b1_Accept').prop('checked');
    var isAccept = ckAccept ? 0 : 1;

    var formData = {
        isAccept: isAccept,
        catid: catid,
        wtype: BetData.wtype,
        wgid: BetData.wgid,
        amount: $('#txt_Amount').val(),
        wagerString: $('#hd_WagerString').val()
    };

    //when betting hidden this dom
    $("#order_reload_sec").hide();
    $("#order_reload_btn").hide();
    $('#btn_bet').hide();
    hideBetMsg();

    $('#div_bet_order').mask(_BetLoading + '......');

    $('#txt_Amount').attr('readonly', 'readonly');
    isBetting = true;
    $.ajax({
        url: '/sport/handler/bet.ashx',
        type: 'POST',
        dataType: 'html',
        cache: false,
        async: true,
        timeout: 60000,
        processData: true,
        data: formData,
        beforeSend: function () {
            hideBetMsg();
        },
        success: function (xml) {
            $('#div_bet_order').unmask();
            if (xml == '') {
                // 发生错误
                showBetMsg(_BetError);
            }
            else {
                var status = xml.split(',')[0];
                var msg = xml.split(',')[1];
                var orderno = xml.split(',')[2];
                var dtime = xml.split(',')[3].substring(0, 11);

                if (status == -2013) {  //赔率已改變, 是否繼續投注?
                    $('#div_bet_order').show();
                }
                else if (status != 1000) {
                    showBetMsg(msg);
                }
                else {
                    $('#orderno').html(orderno);
                    $('#finish_main').html($('#ord_main').html());
                    $('#finish_gold').html($('#txt_Amount').val());
                    $('#finish_win_gold').html($('#div_WinMoney').html());
                    $('#WaitingInfo').show();
                    $('#div_finish').show();
                    $('#div_finish_order').show();
                    //debugger;
                    //滾球時顯示等待訊息
				   //soccer滾球時顯示等待訊息
                    if (gametype == 2 && catid == 1) {
                        $('#div_finish1').hide();
                        $('#div_finish2').show();
                    }
                    else {
                        $('#div_finish2').hide();
                        $('#div_finish1').show();

                    }


                }
            }
        },
        complete: function (XHR, TS) {
            isBetting = false;
            $('#div_bet_order').unmask();
            $('#txt_Amount').removeAttr('readonly');
            XHR = null;
        },
        error: function () {
            //alert(_BetTimeOut);
            showBetMsg(_BetTimeOut);

        }
    });
}

function showBetMsg(msg) {
    $('#btn_bet').show();
    $('#div_error').show();
    $('#error_msg').html(msg);
}

function hideBetMsg() {
    $('#div_error').hide();
    $('#error_msg').html('');
}

function closebet() {

    $('#div_finish').hide();
    $('#div_finish_order').hide();
    $('#div_bet').hide();
    $('#div_bet_order').hide();

    $("#order_reload_sec").html("90");
    hideBetMsg();
}

function refreshBetInfo() {
    if (!$('#order_reload_btn').attr("load")) {  //如果没有在加载
        var count = parseInt($("#order_reload_sec").html()) - 1;
        $("#order_reload_sec").html(count);
        if ($("#order_reload_sec").html() == "0") {
            showBetInfo();
        }
    }
}
