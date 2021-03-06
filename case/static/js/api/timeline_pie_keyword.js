// Date format
Date.prototype.format = function(format) {
    var o = {
        "M+" : this.getMonth()+1, //month
        "d+" : this.getDate(), //day
        "h+" : this.getHours(), //hour
        "m+" : this.getMinutes(), //minute
        "s+" : this.getSeconds(), //second
        "q+" : Math.floor((this.getMonth()+3)/3), //quarter
        "S" : this.getMilliseconds() //millisecond
    }
    if(/(y+)/.test(format)){
        format=format.replace(RegExp.$1, (this.getFullYear()+"").substr(4 - RegExp.$1.length));
    }
    for(var k in o){
        if(new RegExp("("+ k +")").test(format)){
            format = format.replace(RegExp.$1, RegExp.$1.length==1 ? o[k] : ("00"+ o[k]).substr((""+ o[k]).length));
        }
    }
    return format;
}
// TrendsLine Constructor
function TrendsLine(query, start_ts, end_ts, pointInterval){
    //instance property
    this.query = query;
    this.start_ts = start_ts; // 开始时间戳
    this.end_ts = end_ts; // 终止时间戳
    this.pointInterval = pointInterval; // 图上一点的时间间隔
    this.during = end_ts - start_ts; // 整个时间范围
    this.statusEng2Int = {
        'origin': '1',
        'comment': '2',
        'forward': '3',
        'all': '4',
        'total': '5'
    }
    this.pie_ajax_url = function(query, end_ts, during, emotion){
        return "/propagate/total/?end_ts=" + end_ts + "&style=" + this.statusEng2Int[emotion] +"&during="+ during + "&topic=" + query;
    }
    this.keywords_ajax_url = function(query, end_ts, during, emotion){
        var limit = 50;
        return "/propagate/keywords/?end_ts=" + end_ts + "&topic=" + query + "&during="+ during + "&limit="+ limit + "&style="+ this.statusEng2Int[emotion];
    }
    this.weibos_ajax_url = function(query, end_ts, during, emotion, limit){
        var limit = 50;
        return "/propagate/weibos/?&topic=" + query + "&end_ts=" + end_ts +"&limit="+limit + "&during=" + during + "&style=" + this.statusEng2Int[emotion];
    }
    this.peak_ajax_url = function(data, ts_list, during, emotion){
        return "/propagate/propagatepeak/?lis=" + data.join(',') + "&ts=" + ts_list + '&during=' + during + "&mtype=" + this.statusEng2Int[emotion];
    }
    this.ajax_method = "GET";
    this.call_sync_ajax_request = function(url, method, callback){
        $.ajax({
            url: url,
            type: method,
            dataType: "json",
            async: false,
            success: callback
        })
    }
    this.call_async_ajax_request = function(url, method, callback){
        $.ajax({
            url: url,
            type: method,
            dataType: "json",
            async: true,
            success: callback
        })
    }
    this.pie_title = '类别饼图';
    this.pie_series_title = '各类占比';
    this.pie_div_id = 'pie_div';
    this.keywords_div_id = 'keywords_cloud_div';
    this.weibos_div_id = 'weibo_list';
    this.weibo_more_id = 'more_information';
    this.select_div_id = 'Tableselect';
    this.max_keywords_size = 50; // 和计算相关的50，实际返回10
    this.min_keywords_size = 2;
    this.top_weibos_limit = 50; // 和计算相关的50，实际返回10
    this.range_weibos_data = {};
    this.trend_div_id = 'trend_div_whole';
    this.trend_chart;
    this.names = {
        'origin': '原创',
        'forward': '转发',
        'comment': '评论',
        'total': '全量'
    }
    this.trend_count_obj = {
        'ts': [], // 时间数组
        'count': {},
    };
    for (var name in this.names){
        this.trend_count_obj['count'][name] = [];
    }
}
// instance method, 初始化时获取整个时间段的饼图数据并绘制
TrendsLine.prototype.initPullDrawPie = function(){
    var that = this;
    var names = this.names;
    var ajax_url = this.pie_ajax_url(this.query, this.end_ts, this.during, 'all'); // style = 4;
    this.call_async_ajax_request(ajax_url, this.ajax_method, range_count_callback);
    function range_count_callback(data){
        var data = data['count'];
        var pie_data = [];
        for (var status in data){ // 3 statuses
            var count = data[status];
            pie_data.push({
                value: count,
                name: names[status]
            });
        }
        var legend_data = [];
        for (var name in names){
            if (name != 'total'){ // 3 counts
                legend_data.push(names[name]);
            }
        }
        refreshDrawPie(that, pie_data, legend_data);
    }
}
// instance method, 初始化时获取整个时间范围的关键词云数据并绘制
TrendsLine.prototype.initPullDrawKeywords = function(){
    var that = this;
    var names = this.names;
    var emotion = 'all';
    var ajax_url = this.keywords_ajax_url(this.query, this.end_ts, this.during, emotion); //type = 4
    this.call_async_ajax_request(ajax_url, this.ajax_method, range_keywords_callback);
    function range_keywords_callback(data){
        refreshDrawKeywords(that, data, emotion);
    }
}
// instance method, 初始化时获取关键微博数据
TrendsLine.prototype.initPullWeibos = function(){
    var names = this.names;
    var weibos_data = [];
    var that = this;
    for(name in names){
        var ajax_url = this.weibos_ajax_url(this.query, this.end_ts, this.during, name, this.top_weibos_limit);
        this.call_sync_ajax_request(ajax_url, this.ajax_method, range_weibos_callback);
    }
    function range_weibos_callback(data){
        for(var name in names){
            if(name == 'total'){
                if (name in data){
                    that.range_weibos_data[name] = data[name];
                }
            }
            else{
                var id = that.statusEng2Int[name];
                if(id in data){
                    that.range_weibos_data[name] = data[id];
                }
            }
        }
    }
}
// instance method, 初始化绘制关键微博列表
TrendsLine.prototype.initDrawWeibos = function(){
    var select_name = 'origin';
    var that = this;
    var weibo_num = 10;
    refreshDrawWeibos(that, that.range_weibos_data, select_name, weibo_num);
    bindSentimentTabClick(that, that.range_weibos_data);
}
// instance method, 获取数据并绘制趋势图
TrendsLine.prototype.pullDrawTrend = function(){
    var xAxisTitleText = '时间';
    var yAxisTitleText = '数量';
    var series_data = [{
        name: '原创',
        data: [],
        id: 'origin',
        color: '#11c897',
        marker : {
            enabled : false,
        }
    },{
        name: '转发',
        data: [],
        id: 'forward',
        color: '#fa7256',
        marker : {
            enabled : false,
        }
    },{
        name: '评论',
        data: [],
        id: 'comment',
        color: '#6e87d7',
        marker : {
            enabled : false,
        }
    },{
        name: '全量',
        data: [],
        id: 'total',
        color: '#b172c5',
        marker : {
            enabled : false,
        }
    },{
        name: '拐点-原创',
        type : 'flags',
        data : [],
        cursor: 'pointer',
        onSeries : 'origin',
        shape : 'circlepin',
        width : 2,
        color: '#11c897',
        visible: true, // 默认显示存量
        showInLegend: true
    },{
        name: '拐点-转发',
        type : 'flags',
        data : [],
        cursor: 'pointer',
        onSeries : 'forward',
        shape : 'circlepin',
        width : 2,
        color: '#fa7256',
        visible: true, // 默认显示存量
        showInLegend: true
    },{
        name: '拐点-评论',
        type : 'flags',
        data : [],
        cursor: 'pointer',
        onSeries : 'comment',
        shape : 'circlepin',
        width : 2,
        color: '#6e87d7',
        visible: true, // 默认显示存量
        showInLegend: true
    },{
        name: '拐点-全量',
        type : 'flags',
        data : [],
        cursor: 'pointer',
        onSeries : 'total',
        shape : 'circlepin',
        width : 2,
        color: '#b172c5',
        visible: true, // 默认显示存量
        showInLegend: true
    }
    ];
    var that = this;
    var myChart = display_trend(that, series_data, xAxisTitleText, yAxisTitleText);
    this.trend_chart = myChart;
}
function display_trend(that, series_data, xAxisTitleText, yAxisTitleText){
    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });
    var names = that.names;
    var trend_div_id = that.trend_div_id;
    var chart_obj = $('#' + trend_div_id).highcharts({
        chart: {
            type: 'spline',// line,
            animation: Highcharts.svg, // don't animate in old IE
            style: {
                fontSize: '12px',
                fontFamily: 'Microsoft YaHei'
            },
            events: {
                load: function() {
                    var times_init = 0;
                    var count_series = {};
                    var count_peak_series = {};
                    // var incre_peak_series = {};
                    var idx = 0;
                    for(var name in names){
                        count_series[name] = this.series[idx];
                        count_peak_series[name] = this.series[idx+4];
                        // incre_peak_series[name] = this.series[idx+6];
                        idx += 1;
                    }
                    pull_emotion_count(that, 'total', times_init, count_series, count_peak_series);
                }
            }
        },
        plotOptions:{
            line:{
                events: {
                    legendItemClick: function () {
                    }
                }
            }
        },
        title : {
            text: '走势分析图', // trends_title
            margin: 20,
            style: {
                color: '#666',
                fontWeight: 'bold',
                fontSize: '14px',
                fontFamily: 'Microsoft YaHei'
            }
        },
        // 导出按钮汉化
        lang: {
            printChart: "打印",
            downloadJPEG: "下载JPEG 图片",
            downloadPDF: "下载PDF文档",
            downloadPNG: "下载PNG 图片",
            downloadSVG: "下载SVG 矢量图",
            exportButtonTitle: "导出图片"
        },
        rangeSelector: {
            selected: 4,
            inputEnabled: false,
            buttons: [{
                type: 'week',
                count: 1,
                text: '1w'
            }, {
                type: 'month',
                count: 1,
                text: '1m'
            }, {
                type: 'month',
                count: 3,
                text: '3m'
            }]
        },
        xAxis: {
            title: {
                enabled: true,
                text: xAxisTitleText,
                style: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                }
            },
            type: 'datetime',
            tickPixelInterval: 150
        },
        yAxis: {
            min: 0,
            title: {
                enabled: true,
                text: yAxisTitleText,
                style: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                }
            },
        },
        tooltip: {
            valueDecimals: 2,
            xDateFormat: '%Y-%m-%d %H:%M:%S'
        },
        legend: {
            layout: 'horizontal',
            //verticalAlign: true,
            //floating: true,
            align: 'center',
            verticalAlign: 'bottom',
            x: 0,
            y: -2,
            borderWidth: 1,
            itemStyle: {
                color: '#666',
                fontWeight: 'bold',
                fontSize: '12px',
                fontFamily: 'Microsoft YaHei'
            }
            //enabled: true,
            //itemHiddenStyle: {
                //color: 'white'
                //}
        },
        exporting: {
            enabled: true
        },
        series: series_data
    });
    return chart_obj;
}
function pull_emotion_count(that, emotion_type, times, count_series, count_peak_series){
    var names = that.names;
    var query = that.query;
    var during = that.pointInterval;
    var start_ts = that.start_ts;
    var end_ts = that.end_ts;
    var total_days = (end_ts - start_ts) / during;
    if(times > total_days){
        get_peaks(that, count_peak_series);
        return;
    }
    var ts = start_ts + times * during;
    var ajax_url = "/propagate/total/?end_ts=" + ts + "&style=" + that.statusEng2Int[emotion_type] +"&during="+ during + "&topic=" + query;
    $.ajax({
        url: ajax_url,
        type: "GET",
        dataType:"json",
        success: function(data){
            var isShift = false;
            var total_count = 0;
            var count_obj = {};
            that.trend_count_obj['ts'].push(ts);
            for(var name in names){ //4 keys
                if(name in data['count']){
                    count_obj[name] = data['count'][name];
                }
                else{
                    count_obj[name] = 0;
                }
                var count = count_obj[name];
                if (count == null){
                    count = 0;
                }
                count_series[name].addPoint([ts * 1000, count], true, isShift);
                that.trend_count_obj['count'][name].push([ts * 1000, count]);
            }
            times++;
            pull_emotion_count(that, emotion_type, times, count_series, count_peak_series);
        }
    });
}
function get_peaks(that, series){
    var names = that.names;
    var data_obj = that.trend_count_obj['count'];
    var ts_list = that.trend_count_obj['ts'];
    for (var name in names){
        var select_series = series[name];
        var data_list = data_obj[name];
        call_peak_ajax(that, select_series, data_list, ts_list, name);
    }
}
function call_peak_ajax(that, series, data_list, ts_list, emotion){
    var names = that.names;
    var during = that.pointInterval;
    var data = [];
    for(var i in data_list){
        data.push(data_list[i][1]);
    }
    var min_keywords_size = that.min_keywords_size;
    var max_keywords_size = that.max_keywords_size;
    var ajax_url = that.peak_ajax_url(data, ts_list, during, emotion);
    var pie_title = that.pie_title;
    var pie_series_title = that.pie_series_title;
    var legend_data = [];
    for (var name in names){
        if (name != 'total'){
            legend_data.push(names[name]);
        }
    }
    var pie_div_id = that.pie_div_id;
    that.call_async_ajax_request(ajax_url, that.ajax_method, peak_callback);
    function peak_callback(data){
        if ( data != 'Null Data'){
            var isShift = false;
            var flagClick = function(event){
                var click_ts = this.x / 1000;
                var emotion = this.emotion;
                var title = this.title;
                peakDrawTip(click_ts, emotion, title);
                peakPullDrawKeywords(click_ts, emotion, title);
                peakPullDrawPie(click_ts, emotion, title);
                peakPullDrawWeibos(click_ts, emotion, title);
            }
            for(var i in data){
                var x = data[i]['ts'];
                var title = data[i]['title'];
                series.addPoint({'x': x, 'title': title, 'text': title, 'emotion': emotion, 'events': {'click': flagClick}}, true, isShift);
            }
        }
    }
    function peakDrawTip(click_ts, emotion, title){
        $("#peak_trend_tooltip").empty();
        $("#peak_trend_tooltip").append('<span>当前点击了点' + title + '&nbsp;&nbsp;类别:' + that.names[emotion] + '&nbsp;&nbsp;日期:' + new Date(click_ts * 1000).format("yyyy年MM月dd日 hh:mm:ss") + '</span>');
        $("#peak_cloudpie_tooltip").empty();
        $("#peak_cloudpie_tooltip").append('<span>当前点击了点' + title + '&nbsp;&nbsp;类别:' + that.names[emotion] + '&nbsp;&nbsp;日期:' + new Date(click_ts * 1000).format("yyyy年MM月dd日 hh:mm:ss") + '</span>');
        $("#peak_weibo_tooltip").empty();
        $("#peak_weibo_tooltip").append('<span>当前点击了点' + title + '&nbsp;&nbsp;类别:' + that.names[emotion] + '&nbsp;&nbsp;日期:' + new Date(click_ts * 1000).format("yyyy年MM月dd日 hh:mm:ss") + '</span>');
    }
    function peakPullDrawKeywords(click_ts, emotion, title){
        var ajax_url = that.keywords_ajax_url(that.query, click_ts, that.pointInterval, emotion);
        that.call_async_ajax_request(ajax_url, that.ajax_method, callback);
        function callback(data){
            refreshDrawKeywords(that, data, emotion);
        }
    }
    function peakPullDrawPie(click_ts, emotion, title){
        var emotion = 'all';
        var ajax_url = that.pie_ajax_url(that.query, click_ts, that.pointInterval, emotion);
        that.call_async_ajax_request(ajax_url, that.ajax_method, callback);
        function callback(data){
            var data = data['count'];
            var pie_data = [];
            for (var status in data){
                var count = data[status];
                pie_data.push({
                    value: count,
                    name: names[status]
                })
            }
            refreshDrawPie(that, pie_data, legend_data);
        }
    }
    function peakPullDrawWeibos(click_ts, emotion, title){
        var ajax_url = that.weibos_ajax_url(that.query, click_ts, that.pointInterval, 'all', that.top_weibos_limit);
        that.call_async_ajax_request(ajax_url, that.ajax_method, callback);
        function callback(data){
            var weibo_num = 10;
            refreshWeiboTab(emotion);
            refreshDrawWeibos(that, data, emotion, weibo_num);
            bindSentimentTabClick(that, data);
        }
    }
    function refreshWeiboTab(emotion){
        $("#Tableselect").children("a").each(function() {
            var select_a = $(this);
            var select_a_sentiment = select_a.attr('value');
            if (select_a_sentiment == emotion){
                if(!select_a.hasClass('curr')) {
                    select_a.addClass('curr');
                }
            }
            else{
                if(select_a.hasClass('curr')) {
                    select_a.removeClass('curr');
                }
            }
        });
    }
}
function bindSentimentTabClick(that, data){
    var select_div_id = that.select_div_id;
    var weibo_num = 10;
    $("#"+select_div_id).children("a").unbind();
    $("#"+select_div_id).children("a").click(function() {
        var select_a = $(this);
        var unselect_a = $(this).siblings('a');
        if(!select_a.hasClass('curr')) {
            select_a.addClass('curr');
            unselect_a.removeClass('curr');
            var select_sentiment = select_a.attr('value');
            refreshDrawWeibos(that, data, select_sentiment, weibo_num);
        }
    });
}
function bindmore_weibo(that, weibos_obj, weibo_num){
    var weibo_more_id = that.weibo_more_id;
    var weibo_tab_id = that.select_div_id;
    var data = weibos_obj;
    $("#"+weibo_more_id).unbind();
    $("#"+weibo_more_id).click(function(){
        weibo_num = weibo_num + 10;
        var current_city;
        $("#"+weibo_tab_id).children("a").each(function(){
            var select_a = $(this);
            var select_sentiment;
            if (select_a.hasClass('curr')){
                select_sentiment = select_a.attr('value');
                refreshDrawWeibos(that, data, select_sentiment, weibo_num);
                return false;
            }
        });
    });
}
function refreshDrawWeibos(that, data, select_name, weibo_num){
    // console.log(weibo_num);
    var weibos_obj = data;
    var weibos_div_id = that.weibos_div_id;
    var weibo_more_id = that.weibo_more_id;
    $("#"+weibos_div_id).empty();
    if ($("#"+weibo_more_id).hasClass("more_display")){
        $("#"+weibo_more_id).html('').removeClass("more_display");
        // console.log('remove');
    }
    if (!select_name in weibos_obj){
        $("#"+weibos_div_id).append('<li class="item">关键微博为空！</li>');
        return;
    }
    var data = weibos_obj[select_name];
    var weibo_num = weibo_num;
    if (data.length <= weibo_num){
        weibo_num = data.length;
    }
    else{
        var more_html = '加载更多&gt;&gt;';
        $("#"+weibo_more_id).html(more_html).addClass("more_display");
        bindmore_weibo(that, weibos_obj, weibo_num);
        // console.log('append');
    }
    var html = "";
    html += '<div class="tang-scrollpanel-wrapper" style="height: ' + 71 * weibo_num + 'px;">';
    html += '<div class="tang-scrollpanel-content">';
    html += '<ul id="weibo_ul">';
    for(var i = 0; i < weibo_num; i += 1){
        var emotion = select_name;
        var da = data[i];
        var uid = da['user'];
        var name;
        if ('name' in da){
            name = da['name'];
            if(name == 'unknown'){
                name = '未知';
            }
        }
        else{
            name = '未知';
        }
        var mid = da['_id'];
        var retweeted_mid = da['retweeted_mid'];
        var retweeted_uid = da['retweeted_uid'];
        if (da['geo']){
            var ip = da['geo'];
            var loc = ip;
        }
        else{
            var loc = ip = '未知';
        }
        var text = da['text'];
        if (text.length > 100){
            t = '';
            for(j=0;j<=100;j++){
                t = t + text[j];
            }
            t = t + '...';
            text = t;
        }
        var reposts_count = da['reposts_count'];
        var comments_count = da['comments_count'];
        var timestamp = da['timestamp'];
        var date = timestamp;
        var weibo_link = da['weibo_link'];
        var user_link = 'http://weibo.com/u/' + uid;
        var repost_tree_link = 'http://219.224.135.60:8080/show_graph/' + mid;
        var user_image_link = da['profile_image_url'];
        if (user_image_link == 'unknown'){
            user_image_link = '/static/img/unknown_profile_image.gif';
        }
        html += '<li class="item"><div class="weibo_face"><a target="_blank" href="' + user_link + '">';
        html += '<img src="' + user_image_link + '">';
        html += '</a></div>';
        html += '<div class="weibo_detail">';
        html += '<p>昵称:<a class="undlin" target="_blank" href="' + user_link + '">' + name + '</a>(' + loc + ')&nbsp;&nbsp;发布ip:' + '未知' + '&nbsp;&nbsp;发布内容：&nbsp;&nbsp;' + text + '</p>';;
        html += '<div class="weibo_info">';
        html += '<div class="weibo_pz">';
        html += '<a class="undlin" href="javascript:;" target="_blank">转发数(' + reposts_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
        html += '<a class="undlin" href="javascript:;" target="_blank">评论数(' + comments_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
        html += '<a class="undlin" href="javascript:;" target="_blank">粉丝数(未知)</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
        html += '<a class="undlin" href="javascript:;" target="_blank">关注数(未知)</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
        html += '<a class="undlin" href="javascript:;" target="_blank">微博数(未知)</a></div>';
        html += '<div class="m">';
        html += '<a class="undlin" target="_blank" href="' + weibo_link + '">' + date + '</a>&nbsp;-&nbsp;';
        //html += '<a target="_blank" href="http://weibo.com">新浪微博</a>&nbsp;-&nbsp;';
        html += '<a target="_blank" href="' + weibo_link + '">微博</a>&nbsp;-&nbsp;';
        html += '<a target="_blank" href="' + user_link + '">用户</a>&nbsp;-&nbsp;';
        html += '<a target="_blank" href="' + '#huaxiang' + '">画像</a>&nbsp;-&nbsp;';
        html += '<a target="_blank" href="' + repost_tree_link + '">转发树</a>';
        if(retweeted_mid != '0'){
            var source_repost_tree_link = 'http://219.224.135.60:8080/show_graph/' + retweeted_mid;
            html += '&nbsp;-&nbsp;<a target="_blank" href="' + source_repost_tree_link + '">转发子树</a>';
        }
        html += '</div>';
        html += '</div>';
        html += '</div>';
        html += '</li>';
    }
    html += '</ul>';
    html += '</div>';
    /*
    html += '<div id="TANGRAM_54__slider" class="tang-ui tang-slider tang-slider-vtl" style="height: 100%;">';
    html += '<div id="TANGRAM_56__view" class="tang-view" style="width: 6px;">';
    html += '<div class="tang-content">';
    html += '<div id="TANGRAM_56__inner" class="tang-inner">';
    html += '<div id="TANGRAM_56__process" class="tang-process tang-process-undefined" style="height: 0px;">';
    html += '</div>';
    html += '</div>';
    html += '</div>';
    html += '<a id="TANGRAM_56__knob" href="javascript:;" class="tang-knob" style="top: 0%; left: 0px;"></a>';
    html += '</div>';
    html += '<div class="tang-corner tang-start" id="TANGRAM_54__arrowTop"></div>';
    html += '<div class="tang-corner tang-last" id="TANGRAM_54__arrowBottom"></div>';
    html += '</div>';
    */
    $("#"+weibos_div_id).append(html);
}
// 画关键词云图
function refreshDrawKeywords(that, keywords_data, emotion){
    var min_keywords_size = that.min_keywords_size;
    var max_keywords_size = that.max_keywords_size;
    var keywords_div_id = that.keywords_div_id;
    $("#"+keywords_div_id).empty();
    if (keywords_data == {}){
        $("#"+keywords_div_id).append("<a style='font-size:1ex'>关键词云数据为空</a>");
    }
    else{
        var min_count, max_count = 0, words_count_obj = {};
        for (var keyword in keywords_data){
            // 垃圾过滤
            if(keyword in rubbish_words){
                continue;
            }
            var count = keywords_data[keyword];
            if(count > max_count){
                max_count = count;
            }
            if(!min_count){
                min_count = count;
            }
            if(count < min_count){
                min_count = count;
            }
            words_count_obj[keyword] = count;
        }
        var colors = {
            'all': '#666',
            'origin': '#11c897',
            'forward': '#fa7256',
            'comment': '#6e87d7'
        }
        var color = colors[emotion];
        for(var keyword in words_count_obj){
            var count = words_count_obj[keyword];
            var size = defscale(count, min_count, max_count, min_keywords_size, max_keywords_size);
            $('#'+keywords_div_id).append('<a><font style="color:' + color + '; font-size:' + size + 'px;">' + keyword + '</font></a>');
        }
        on_load(keywords_div_id);
    }
}
// 根据权重决定字体大小
function defscale(count, mincount, maxcount, minsize, maxsize){
    if(maxcount == mincount){
        return (maxsize + minsize) * 1.0 / 2
    }else{
        return minsize + 1.0 * (maxsize - minsize) * Math.pow((count / maxcount), 2)
    }
}
// 绘制饼图方法
function refreshDrawPie(that, pie_data, legend_data) {
    for (var i in pie_data){
        pie_data[i]['name'] += pie_data[i]['value'];
    }
    var pie_title = that.pie_title;
    var pie_series_title = that.pie_series_title;
    var pie_div_id = that.pie_div_id;
    var option = {
        backgroundColor: '#FFF',
        color: ['#11c897', '#fa7256', '#6e87d7', '#b172c5'],
        title : {
            text: pie_title,
            x: 'center',
            textStyle:{
                fontWeight: 'lighter',
                fontSize: 13
            }
        },
        toolbox: {
            show: true,
            feature : {
                mark : {show: true},
                dataView : {show: true, readOnly: false},
                //magicType : {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)",
            textStyle: {
                fontWeight: 'bold',
                fontFamily: 'Microsoft YaHei'
            }
        },
        legend: {
            orient:'vertical',
            x : 'left',
            data: legend_data,
            textStyle: {
                fontWeight: 'bold',
                fontFamily: 'Microsoft YaHei'
            }
        },
        calculable : true,
        series : [
        {
            name: pie_series_title,
            type: 'pie',
            radius : '50%',
            center: ['50%', '60%'],
            /*itemStyle: {
                normal: {
                    label: {
                        position: 'inner',
                        formatter: "{d}%",
                        textStyle: {
                            fontWeight: 'bold',
                            fontFamily: 'Microsoft YaHei'
                        }
                    },
                    labelLine: {
                        show: false
                    }
                },
                emphasis: {
                    label: {
                        show: true,
                        formatter: "{b}\n{d}%",
                        textStyle: {
                            fontWeight: 'bold',
                            fontFamily: 'Microsoft YaHei'
                        }
                    }
                }
            },*/
            data: pie_data
        }
        ],
        textStyle: {
            fontWeight: 'bold',
            fontFamily: 'Microsoft YaHei'
        }
    };
    var myChart = echarts.init(document.getElementById(pie_div_id));
    myChart.setOption(option);
}
tl = new TrendsLine(QUERY, START_TS, END_TS, POINT_INTERVAL);
tl.pullDrawTrend();
tl.initPullDrawPie();
tl.initPullDrawKeywords();
tl.initPullWeibos();
tl.initDrawWeibos();

