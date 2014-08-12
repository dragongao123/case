#-*- coding:utf-8 -*-


import json
import time
import datetime
from case.model import *
from case.extensions import db
from case.moodlens import pie as pieModule
import search as searchModule
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect, make_response


mod = Blueprint('case', __name__, url_prefix='/index')

#tag = ['九一八','钓鱼岛','历史',]
comment = ['历史是不能改变的',]
'''
title = ['2012.9.19 新浪微博：九一八 ','2012.9.21 新浪微博：九一八',
    '2012.9.23 新浪微博：九一八 ','2012.9.25 腾讯微博：九一八',
    '2012.9.28 新浪微博：九一八 ','2012.10.1 搜狐微博：九一八',
    '2012.10.19 新浪微博：九一八 ','2012.10.21 腾讯微博：九一八',
    '2012.10.25 搜狐微博：九一八 ',]
content = ['1905年，日本在日俄战争中获胜，通过日俄讲和条约，将中国旅顺、大连等地的租借权和长春－旅顺的铁路及附属设施的财产权利占为己有。此后，日本创立“南满洲铁道株式会社”，并由关东军负责铁路沿线的警备。','明治维新以来，日本一直奉行军事优先的原则，培养了大批职业军人。1921年华盛顿会议后，日本开始大规模裁军。1921年至1930年日本的军费由七亿三千万日元裁减到五亿日元以下，裁减额达40%。',
    '大规模裁军却引起了军人们的强烈不满。不满的军人开始秘密集会，东条英机、冈村宁次、石原莞尔等为主要人物的军人秘密组织天剑党、樱会、一夕会等纷纷成立。”。','九一八事变是由日本蓄意制造并发动的侵华战争，是日本帝国主义侵华的开端。九一八事变也标志着世界反法西斯战争的起点，揭开了第二次世界大战东方战场的序幕。',
    '1928年12月29日，张作霖的继承人张学良突然宣布全东北易帜，接受中华民国国民政府的领导，挫败了日本的阴谋，保住了东北的安全，使中国达到形式上的统一。','1929年底，张学良的东北军为了从苏联手中收回位于中国东北的中东铁路与苏联红军爆发武装冲突，即中东路事件。东北军大败。事后，中苏关系彻底断绝。',
    '1931年6月，日本关东军中村震太郎大尉和曹井杉延太郎在兴安岭索伦一带作军事调查，被中国东北军兴安屯垦公署第三团团副董昆吾发现并扣留，在证据确凿情况下，团长关玉衡下令秘密处决中村震太郎。','1931年9月18日傍晚，日本关东军虎石台独立守备队第2营第3连离开原驻地虎石台兵营，沿南满铁路向南行进。夜22时20分左右中国人尸体放在现场，作为东北军破坏铁路的证据，诬称中国军队破坏铁路并袭击日守备队。',
    '1931年9月18日事变发生当夜，东北边防军司令长官公署中将参谋长荣臻根据张学良之命，命令东北军“不准抵抗，不准动，把枪放到库房里，挺着死，大家成仁，为国牺牲”。','1931年9月20日，中国共产党中央委员会发表《中国共产党为日本帝国主义强暴占领东三省事件宣言》[27]，谴责日军侵略，并提出“武装拥护苏联”的口号。',]
'''

@mod.route('/')
def loading():
    return render_template('index/gl.html')

@mod.route('/detail/')
def detail():
    return render_template('index/detail.html')

@mod.route('/manage/')
def manage():
    return render_template('index/manage.html')

@mod.route('/eva/')
def eva():
    return render_template('index/eva.html')

@mod.route('/moodlens/')
def moodlens():
    return render_template('index/moodlens.html')

@mod.route('/area/')
def area():
    return render_template('index/diyu.html')

@mod.route('/semantic/')
def meaning():
    return render_template('index/yuyi.html')

@mod.route('/time/')
def shijian():
    return render_template('index/shijian.html')

@mod.route('/gaishu/')
def gaishu():
    return render_template('index/gaishu.html')

@mod.route('/zhibiao/')
def zhibiao():
    return render_template('index/zhibiao.html')

@mod.route('/network/')
def topic():
    return render_template('index/topic.html')

# 以下为新增内容
@mod.route('/gaishu/<topic>/')
def gaishu_topic(topic = u'中国'):
    if topic:
        topic = topic.strip()
    tag = '九一八、政府'
    event_time = '2013-09-01'
    event_spot = '北京'
    event_summary = '近年来，日本政府在钓鱼岛问题上不断挑起事端，特别是今年以来姑息纵容右翼势力掀起“购岛”风波，以为自己出面“购岛”铺路搭桥。'
    begin = topic_search('begin', topic)
    end = topic_search('end', topic)
    user_count = topic_search('user_count', topic)
    count = topic_search('count', topic)
    area = topic_search('area',topic)
    key_words = topic_search('key_words',topic)
    opinion = topic_search('opinion',topic)
    moodlens_pie = get_moodlens_pie(topic)

    content = '     标签：' + tag
    content += '\n      ' + topic + '发生于' + event_time + '，事件发生地点为' + event_spot + '。' + event_summary
    content += '\n      该话题的网络讨论起始于' + begin + '，终止于' + end
    content += '，共' + user_count + '人参与讨论，' + '累计讨论' + count + '次。'
    content += '讨论人群集中于' + area + '。'
    content += '\n      话题讨论关键词有：' + key_words + '\n      话题相关的观点列举如下：' + opinion
    content += '\n' + '情绪分布情况为：' + moodlens_pie + '。'
    return content

