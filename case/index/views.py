#-*- coding:utf-8 -*-


import json
import time
import datetime
from case.model import *
from case.extensions import db
from case.moodlens import pie as pieModule
from case.identify import utils as identifyModule
import search as searchModule
from case.time_utils import ts2datetime, ts2date
from xapian_case.xapian_backend import XapianSearch
from case.dynamic_xapian_weibo import getXapianWeiboByTopic
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect, make_response


mod = Blueprint('case', __name__, url_prefix='/index')

xapian_search_weibo = getXapianWeiboByTopic()

def acquire_user_by_id(uid):
    XAPIAN_USER_DATA_PATH = '/home/ubuntu3/huxiaoqian/case_test/data/user-datapath/'
    user_search = XapianSearch(path=XAPIAN_USER_DATA_PATH, name='master_timeline_user', schema_version=1)
    result = user_search.search_by_id(int(uid), fields=['name', 'location', 'followers_count', 'friends_count', 'profile_image_url'])
    user = {}

    if result:
        user['name'] = result['name']
        user['location'] = result['location']
        user['followers_count'] = result['followers_count']
        user['friends_count'] = result['friends_count']
        user['profile_image_url'] = result['profile_image_url']
    else:
        return None
    
    return user

comment = ['历史是不能改变的',]

def get_default_timerange():
    return u'20150123-20150203'

def get_default_topic():
    return u'张灵甫遗骨疑似被埋羊圈'

def get_default_pointInterval():
    return {'zh': u'1天', 'en': 3600 * 24}

def get_pointIntervals():
    return [{'zh': u'15分钟', 'en': 900}, {'zh': u'1小时', 'en': 3600}, {'zh': u'1天', 'en': 3600 * 24}]

def get_gaishu_yaosus():
    return {'yaosu': (('gaishu', u'概述分析'), ('zhibiao', u'指标分析'))}

def get_deep_yaosus():
    return {'yaosu': (('time', u'时间分析'), ('area', u'地域分析'), \
                      ('moodlens', u'情绪分析'), ('network', u'网络分析'), \
                      ('semantic', u'语义分析'))}

default_timerange = get_default_timerange()
default_topic = get_default_topic()
default_pointInterval = get_default_pointInterval()
pointIntervals = get_pointIntervals()
gaishu_yaosus = get_gaishu_yaosus()
deep_yaosus = get_deep_yaosus()

@mod.route('/')
def loading():
    """舆情案例首页
    """
    return render_template('index/gl.html')

@mod.route('/detail/')
def detail():
    """原有概述首页
    """
    return render_template('index/detail.html')

@mod.route('/manage/')
def manage():
    """案例定制页面
    """
    return render_template('index/manage.html')

@mod.route('/eva/')
def eva():
    """案例评价页面
    """
    return render_template('index/eva.html')

@mod.route('/user_weibo/')
def user_weibo():
    """微博列表页面
    """
    # 要素
    yaosu = 'moodlens'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    weibos = []
    tar_location = u'地域未知'
    tar_nickname = u'昵称未知'
    tar_profile_image_url = '#'
    tar_followers_count = u'粉丝数未知'
    tar_friends_count = u'关注数未知'
    tar_user_url = '#'
    uid = request.args.get('uid', None)

    if uid:   
        count, results = xapian_search_weibo.search(query={'user': int(uid)}, sort_by=['timestamp'], \
            fields=['id', 'user', 'text', 'reposts_count', 'comments_count', 'geo', 'timestamp'])
        
        for r in results():
            r['weibo_url'] = 'http://weibo.com/'
            r['user_url'] = 'http://weibo.com/u/' + str(uid)
            r['created_at'] = ts2date(r['timestamp'])
            weibos.append(r)

        user_info = acquire_user_by_id(uid)
        if user_info:
            tar_name = user_info['name']
            tar_location = user_info['location']
            tar_profile_image_url = user_info['profile_image_url']
            tar_friends_count = user_info['friends_count']
            tar_followers_count = user_info['followers_count']
            tar_user_url = 'http://weibo.com/u/' + str(uid)

    return render_template('index/weibolist.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus, tar_location=tar_location, \
            tar_profile_image_url=tar_profile_image_url, \
            statuses=weibos, tar_name=tar_name, tar_friends_count=tar_friends_count, \
            tar_followers_count=tar_followers_count, tar_user_url=tar_user_url)

@mod.route('/moodlens/')
def moodlens():
    # 要素
    yaosu = 'moodlens'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/moodlens.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)


