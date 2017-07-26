#!/usr/local/env python
# -*- coding: utf-8 -*-


import requests, json, os, redis, threading, lxml, time

from elasticsearch import Elasticsearch

es = Elasticsearch('http://192.168.0.6:9200')

DocsURL = "http://47.52.73.177:8888"
ELASTICSEARCH_SEARCH_SERVERS = "http://els.hotstone.com.cn/"
ELASTICSEARCH_DB_INDEX = "docs-test"
ELASTICSEARCH_DB_TYPE = "item"
ELASTICSEARCH_SHA_TYPE = "sha"
REDIS_HOST = "192.168.0.6"
REDIS_PORT = 6379
REDIS_INDEX = 0
REDIS_DUPEFILTER = "DockerDocs:dupefilter"

redis_set = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_INDEX)

# DocsURL = os.getenv("DocsURL")
# REDIS_HOST = os.getenv('REDIS_DB_HOST')
# REDIS_PORT = int(os.getenv('REDIS_DB_PORT'))
# REDIS_INDEX = int(os.getenv('REDIS_DB_INDEX'))

UrlList = []
Counter = 0
threads = []

Source = requests.get(DocsURL + "{}".format("/metadata.txt")).content


# 获取 LEN 值
def Obtain_LEN(URL):
    Size = str(len(requests.get(url=URL).content))
    #	print(Size)
    return Size


# 检查 LEN 大小
def Check_LEN(Url, SizeValue):
    global Counter
    URL = ELASTICSEARCH_SEARCH_SERVERS + ELASTICSEARCH_DB_INDEX + "/" + ELASTICSEARCH_DB_TYPE + "/" + "_search?q=" + "url:" + "\"" + Url + "\"" + "&size=1"
    # print(URL, SizeValue)
    Session = requests.get(url=URL).content
    SearchNum = json.loads(Session)['hits']['total']
    if SearchNum >= 1:
        for i in json.loads(Session)['hits']['hits']:
            SearchDataUrl = i['_source']['url']
            SearchDataLength = i['_source']['length']
            SearchDataID = i['_id']
            if not SearchDataLength == SizeValue:
                es.delete(index=ELASTICSEARCH_DB_INDEX, doc_type=ELASTICSEARCH_DB_TYPE, id=SearchDataID)
                URL = ELASTICSEARCH_SEARCH_SERVERS + ELASTICSEARCH_DB_INDEX + "/" + ELASTICSEARCH_SHA_TYPE + "/" + "_search?q=" + "url:" + "\"" + SearchDataUrl + "\"" + "&size=1"
                Session = requests.get(url=URL).content
                SearchNum = json.loads(Session)['hits']['total']
                if SearchNum >= 1:
                    for i in json.loads(Session)['hits']['hits']:
                        SearchDataID = i['_id']
                        SearchDataSHA1 = i['_source']['sha1']
                        Counter += 1
                        es.delete(index=ELASTICSEARCH_DB_INDEX, doc_type=ELASTICSEARCH_SHA_TYPE, id=SearchDataID)
                        redis_set.srem(REDIS_DUPEFILTER, SearchSHA)
                        # print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                        print(
                            ">>> ERROR!! Counter is: {5}, DELETE ID: {0} , URL is: {1} , Length is: {2} , Actual Length is: {3} , SHA1 is: {4} 。".format(
                                SearchDataID, SearchDataUrl, SizeValue, SearchDataLength, SearchDataSHA1, Counter))
                        print("")
                        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


if __name__ == "__main__":
    Source = json.loads(Source)['pages']
    for i in Source:
        ss = DocsURL + i['url']
        UrlList.append(ss)
        Check_LEN(ss, Obtain_LEN(ss))

# print("The total number of {} 。".format(UrlList))
