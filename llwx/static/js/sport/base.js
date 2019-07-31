/**
 * Created by apple on 2018/11/29.
 */
$(document).ready(function () {

    ///设置多语言
    $('*[cul]').each(function (i, item) {
        var langValue = eval($(item).attr('cul'));
        $(item).text(langValue);
    });

    //checkOnLine();

    var ptype = getPType();
    $('#sel_ptype').val(ptype);

    $('#sel_ptype').change(function () {
        CP.Cookie.set('ptype', $(this).val(), null, null, 9999);
        if (typeof (getAjaxData) == "function") {
            getAjaxData();
        }
    });

    $('#sel_Lang').change(function () {
        CP.Cookie.set('m.CultureLanguage', $(this).val(), null, null, 9999);
        window.location.href = window.location.href;
    });

    var lang = CP.Cookie.get('m.CultureLanguage');
    if (lang) {
        $('#sel_Lang').val(lang);
    }

    var gameType = getGameType();
    swtichHeadClass(gameType);

    $('div[id*=gametype_]').click(function () {
        gametype = $(this).attr('gametype');
        CP.Cookie.set('gametype', gametype, null, null, 9999);
        //返回主页
        window.location.href = 'index.aspx';
    });


    ///原来是否隐藏
    var headIsShow = CP.Cookie.get('m.headIsShow');
    if (headIsShow == "1") {
        $("#header_movie").show();
    }

    ///菜单显示或者隐藏
    $("#header_menu").click(function () {
        $("#header_movie").toggle();
        if ($("#header_movie").is(':visible')) {
            CP.Cookie.set('m.headIsShow', "1", null, null, 9999);
        }
        else {
            CP.Cookie.set('m.headIsShow', "0", null, null, 9999);
        }
    });

    ///返回按钮
    $("#header_back").click(function () {
        if ($.getUrlParam('wagerType') == "120")
            history.back();
        else
            window.location.href = 'index.aspx';
    });
    //是否查看公告
    var isViewAds = CP.Cookie.get('isViewAds');
    if (isViewAds == 1) {
        $("#msg_count").removeClass("msg_count");
    }

    $('#go-desktop').click(function () {
        //window.location.href = 'http://' + window.location.host.replace("m.", "").replace("M.", "");
        window.location.href = 'http://' + window.location.host.replace(window.location.host.split('.')[0] + '.', 'w3.')
        + '/lottery/user/autologin.aspx?from=pc&lang='+ $('#sel_Lang').val( );
    });

});

///设置今日早餐滚球的样式
function swtichHeadClass(gtype) {
    $('div[id*=gametype_]').removeClass().addClass('header_inplay2');
    $('#gametype_' + gtype).removeClass().addClass('header_inplay2_selected');
}

/**
* @namespace url 参数操作
* @name 参数名
*/
(function ($) {
    $.getUrlParam = function (name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
        //       var reg = new RegExp("(^|)" + name + "=([^&]*)(|$)");
        var r = window.location.search.substr(1).match(reg);
        if (r != null) {
            return unescape(r[2]);
        }
        return null;
    };

    $.setUrlParam = function (url, name, value) {
        var reg = new RegExp("(^|)" + name + "=([^&]*)(|$)");
        var tmp = name + "=" + value;
        //var url = window.location.href;
        if (url.match(reg) != null) {
            return url.replace(eval(reg), tmp);
        } else {
            if (url.match("[\?]")) {
                return url + "&" + tmp;
            } else {
                return url + "?" + tmp;
            }
        }
    };
})(jQuery);



function getGameType() {
    var gtype = CP.Cookie.get('gametype');
    if (gtype) return gtype;
    else {
        return 1;
    }
}

function getPType() {
    var ptype = CP.Cookie.get('ptype');
    if (ptype) return ptype;
    else {
        return 0;
    }
}


