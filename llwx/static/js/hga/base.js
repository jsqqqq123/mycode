/**
 * Created by apple on 2018/12/1.
 */

window.onload = function(){
    showleague();
}

function showleague(){
     $.ajax({
        type: 'POST',
        url: '/tfball/hga/get_league_count/',
        data: {"uid": "eujpg39m20919515l51277", "langx": "zh-cn", "date":"ALL", "sorttype":"league", "ltype":3, "classname": "home"},
        success: function(data){
            showXML(data);
        },
        error: function(){
            console.log("ajax error!")
        }
    })
}


function showXML(sdata){
    var parser = new DOMParser();
    var xmlDoc = parser.parseFromString(sdata, "text/xml");
    var tab = "<table border='1' bordercolor='blue'>"
    var x = xmlDoc.documentElement.childNodes;
    //console.log(x[3].getElementsByTagName('gtype')[0].innerHTML);
    for(i=2; i< x.length; i++){
        var mynodeName = x[i].getElementsByTagName('gtype')[0].innerHTML;
        var mynodeValue = x[i].getElementsByTagName('FT_count')[0].innerHTML;
        tab = tab + "<tr><td class='mytdclass' onclick='mytdClick()' gtype=" + mynodeName + ">" + mynodeName+ "</td>" + "<td>" + mynodeValue + "</td></tr>"
    }
    tab = tab + "</table>";
    $("#showdata").html(tab);

}

//$(".mytdclass").click(function(){
//    showGameList();
//})

function mytdClick(){
    get_LeagueList();
}

function get_LeagueList(){
    $.ajax({
        type: 'POST',
        url: '/tfball/hga/get_league_list/',
        data: {"uid": "eujpg39m20919515l51277","langx":"zh-cn","ltype":"3","gtype":"FT","showtype":"FT","sorttype":"","date":"","isP":""},
        success: function(data){
            showGameList(data);
        },
        error: function(){
            console.log("ajax error!")
        }
    })
}

function showGameList(ddata){
    var parser = new DOMParser();
    var xmlDoc = parser.parseFromString(ddata, "text/xml");
    var tab = "<table border='1' bordercolor='blue'>"
    var myleagueName = new Array();
    var myleagueCount = new Array();
    var myleagueId = new Array();
    //var x = xmlDoc.documentElement.childNodes;
    //console.log(x[3].getElementsByTagName('gtype')[0].innerHTML);
    //var x = xmlDoc.getElementById('FT')
    //for(i=2; i< x.length; i++){
    //    var mynodeName = x[i].getElementsByTagName('gtype')[0].innerHTML;
    //    var mynodeValue = x[i].getElementsByTagName('FT_count')[0].innerHTML;
    //    tab = tab + "<tr><td class='mytdclass' onclick='mytdClick()' gtype=" + mynodeName + ">" + mynodeName+ "</td>" + "<td>" + mynodeValue + "</td></tr>"
    //}
    //tab = tab + "</table>";
    //$("#showdata").html(x[0].localName);
    myleagueName = xmlDoc.getElementsByTagName('league_name')
    myleagueCount = xmlDoc.getElementsByTagName('game_count')
    myleagueId = xmlDoc.getElementsByTagName('league_id')
    var mygtype = xmlDoc.getElementsByTagName('gtype')[0].innerHTML
    console.log(myleagueName[0].innerHTML)
    for (i=0; i< myleagueId.length; i++){
        tab += "<tr><td lid=li" +myleagueId[i].innerHTML +" gtype=" + mygtype + ">" + myleagueName[i].innerHTML + "</td><td>" + myleagueCount[i].innerHTML + "</td></tr>"
    }
    tab += "</table>"

    $('#showdata').html(tab)
}