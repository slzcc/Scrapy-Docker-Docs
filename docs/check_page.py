#!/usr/local/env python
# -*- coding: utf-8 -*-


import requests, json, os, redis

from elasticsearch import Elasticsearch



# DocsURL = "http://47.52.73.177:8888"
# ELASTICSEARCH_SEARCH_SERVERS = "http://els.hotstone.com.cn/"
# ELASTICSEARCH_DB_INDEX = "docs-test"
# ELASTICSEARCH_DB_TYPE = "item"
# ELASTICSEARCH_SHA_TYPE = "sha"
# REDIS_HOST = "192.168.0.6"
# REDIS_PORT = 6379
# REDIS_INDEX = 0

REDIS_DUPEFILTER = os.getenv("REDIS_DUPEFILTER")
es = Elasticsearch(os.getenv('ELASTICSEARCH_DB_SERVER'))
DocsURL = os.getenv("DocsURL")
REDIS_HOST = os.getenv('REDIS_DB_HOST')
REDIS_PORT = int(os.getenv('REDIS_DB_PORT'))
REDIS_INDEX = int(os.getenv('REDIS_DB_INDEX'))
ELASTICSEARCH_DB_SERVER = os.getenv('ELASTICSEARCH_DB_SERVER')
ELASTICSEARCH_DATA_INDEX = os.getenv('ELASTICSEARCH_DATA_INDEX')
ELASTICSEARCH_DATA_TYPE = os.getenv('ELASTICSEARCH_DATA_TYPE')
ELASTICSEARCH_SHA_TYPE = os.getenv('ELASTICSEARCH_SHA_TYPE')

redis_set = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_INDEX)

UrlList = []
Counter = 0
threads = []

Source = requests.get(DocsURL + "{}".format("/metadata.txt")).content


# 获取 LEN 值
def Obtain_LEN(URL):
    Size = str(len(requests.get(url=URL).content))
    return Size


# 检查 LEN 大小
def Check_LEN(Url, SizeValue):
    global Counter
    URL       = ELASTICSEARCH_DB_SERVER + ELASTICSEARCH_DATA_INDEX + "/" + ELASTICSEARCH_DATA_TYPE + "/" + "_search?q=" + "url:" + "\"" + Url + "\"" + "&size=100"
    Session   = requests.get(url=URL).content
    SearchNum = json.loads(Session)['hits']['total']
    if SearchNum >= 1:
        for i in json.loads(Session)['hits']['hits']:
            SearchDataUrl    = i['_source']['url']
            SearchDataLength = i['_source']['length']
            SearchDataID     = i['_id']
            if SearchDataUrl == Url:
                if not SearchDataLength == SizeValue:
                    URL     = ELASTICSEARCH_DB_SERVER + ELASTICSEARCH_DATA_INDEX + "/" + ELASTICSEARCH_SHA_TYPE + "/" + "_search?q=" + "url:" + "\"" + SearchDataUrl + "\"" + "&size=100"
                    Session = requests.get(url=URL).content
                    for j in json.loads(Session)['hits']['hits']:
                        SubSearchDataUrl = j['_source']['url']
                        if SearchDataUrl == SubSearchDataUrl:
                            SubSearchDataID   = j['_id']
                            SubSearchDataSHA1 = j['_source']['sha1']
                            Counter          += 1
                            print(">>> ERROR!! Counter is: {5}, DELETE ID: {0} , URL is: {1} , Now Length is: {2} , Source Length is: {3} , SHA1 is: {4} 。".format(SubSearchDataID, SearchDataUrl, SizeValue, SearchDataLength, SubSearchDataSHA1, Counter))
                            print("")
                            es.delete(index=ELASTICSEARCH_DATA_INDEX, doc_type=ELASTICSEARCH_DATA_TYPE, id=SearchDataID)
                            es.delete(index=ELASTICSEARCH_DATA_INDEX, doc_type=ELASTICSEARCH_SHA_TYPE, id=SubSearchDataID)
                            redis_set.srem(REDIS_DUPEFILTER, SubSearchDataSHA1)

if __name__ == "__main__":
    Source = json.loads(Source)['pages']
    for i in Source:
        url = DocsURL + i['url']
        UrlList.append(url)
        Check_LEN(url, Obtain_LEN(url))