#-*- coding:utf-8 -*-
import os
import json
import pymongo
from case.global_config import MONGODB_HOST, MONGODB_PORT
from xapian_case.xapian_backend import XapianSearch
from case.extensions import db

conn = pymongo.Connection(host=MONGODB_HOST, port=MONGODB_PORT)
mongodb = conn['54api_weibo_v2']
#collection = 'master_timeline_topic'
'''
Q: topicname ->topic_id  weibo   mongo
'''
def get_info_num(topic_name):
    topic_id = get_dynamic_mongo(topic_name)
    xapian_search_weibo = getXapianWeiboByTopic(topic_id)
    items = xapian_search_weibo.iter_all_docs()
    weibo_count = 0
    user_set = set()
    for item in items:
        weibo_count += 1
        uid = item['user']
        user_set.add(uid)
    user_count = len(user_set)
    return user_count, weibo_count
    

def get_dynamic_mongo(topic_name):
    topic_collection = mongodb.master_timeline_topic
    topic_item = topic_collection.find_one({'name': topic_name})
    if not topic_item:
        print 'this topic is not exist'
        return None
    else:
        topic_id = topic_item['_id']
        return topic_id

def getXapianWeiboByTopic(topic_id):
    XAPIAN_WEIBO_TOPIC_PATH = '/home/xapian/xapian_weibo_topic/'
    stub_file = XAPIAN_WEIBO_TOPIC_PATH + 'stub/xapian_weibo_topic_stub_' + str(topic_id)
    if os.path.exists(stub_file):
        print 'stub_file exist'
        xapian_search_weibo = XapianSearch(stub=stub_file, schema_version='5')
        return xapian_search_weibo
    else:
        print 'stub not exist'
        return None

def json2str(key, items):
    result = ''

    #print 'key, items:', key, items
    if key== 'propagate_keywords':
        for item in items:
            result += str(item)
            result += '|'
    elif key== 'identify_firstuser':
        items = items[1:]
        for item in items:
            #print 'item:', item
            result += str(item[0])
            result += ','
            result += str(item[1])
            if item[1]==u'未知':
                result += '('
                result += str(item[0])
                result += ')'
            result += ', , |'
    elif key== 'identify_trendpusher':
        for item in items:
            result += str(item[0])
            result += ','
            result += str(item[1])
            if item[1]==u'未知':
                result += '('
                result += str(item[0])
                result += ')'
            result += ', , |'
    elif key=='identify_pagerank':
        for item in items:
            result += str(item[1])
            result += ','
            result += str(item[2])
            if item[2]==u'未知':
                result += '('
                result += str(item[1])
                result += ')'
            result += ', , |'
    n = len(result)
    result = result[:n-1]
    #print 'key:', key
    #print 'result:', result
    return result

def json2list(key, items):
    result = []
    if key=='propagate_peak':
        kind = u'微博'
    elif key=='propagate_peak_news':
        kind = u'新闻'
    count_list = items['count_list']
    ts_list = items['ts']
    peaks = items['peak']
    peak_list = []
    for peak in peaks:
        peak_dict = peaks[peak]
        peak_list.append(peak_dict['ts'])
    for n in range(len(count_list)):
        item = []
        count = count_list[n]
        ts = ts_list[n]
        if ts in peak_list:
            peak = 1
        else:
            peak = 0
        item = [count, ts, peak]
        result.append(item)
    return result
