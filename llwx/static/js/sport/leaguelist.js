/**
 * Created by apple on 2018/11/29.
 */
var gametype = 1;

var catid = 1;

$(document).ready(function () {

    catid = $.getUrlParam('catid');
    wagerType = $.getUrlParam('wagerType');
    //gametype = getGameType();

    getAjaxData();

    $('#div_show').on('click', 'div[lgid]', function () {
        var cateId = $(this).attr('catid');
        var url = '/tfball/gamelist/?catid=' + cateId + '&lgid=' + $(this).attr('lgid');
        if (wagerType != '' && wagerType != null)
            url += '&wagerType=' + wagerType;
        window.location.href = url;
    });

    var sort = CP.Cookie.get('m.sort');
    if (sort) {
        $("#sel_sort").val(sort);
    }

    $("#sel_sort").change(function () {
        CP.Cookie.set('m.sort', $(this).val(), null, null, 9999);
        getAjaxData();
    });

    $("#refresh").click(function () {
        getAjaxData();
    });

    $("#header_back").click(function () {
        window.location.href = 'index.aspx';
    });

});



///加载远程数据
function getAjaxData( ) {
    //正在加载
    if ($('#refresh').attr("load")) return;

    $('#re_second').css("background-image", "url(/static/css/images/loading1.gif)");
    $('#refresh').attr("load", 1);
    $("#re_second").html('');
    $('#div_show').empty();
    var option = {
            sort: $('#sel_sort').val(),
            catid : catid,
            gametype: gametype,
            ptype :  0    // 0 台湾盘，1非台湾盘
        };
    var url = '/tfball/leaguelist/';
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
            showJsonData(json.Data);

            $('#re_second').css("background-image", "url(/static/css/images/refresh_icon.png)");
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

function showJsonData(json) {

    var div_show = $('#div_show').empty();
    if (json.length == 0) {
        div_show.append($('#div_nodata').html());
        return;
    }

    var div_model = $('#div_model').html();
    for (var i = 0; i < json.length; i++) {
        var div = $(div_model);
        div.attr("lgid", json[i].LeagueID).attr("id", 'lg_' + json[i].LeagueID).attr('catid', json[i].CatID);
        div.find("[lgname]").html(json[i].LeagueName);
        div.find("[TGames]").html(json[i].TGames);
        div_show.append(div);
    }
}

///定时器
var timeleague = setInterval(function () {
    if (!$('#refresh').attr("load")) {  //如果没有在加载
        var count = parseInt($("#re_second").html()) - 1;
        $("#re_second").html(count);
        if ($("#re_second").html() == "0") {
            getAjaxData();
        }
    }
}, 1000);