@mod.route('/semantic/')
def meaning():
        # 要素
    yaosu = 'semantic'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/yuyi.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/area/')
def newarea():
    # 要素
    yaosu = 'area'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/area.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/time/')
def shijian():
        # 要素
    yaosu = 'time'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/time.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/time_news/')
def shijian_news():
        # 要素
    yaosu = 'time'

    # 话题关键词
    # topic = request.args.get('query', default_topic)
    topic = u'全军政治工作会议'

    # 时间范围: 20130901-20130901
    # time_range = request.args.get('time_range', default_timerange)
    time_range = u'20141101-20141115'

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/time_news.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/gaishu/')
def gaishu():
        # 要素
    yaosu = 'gaishu'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/gaishu.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/zhibiao/')
def zhibiao():
        # 要素
    yaosu = 'zhibiao'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/zhibiao.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/network/')
def topic():
        # 要素
    yaosu = 'network'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/network_direct_superior2.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/network1/')
def topic1():
        # 要素
    yaosu = 'network1'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/network_source.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/network_news/')
def network_news():
    yaosu = 'network_news'
    topic = request.args.get('query', default_topic)
    time_range = request.args.get('time_range', default_timerange)
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break
    # test        
    time_range = u'20141104-20141112'
    topic = u'全军政治工作会议'
    point_interval = 3600 * 24 

    return render_template('index/network_news.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntegervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

'''
@mod.route('/network2/')
def topic2():
        # 要素
    yaosu = 'network2'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/network_direct_superior.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)
'''

# 以下为新增内容
@mod.route('/gaishu_data/', methods = ['GET', 'POST'])
def gaishu_topic():
    topic = request.args.get('query', u'中国')
    if topic:
        topic = topic.strip()

    results = {}

    tag = '九一八、政府'
    results['tag'] = tag

    event_time = '2013-09-01'
    results['event_time'] = event_time

    event_spot = '北京'
    results['event_spot'] = event_spot

    # event_summary = '近年来，日本政府在钓鱼岛问题上不断挑起事端，特别是今年以来姑息纵容右翼势力掀起“购岛”风波，以为自己出面“购岛”铺路搭桥。'
    # results['event_summary'] = event_summary

    begin = topic_search('begin', topic)
    results['begin'] = begin

    end = topic_search('end', topic)
    results['end'] = end

    user_count = topic_search('user_count', topic)
    results['user_count'] = user_count

    count = topic_search('count', topic)
    results['count'] = count

    area = topic_search('area',topic)
    results['area'] = area

    k_limit = 3
    results['k_limit'] = k_limit

    key_words = topic_search('key_words',topic)
    results['key_words'] = key_words

    opinion = topic_search('opinion',topic)
    results['opinion'] = opinion

    media_opinion = topic_search('media_opinion',topic)
    results['media_opinion'] = media_opinion

    moodlens_pie = get_moodlens_pie(topic)
    results['moodlens_pie'] = moodlens_pie

    top_users = get_top_users(topic)
    results['top_users'] = top_users

    return json.dumps(results)

def get_moodlens_pie(topic = u'中国'):
    end_ts = time.mktime(datetime.datetime(2013,9,1,0,1,0).timetuple())
    during = 10

    results = {}
    results = pieModule.search_topic_pie(end_ts, during, query = topic)

    return results

def get_top_users(topic = u'中国'):
    topn = 10
    start_ts = 1377965700
    end_ts = 1378051200
    windowsize = (end_ts - start_ts + 900) / (24 * 60 * 60)
    date = ts2datetime(end_ts)

    if windowsize > 7:
        rank_method = 'degreerank'
    else:
        rank_method = 'pagerank'

    results = identifyModule.read_topic_rank_results(topic, topn, rank_method, date, windowsize)
    return results

def topic_search(item = 'count', topic = u'中国'):

    results = {}

    search_func = getattr(searchModule, 'search_%s' % item, None)

    if search_func:
        results = search_func(topic)
    else:
        return 'Search function undefined'

    return results

# 以下为原有内容
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

