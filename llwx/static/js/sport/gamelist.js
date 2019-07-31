/**
 * Created by apple on 2018/11/29.
 */

var gametype = 1;
var catid = 1;
var lgid = 0;
var ptype = 0; //賠率類別， 0 港，1 馬來，8 歐賠

$(document).ready(function () {

    catid = $.getUrlParam('catid');

    ptype = CP.Cookie.get('ptype');

    gametype = CP.Cookie.get('gametype');

    lgid = $.getUrlParam('lgid');

    getAjaxData();

    $("#sel_sort").change(function () {
        getAjaxData();
    });

    $("#refresh").click(function () {
        getAjaxData();
    });

    ///更多
    $('#div_show').on('click', 'div.bet', function () {
        window.location.href = '/tfball/gamemore/?catid=' + catid + '&lgid=' + lgid + '&evtid=' + $(this).attr('evtid');
    });

    $('#div_show').on('click', 'div.bet120', function () {
        window.location.href = '/tfball/gamelist/?catid=' + catid + '&lgid=' + lgid + '&evtid=' + $(this).attr('evtid') + '&wagerType=120';
        //window.location.href = 'gamelist.aspx?catid=' + catid + '&lgid=' + lgid + '&wagerType=120'
    });

    $('#div_show').on('click', 'div.acc_1', function () {
        $(this).next('div.model_r').slideToggle();
    });

});



///加载远程数据
function getAjaxData() {

    //正在加载
    if ($('#refresh').attr("load")) return;

    $('#re_second').css("background-image", "url(/images/loading1.gif)");
    $('#refresh').attr("load", 1);
    $("#re_second").html('');

    var option = {
        sort: $('#sel_sort').val(),
        catid: catid,
        gametype: gametype,
        lgid: lgid,
        ptype: CP.Cookie.get('ptype')
    };

    var wagerTypeId = 0;
    if (isWagerType120 == 'True')
        wagerTypeId = 120;
    //var url = '/sport/handler/proxy.ashx?cmd=get_game_list&wagerType=' + wagerTypeId;
    var url = '/tfball/gamelist/?cmd=get_game_list&wagerType=' + wagerTypeId;
    $('#div_show').empty();
    $.ajax({
        url: url,
        type: 'POST',
        dataType: 'json',
        data: option,
        cache: false,
        async: true,
        timeout: 60000,
        beforeSend: function () {
        },
        success: function (json) {


            if (json.Result == 1) {

                if (catid == 72) {
                    showJsonData72(json.Data);
                } else {
                    if (isWagerType120 == 'True') {
                        showJsonData120(json.Data);
                    }
                    else {
                        showJsonData(json.Data);
                    }
                }

            }
            else {
                // alert('no data');

            }

            $('#re_second').css("background-image", "url(/images/refresh_icon.png)");
            $('#refresh').attr("load", "");
            $("#re_second").html($("#re_second").attr('title'));

        },
        complete: function (XHR, TS) {
            XHR = null;
        },
        error: function () {

        }
    });
}