def get_moodlens_pie(topic = u'中国'):
    end_ts = time.mktime(datetime.datetime(2013,9,1,0,1,0).timetuple())
    during = 10

    results = {}
    results = pieModule.search_topic_pie(end_ts, during, query = topic)

    return json.dumps(results)




def topic_search(item = 'count', topic = u'中国'):

    results = {}

    search_func = getattr(searchModule, 'search_%s' % item, None)

    if search_func:
        results[topic] = search_func(topic)
    else:
        return json.dumps('Search function undefined')

    return json.dumps(results)

# 以下为原有内容

@mod.route("/network_data/", methods=["POST"])
def area_network():
    request_method = request.method
    if request_method == 'POST':
        gexf = None
        form = request.form

        with open("data.txt","r+") as fh:
            data=fh.readline().strip()
            gexf=json.loads(data)

        if not gexf:
            gexf = ''

        response = make_response(gexf)
        response.headers['Content-Type'] = 'text/xml'
        return response

    else:
        abort(404)

@mod.route('/show_tag_data/')
def show_tag():
    return json.dumps({'tag': tag})

@mod.route('/alter_tag/',methods=['GET','POST'])
def alter_tag():
    tagname = request.form['tag']
    if tagname:
        tagname = tagname.strip()
    tag = []
    tag.append(tagname)
    return json.dumps(tag)

@mod.route('/show_comment_data/')
def show_comment():
    return json.dumps({'comment': comment})


@mod.route('/alter_comment/',methods=['GET','POST'])
def alter_comment():
    commentname = request.form['comment']
    if commentname:
        commentname = commentname.strip()
    comment = []
    comment.append(commentname)
    return json.dumps(comment)

@mod.route('/show_lt_data/')
def show_lt_data():
    title = []
    content = []
    title = ['2012.9.19 天涯论坛：九一八事变起因 ','2012.9.21 猫扑：九一八是精心策划的阴谋',
    '2012.9.23 天涯论坛：九一八事变起因 ','2012.9.25 猫扑：九一八是精心策划的阴谋',
    '2012.9.28 天涯论坛：九一八事变起因 ','2012.10.1 猫扑：九一八是精心策划的阴谋',
    '2012.10.19 天涯论坛：九一八事变起因 ','2012.10.21 猫扑：九一八是精心策划的阴谋',
    '2012.10.25 天涯论坛：九一八事变起因 ',]
    content = ['1931年9月18日夜，盘踞在中国东北的日本关东军按照精心策划的阴谋，由铁道“守备队”炸毁沈阳柳条湖附近日本修筑的南满铁路路轨，并栽赃嫁祸于中国军队，（其实就是要找任何一个借口，开始侵略中国）日军就以此为借口，开始“名正言顺”“光明正大”地炮轰沈阳北大营，制造了震惊中外的“九一八事变”。','九一八事变是由日本蓄意制造并发动的侵华战争，是日本帝国主义侵华的开端。九一八事变也标志着世界反法西斯战争的起点，揭开了第二次世界大战东方战场的序幕。',
    '1931年9月18日夜，盘踞在中国东北的日本关东军按照精心策划的阴谋，由铁道“守备队”炸毁沈阳柳条湖附近日本修筑的南满铁路路轨，并栽赃嫁祸于中国军队，（其实就是要找任何一个借口，开始侵略中国）日军就以此为借口，开始“名正言顺”“光明正大”地炮轰沈阳北大营，制造了震惊中外的“九一八事变”。','九一八事变是由日本蓄意制造并发动的侵华战争，是日本帝国主义侵华的开端。九一八事变也标志着世界反法西斯战争的起点，揭开了第二次世界大战东方战场的序幕。',
    '1931年9月18日夜，盘踞在中国东北的日本关东军按照精心策划的阴谋，由铁道“守备队”炸毁沈阳柳条湖附近日本修筑的南满铁路路轨，并栽赃嫁祸于中国军队，（其实就是要找任何一个借口，开始侵略中国）日军就以此为借口，开始“名正言顺”“光明正大”地炮轰沈阳北大营，制造了震惊中外的“九一八事变”。','九一八事变是由日本蓄意制造并发动的侵华战争，是日本帝国主义侵华的开端。九一八事变也标志着世界反法西斯战争的起点，揭开了第二次世界大战东方战场的序幕。',
    '1931年9月18日夜，盘踞在中国东北的日本关东军按照精心策划的阴谋，由铁道“守备队”炸毁沈阳柳条湖附近日本修筑的南满铁路路轨，并栽赃嫁祸于中国军队，（其实就是要找任何一个借口，开始侵略中国）日军就以此为借口，开始“名正言顺”“光明正大”地炮轰沈阳北大营，制造了震惊中外的“九一八事变”。','九一八事变是由日本蓄意制造并发动的侵华战争，是日本帝国主义侵华的开端。九一八事变也标志着世界反法西斯战争的起点，揭开了第二次世界大战东方战场的序幕。',
    '1931年9月18日夜，盘踞在中国东北的日本关东军按照精心策划的阴谋，由铁道“守备队”炸毁沈阳柳条湖附近日本修筑的南满铁路路轨，并栽赃嫁祸于中国军队，（其实就是要找任何一个借口，开始侵略中国）日军就以此为借口，开始“名正言顺”“光明正大”地炮轰沈阳北大营，制造了震惊中外的“九一八事变”。','九一八事变是由日本蓄意制造并发动的侵华战争，是日本帝国主义侵华的开端。九一八事变也标志着世界反法西斯战争的起点，揭开了第二次世界大战东方战场的序幕。',]

    results = {'title': title,'content': content}
    return json.dumps(results)