function checkOnLine () {
    $.ajax({
        url: '/sport/handler/checkonline.ashx',
        type: 'POST',
        dataType: 'json',
        cache: false,
        async: true,
        timeout: 10000,
        success: function (json) {
            if (json.Result == 0) {              // 已登录被迫下线
                alert(json.Msg);
                window.location.href = "/sport/user/logout.aspx";
            }
        },
        complete: function (XHR, TS) { XHR = null; },
        error: function () {
        }
    });
}




var CP = {};

/**
* @namespace Cookie类
* @name Cookie
* @memberOf CP
*/
CP.Cookie = {
    /**
    * @description 设置cookie
    * @author jeking、classyuan
    * @param {String} name 名称
    * @param {String} value 值
    * @param {String} [domain:tenpay.com] 域
    * @param {String} [path:/] 路径
    * @param {String} [hour] 小时
    * @example CP.Cookie.set('cp_pagetype', 'page', 'tenpay.com');
    * @memberOf CP.Cookie
    */
    set: function (name, value, domain, path, hour) {
        var dname = thisDomain + '.' + name;

        var date = new Date();
        date.setTime(date.getTime() + (hour * 60 * 60 * 1000));
        var expires = "; expires=" + date.toGMTString();
        document.cookie = dname + "=" + value + expires + "; path=/ " + "; domain=" + thisDomain;
    },
    /**
    * @description 设置cookie
    * @author jeking、classyuan
    * @param {String} name 名称
    * @example CP.Cookie.get('cp_pagetype'); "page"
    * @memberOf CP.Cookie
    */
    get: function (name) {
        var dname = thisDomain + '.' + name;
        var nameEQ = dname + "=";
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
        }
        return "";
    },
    /**
    * @description 删除cookie
    * @param {String} name 名称
    * @param {String} [domain:tenpay_com] 域
    * @param {String} [path:/] 路径
    * @example CP.Cookie.del('cp_pagetype');
    * @memberOf CP.Cookie
    */
    del: function (name, domain, path) {
        var dname = thisDomain + '.' + name;

        CP.Cookie.set(dname, '', null, null, -1);
    }
};


function FloatAdd(arg1, arg2) {
    var r1, r2, m;
    try { r1 = arg1.toString().split(".")[1].length; } catch (e) { r1 = 0; }
    try { r2 = arg2.toString().split(".")[1].length; } catch (e) { r2 = 0; }
    m = Math.pow(10, Math.max(r1, r2));
    return (FloatMul(arg1, m) + FloatMul(arg2, m)) / m;
}
//浮點數相減
function FloatSubtraction(arg1, arg2) {
    var r1, r2, m, n;
    try { r1 = arg1.toString().split(".")[1].length } catch (e) { r1 = 0 }
    try { r2 = arg2.toString().split(".")[1].length } catch (e) { r2 = 0 }
    m = Math.pow(10, Math.max(r1, r2));
    n = (r1 >= r2) ? r1 : r2;
    return ((arg1 * m - arg2 * m) / m).toFixed(n);
}
//浮點數相乘
function FloatMul(arg1, arg2) {
    var m = 0, s1 = arg1.toString(), s2 = arg2.toString();
    try { m += s1.split(".")[1].length; } catch (e) { }
    try { m += s2.split(".")[1].length; } catch (e) { }
    return Number(s1.replace(".", "")) * Number(s2.replace(".", "")) / Math.pow(10, m);
}
//浮點數相除
function FloatDiv(arg1, arg2) {
    var t1 = 0, t2 = 0, r1, r2;
    try { t1 = arg1.toString().split(".")[1].length } catch (e) { }
    try { t2 = arg2.toString().split(".")[1].length } catch (e) { }
    with (Math) {
        r1 = Number(arg1.toString().replace(".", ""))
        r2 = Number(arg2.toString().replace(".", ""))
        return (r1 / r2) * pow(10, t2 - t1);
    }
}

function alert(msg) {
    var d = dialog({
        content: msg
    });
    d.show();
    setTimeout(function () {
        d.close().remove();
    }, 3000);

};