function showJsonData120(jsonData) {

    $('#league_name').html(jsonData.LeagueName);
    //$('#a_cateid_120').attr('href', 'leaguelist.aspx?catid=' + catid + '&wagerType=120');
    //$('#a_cateid_120').attr('href', 'gamelist.aspx?catid=' + catid +'&lgid='+lgid+'&wagerType=120');

    $('#a_cateid').attr('href', 'leaguelist.aspx?catid=' + catid);
    $('#a_cateid div').html(jsonData.CateName);

    var json = jsonData.GameList;
    if (json.length == 0) {
        $('#nodata2').show();
        return;
    }
    $('#racetime').html(json[0].RaceTime);

    var div_show = $('#div_show').empty();
    var table_game = $('#table_game').html();

    var tr_team = $('#tr_team120 tbody').html();
    var tr_head = $('#tr_head120 tbody').html();
    var tr_item = $('#tr_item120 tbody').html();

    var table = $(table_game);
    var tbody = table.find('tbody');

    //var trTeam = $(tr_team);
    var trHead = $(tr_head);
    //alert(json);
    for (var i = 0; i < json.length; i++) {

        var reqEvtId = $.getUrlParam('evtid');
        if (reqEvtId != null) {
            var acquEvtId = json[i].AcquEventID;
            if (reqEvtId != acquEvtId) continue;
        }
        var bList = json[i].BList;

        var homeTeam = json[i].HomeTeam;
        var awayTeam = json[i].AwayTeam;

        var tr_team = $('#tr_team120 tbody').html();
        var tr_head = $('#tr_head120 tbody').html();

        var trTeam = $(tr_team);
        var trHead = $(tr_head);

        trTeam.find('[hometeam]').html(homeTeam);
        trTeam.find('[awayteam]').html(awayTeam);

        tbody.append(trTeam);
        tbody.append(trHead);


        //        var spanHomeTeam = trHead.find('[hometeam]');
        //        var spanAwayTeam = trHead.find('[awayteam]');



        //        spanHomeTeam.html(homeTeam);
        //        spanAwayTeam.html(awayTeam);
        //        spanHomeTeam.css('color', 'blue');

        //td1.find('[halftype]').html(_HalfType1);

        var td0List = [];
        var td1List = [];

        for (var n = 0; n < bList.length; n++) {
            if (bList[n].HalfType == "0") {
                td0List.push(bList[n]);
            } else {
                td1List.push(bList[n]);
            }
        }

        var count = td0List.length > td1List.length ? td0List.length : td1List.length;

        for (var n = 0; n < count; n++) {

            var tr = $('<tr class="oddsdetails"></tr>');
            var td0 = $(tr_item).find('td').eq(0);
            var td1 = $(tr_item).find('td').eq(1);

            if (td0List.length > n) {
                td0.attr('gameid', td0List[n].GameId);
                td0.attr('wtype', td0List[n].WagerTypeID);
                td0.attr('evtid', json[i].AcquEventID);

                td0.find('[OULine]').attr('OULine', td0List[n].OULine).html(td0List[n].OULine);
                td0.find('[odds]').attr('odds', td0List[n].HomeHdpOdds).html(td0List[n].HomeHdpOdds + '%');
            } else {
                td0 = $('<td></td>');
            }
            if (td1List.length > n) {
                td1.attr('gameid', td1List[n].GameId);
                td1.attr('wtype', td1List[n].WagerTypeID);
                td1.attr('evtid', json[i].AcquEventID);

                td1.find('[OULine]').attr('OULine', td1List[n].OULine).html(td1List[n].OULine);
                td1.find('[odds]').attr('odds', td1List[n].HomeHdpOdds).html(td1List[n].HomeHdpOdds + '%');
            } else {
                td1 = $('<td></td>');
            }

            tr.append(td0);
            tr.append(td1);

            tbody.append(tr);
        }

        div_show.append(table);
    }

    $('#nodata2').hide();
}


