# -*- coding: utf-8 -*-
import networkx as nx
import time
from SSDB import SSDB 
from config import SSDB_HOST, SSDB_PORT

def compute_quota(G):
    dCentrality = nx.degree_centrality(G)
    # 度中心性 dict{nodes:value} 度量重要性
    bCentrality = nx.betweenness_centrality(G)
    # 介数中心 dict{nodes:value},度量其对网络流程的重要性
    cCentrality = nx.closeness_centrality(G)
    # 紧密中心性 dict{nodes:value},，度量感知整个网络流程事件的位置
    eCentrality = nx.eigenvector_centrality_numpy(G)
    # 特征向量中心性
    dhistogram = nx.degree_histogram(G)
    # 节点度分布（从一到最大度的出现频次）
    gdegree = G.degree()
    #所有节点的度
    #gclustering = nx.clustering(G) --no for directed graph
    # 节点系数
    #aveclustering = nx.average_clustering(G)
    # 平均节点系数
    sconnectedn = nx.number_strongly_connected_components(G)
    # 强连通子图数量  int-n
    sconnectedc = nx.strongly_connected_components(G)
    # 强连通子图中的节点  list of lists
    wconnectesn = nx.number_weakly_connected_components(G)
    # 弱连通子图数量 int-n
    wconnectedc = nx.weakly_connected_components(G)
    # 若联通子图中的节点 list of lists
    #gcenter = nx.center(G)
    # The center is the set of nodes with eccentricity equal to radius   list od nodes in center
    #gdiameter = nx.diameter(G)
    # The diameter is the maximum eccentricity   int-n
    #geccentricity = nx.eccentrivity(G)
    # Return the eccentricity of nodes in G     dict{nodes:value}
    
    save_quota('degree_centrality', dCentrality)
    save_quota('betweenness_centrality', bCentrality)
    save_quota('closeness_centrality', cCentrality)
    save_quota('eigenvector_centrality', eCentrality)
    save_quota('degree_histogram', dhistogram)
    save_quota('g_degree', gdegree)
    #save_quota('clustering', gclustering)
    #save_quota('average_clustering', aveclustering)
    save_quota('number_strongly_connected_components', sconnectedn)
    save_quota('strongly_connected_components', sconnectedc)
    save_quota('number_weakly_connected_components', wconnectesn)
    save_quota('weakly_connected_components', wconnectedc)
    #save_quota('g_center', gcenter)
    #save_quota('g_diameter', gdiameter)
    #save_quota('g_eccentrivity', geccentricity)
    
    

def save_quota(key, value):
    '''保存网络指标
    '''
    try:
        ssdb = SSDB(SSDB_HOST, SSDB_PORT)
        if ssdb:
            print 'ssdb yes'
        else:
            print 'ssdb no'
        result = ssdb.request('set',[key, value])
        if result.code == 'ok':
            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), 'save success', key ,value
        else:
            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), 'save failed'
    except Exception, e:
        print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),'SSDB ERROR'
