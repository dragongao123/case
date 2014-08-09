# -*- coding: utf-8 -*-


import json
import math
import operator
from sqlalchemy import func
from case.extensions import db
from time_utils import datetime2ts
from case.model import CityTopicCount   #需要查询的表
from BeautifulSoup import BeautifulSoup
from city_color import province_color_map


Minute = 60
Fifteenminutes = 15 * Minute
Hour = 3600
SixHour = Hour * 6
Day = Hour * 24
MinInterval = Fifteenminutes
html = '''<select name="province" id="province" defvalue="11"><option value="34">安徽</option><option value="11">北京</option><option value="50">重庆</option><option value="35">福建</option><option value="62">甘肃</option>
            <option value="44">广东</option><option value="45">广西</option><option value="52">贵州</option><option value="46">海南</option><option value="13">河北</option>
            <option value="23">黑龙江</option><option value="41">河南</option><option value="42">湖北</option><option value="43">湖南</option><option value="15">内蒙古</option><option value="32">江苏</option>
            <option value="36">江西</option><option value="22">吉林</option><option value="21">辽宁</option><option value="64">宁夏</option><option value="63">青海</option><option value="14">山西</option><option value="37">山东</option>
            <option value="31">上海</option><option value="51">四川</option><option value="12">天津</option><option value="54">西藏</option><option value="65">新疆</option><option value="53">云南</option><option value="33">浙江</option>
            <option value="61">陕西</option><option value="71">台湾</option><option value="81">香港</option><option value="82">澳门</option><option value="400">海外</option><option value="100">其他</option></select>'''
province_soup = BeautifulSoup(html)
provinces = province_soup.findAll('option')

def sum_pcount(item):
    pcount={}
    print 'item:',item
    for r in item: # 遍历所有匹配集
        if r.ccount:
            rccount = json.loads(r.ccount)
            #print rccount
            for i in rccount: # 遍历匹配集中的ccount字典
                #print '*'*10
                #print type(i)
                for province in provinces:
                    p = province.string
                    #print '$'*10
                    #print type(p)
                    if i.split('\t')[1] == p:
                        try:
                            pcount[p] += rccount[i]
                        except KeyError:
                            pcount[p] = rccount[i]
                    else:
                        continue


        else:
            continue
        
    return pcount


def Pcount(end_ts, during, stylenum, topic, unit=MinInterval):

    pcount={} # 省市对应count
    if during <= unit: # 时间范围选择小于默认最小时间段15分钟，则默认为15分钟
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        if stylenum == 4: # 求所有的和
            item=db.session.query(CityTopicCount).filter(SentimentCount.end==upbound, \
                                              SentimentCount.range==unit, \
                                              SentimentCount.topic==topic).first()
        else:
            item = db.session.query(CityTopicCount).filter(SentimentCount.end==upbound, \
                                              SentimentCount.mtype==stylenum, \
                                              SentimentCount.range==unit, \
                                              SentimentCount.topic==topic).first() # 查询出匹配微博集
        if item: # 若查询结果存在，计算ccount中属于同一个省份count和
            if not isinstance(item, list):
                item = [item]
            pcount=sum_pcount(item)
        else:
            pcount={} # 查询结果为空

    else:                         #时间范围大于15分钟时，将其转化为15分钟的整数倍段
        start_ts =end_ts - during
        upbound = int(math.ceil(end_ts / (unit * 1.0)) * unit)
        lowbound = (start_ts / unit) * unit
        if stylenum == 4:
            item = db.session.query(CityTopicCount).filter(CityTopicCount.end>lowbound, \
                                                CityTopicCount.end<=upbound, \
                                                CityTopicCount.range==unit, \
                                                CityTopicCount.topic==topic).all()
        else:
            item = db.session.query(CityTopicCount).filter(CityTopicCount.end>lowbound, \
                                                CityTopicCount.end<=upbound, \
                                                CityTopicCount.mtype==stylenum, \
                                                CityTopicCount.range==unit, \
                                                CityTopicCount.topic==topic).all()

        if item:
            if not isinstance(item, list):
                item = [item]
            pcount=sum_pcount(item)
        else:
            pcount = {}

    return pcount

'''
if __name__ == '__main__':
    end_ts = datetime2ts('2013-09-1')
    during = 1 * Day
    topic = u'九一八'
    stylenum = 1
    count = Pcount(end_ts, during, stylenum, topic)
    print count
'''