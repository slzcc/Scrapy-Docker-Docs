#!/usr/bin/env python
# -*- coding: utf-8 -*-


import requests, json, os, redis, threading

DocsURL = os.getenv("DocsURL")

REDIS_HOST = os.getenv('REDIS_DB_HOST')
REDIS_PORT = int(os.getenv('REDIS_DB_PORT'))

threads = []
Counter = 0

redis_q = redis.StrictRedis(connection_pool=redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0))

header = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, sdch, br',
		'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
		'Connection': 'keep-alive',
		'Host': 'www.zhihu.com',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
	}

Source = requests.get(DocsURL + "{}".format("/metadata.txt"),  headers=header).content

class TaskThread(threading.Thread):
	def __init__(self, data):
		threading.Thread.__init__(self)
		self.Data = data

	def run(self):
		global redis_q, DocsURL, Counter
		locks.acquire()
		Data = DocsURL + "{}".format(self.Data)
		redis_q.lpush('docs:start_urls', Data)
		Counter += 1
		print(Data, Counter)
		locks.release()

def ObtainUrl(URL):
	T = TaskThread(URL)
	T.start()
	threads.append(T)
	for t in threads:
		t.join()

if __name__ == "__main__":
	Source = json.loads(Source)['pages']
	locks = threading.Lock()
	for i in Source:
		ObtainUrl(i['url'])
	print("The total number of {} 。".format(Counter))