function showJsonData(jsonData) {

    $('#league_name').html(jsonData.LeagueName);
    //$('#a_cateid_120').attr('href', 'leaguelist.aspx?catid=' + catid + '&wagerType=120');
    //$('#a_cateid_120').attr('href', 'gamelist.aspx?catid=' + catid +'&lgid='+lgid+'&wagerType=120');

    $('#a_cateid').attr('href', 'leaguelist.aspx?catid=' + catid);
    $('#a_cateid div').html(jsonData.CateName);

    var json = jsonData.GameList;
    if (json.length == 0) {
        $('#nodata2').show();
        return;
    }

    var div_show = $('#div_show').empty();
    var table_game = $('#table_game').html();

    var tr_head = $('#tr_head tbody').html();
    var tr_home = $('#tr_home tbody').html();
    var tr_away = $('#tr_away tbody').html();
    var tr_more = $('#tr_more tbody').html();
    var tr_more_120 = $('#tr_more_120 tbody').html();

    var table = $(table_game);

    var tbody = table.find('tbody');

    for (var i = 0; i < json.length; i++) {

        var trHead = $(tr_head);

        //滚球显示比分和 比赛进行的时间
        if (gametype == 2) {
            trHead.find('[timestatus]').html(json[i].TeamInfo.ScoreString);
            trHead.find('[racetime]').html(json[i].TimeAct);
            //trHead.find('[timestatus]').html('Live');
        }
        else {
            trHead.find('[racetime]').html(json[i].RaceTime);
            trHead.find('[oddsmid]').html(json[i].OddsMid);
        }

        var trMore = $(tr_more);
        var trMore_120 = $(tr_more_120);
        var evtId = json[i].AcquEventID;
        var gameMore = json[i].MoreCount;
        trMore.find('div[evtid]').attr('evtid', json[i].AcquEventID);
        trMore_120.find('div[evtid]').attr('evtid', json[i].AcquEventID);

        tbody.append(trHead);
        var bList = json[i].BList;

        var homeTeam = json[i].HomeTeam;
        var awayTeam = json[i].AwayTeam;
        if (catid != 83) {
            //homeTeam += _HomeFlag;
        }

        for (var n = 0; n < bList.length; n++) {
            var trHome = $(tr_home);
            var trAway = $(tr_away);

            var spanHomeTeam = trHome.find('[hometeam]');
            var spanAwayTeam = trAway.find('[awayteam]');
            //强队蓝色
            if (!json[i].OddsMid && catid != 83) {
                if (bList[n].Hdppos == '0') {
                    spanHomeTeam.css('color', 'blue');
                }
                else {
                    spanAwayTeam.css('color', 'blue');
                }
            }
            spanHomeTeam.html(homeTeam);
            spanAwayTeam.html(awayTeam);

            //让分
            if (bList[n].GameId && bList[n].GameId != '0') {
                var tdHome1 = trHome.find('td').eq(1);
                var tdAway1 = trAway.find('td').eq(1);

                tdHome1.find('div.con').html(bList[n].HomeHdp);
                tdHome1.find('font.ratio').html(bList[n].HomeHdpOdds);

                tdAway1.find('div.con').html(bList[n].AwayHdp);
                tdAway1.find('font.ratio').html(bList[n].AwayHdpOdds);

                tdHome1.attr('gameid', bList[n].GameId).attr('wtype', bList[n].WagerTypeID).attr('wpos', 1).attr('evtid', evtId);
                tdAway1.attr('gameid', bList[n].GameId).attr('wtype', bList[n].WagerTypeID).attr('wpos', 2).attr('evtid', evtId);
            }

            //大小
            if (bList[n].GameId2 && bList[n].GameId2 != '0') {
                var tdHome2 = trHome.find('td').eq(2);
                var tdAway2 = trAway.find('td').eq(2);
                tdHome2.attr('gameid', bList[n].GameId2).attr('wtype', bList[n].WagerTypeID2).attr('evtid', evtId);
                tdAway2.attr('gameid', bList[n].GameId2).attr('wtype', bList[n].WagerTypeID2).attr('evtid', evtId);

                if (WebStyle == 1 || catid == 1) {   //香港版所有或者 足球 主队在上面
                    tdHome2.attr('wpos', 4);
                    tdAway2.attr('wpos', 5);

                    tdHome2.find('div.con').html(_Over + ' ' + bList[n].OULine);
                    tdHome2.find('font.ratio').html(bList[n].OverOdds);

                    tdAway2.find('div.con').html(_Under);
                    tdAway2.find('font.ratio').html(bList[n].UnderOdds);
                }
                else {
                    tdHome2.attr('wpos', 5);
                    tdAway2.attr('wpos', 4);

                    tdAway2.find('div.con').html(_Over + ' ' + bList[n].OULine);
                    tdAway2.find('font.ratio').html(bList[n].OverOdds);

                    tdHome2.find('div.con').html(_Under);
                    tdHome2.find('font.ratio').html(bList[n].UnderOdds);
                }
            }
            //香港版或者足球 主队在前，其他客队在前
            if (WebStyle == 1 || catid == 1) {
                tbody.append(trHome);
                tbody.append(trAway);
            }
            else {
                tbody.append(trAway);
                tbody.append(trHome);
            }
        }
        tbody.append(trMore);
        if (WebConfigWagerType == '0' && gameMore != '0')
            tbody.append(trMore_120);
    }
    div_show.append(table);

    $('#nodata2').hide();

}
function showJsonData72(jsonData) {

    $('#league_name').html(jsonData.LeagueName);
    //$('#a_cateid_120').attr('href', 'leaguelist.aspx?catid=' + catid + '&wagerType=120');
    //$('#a_cateid_120').attr('href', 'gamelist.aspx?catid=' + catid +'&lgid='+lgid+'&wagerType=120');

    //gamelist.aspx?catid=1&lgid=1258
    $('#a_cateid').attr('href', 'leaguelist.aspx?catid=' + catid);
    $('#a_cateid div').html(jsonData.CateName);

    var json = jsonData.GameList;
    if (json.length == 0) {
        $('#nodata2').show();
        return;
    }

    var div_show = $('#div_show').empty();
    var table_game = $('#table_game').html();

    var tr_head = $('#tr_head72 tbody').html();
    var tr_home = $('#tr_home72 tbody').html();
    var tr_away = $('#tr_away72 tbody').html();
    var tr_more = $('#tr_more72 tbody').html();
    var tr_more_120 = $('#tr_more72_120 tbody').html();

    var table = $(table_game);

    var tbody = table.find('tbody');

    for (var i = 0; i < json.length; i++) {
        var trHead = $(tr_head);

        //滚球显示比分和 比赛进行的时间
        if (gametype == 2) {
            trHead.find('[timestatus]').html(json[i].TeamInfo.ScoreString);
            trHead.find('[racetime]').html(json[i].TimeAct);
            //trHead.find('[timestatus]').html('Live');
        }
        else {
            trHead.find('[racetime]').html(json[i].RaceTime);
            trHead.find('[oddsmid]').html(json[i].OddsMid);
        }

        //lotery set empty
        if (catid == 83) {
            trHead.find('[teamdesc]').html("");
        }

        var trMore = $(tr_more);
        var trMore_120 = $(tr_more_120);
        var evtId = json[i].AcquEventID;
        var gameMore = json[i].MoreCount;
        trMore.find('div[evtid]').attr('evtid', json[i].AcquEventID);
        trMore_120.find('div[evtid]').attr('evtid', json[i].AcquEventID);

        tbody.append(trHead);
        var bList = json[i].BList;

        var homeTeam = json[i].HomeTeam;
        var awayTeam = json[i].AwayTeam;
        if (catid != 83) {
            //homeTeam += _HomeFlag;
        }

        for (var n = 0; n < bList.length; n++) {
            var trHome = $(tr_home);
            var trAway = $(tr_away);

            var spanHomeTeam = trHome.find('[hometeam]');
            var spanAwayTeam = trAway.find('[awayteam]');
            //强队蓝色
            if (!json[i].OddsMid && catid != 83) {
                if (bList[n].Hdppos == '0') {
                    spanHomeTeam.css('color', 'blue');
                }
                else {
                    spanAwayTeam.css('color', 'blue');
                }
            }
            spanHomeTeam.html(homeTeam);
            spanAwayTeam.html(awayTeam);

            //单双
            if (bList[n].GameId && bList[n].GameId != '0') {
                var tdHome1 = trHome.find('td').eq(1);
                var tdAway1 = trAway.find('td').eq(1);

                tdHome1.find('div.con').html(_OEE);
                tdHome1.find('font.ratio').html(bList[n].HomeHdpOdds);

                tdAway1.find('div.con').html(_OEO);
                tdAway1.find('font.ratio').html(bList[n].AwayHdpOdds);

                tdHome1.attr('gameid', bList[n].GameId).attr('wtype', bList[n].WagerTypeID).attr('wpos', 5).attr('evtid', evtId);
                tdAway1.attr('gameid', bList[n].GameId).attr('wtype', bList[n].WagerTypeID).attr('wpos', 4).attr('evtid', evtId);
            }

            //大小
            if (bList[n].GameId2 && bList[n].GameId2 != '0') {
                var tdHome2 = trHome.find('td').eq(2);
                var tdAway2 = trAway.find('td').eq(2);
                tdHome2.attr('gameid', bList[n].GameId2).attr('wtype', bList[n].WagerTypeID2).attr('evtid', evtId);
                tdAway2.attr('gameid', bList[n].GameId2).attr('wtype', bList[n].WagerTypeID2).attr('evtid', evtId);

                if (WebStyle == 1 || catid == 1) {   //香港版所有或者 足球 主队在上面
                    tdHome2.attr('wpos', 4);
                    tdAway2.attr('wpos', 5);

                    tdHome2.find('div.con').html(_Over + ' ' + bList[n].OULine);
                    tdHome2.find('font.ratio').html(bList[n].OverOdds);

                    tdAway2.find('div.con').html(_Under);
                    tdAway2.find('font.ratio').html(bList[n].UnderOdds);
                }
                else {
                    tdHome2.attr('wpos', 5);
                    tdAway2.attr('wpos', 4);

                    tdAway2.find('div.con').html(_Over + ' ' + bList[n].OULine);
                    tdAway2.find('font.ratio').html(bList[n].OverOdds);

                    tdHome2.find('div.con').html(_Under);
                    tdHome2.find('font.ratio').html(bList[n].UnderOdds);
                }
            }
            //香港版或者足球 主队在前，其他客队在前
            if (WebStyle == 1 || catid == 1) {
                tbody.append(trHome);
                tbody.append(trAway);
            }
            else {
                tbody.append(trAway);
                tbody.append(trHome);
            }
        }

        if (catid != 72) {
            tbody.append(trMore);
        }
        if (WebConfigWagerType == '0' && gameMore != '0')
            tbody.append(trMore_120);
    }
    div_show.append(table);

    $('#nodata2').hide();
}

///定时器
var time_gamelist = setInterval(function () {
    if (!$('#refresh').attr("load")) {  //如果没有在加载
        var count = parseInt($("#re_second").html()) - 1;
        $("#re_second").html(count);
        if ($("#re_second").html() == "0") {
            getAjaxData();
        }
    }
}, 1000);

