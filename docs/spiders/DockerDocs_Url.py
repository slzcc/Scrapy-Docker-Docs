# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from docs.items import DocsItem
import html2text, re, redis, os

REDIS_HOST = os.getenv('REDIS_DB_HOST')
REDIS_PORT = int(os.getenv('REDIS_DB_PORT'))
redis_q = redis.StrictRedis(connection_pool=redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0))

class DockerdocsSpider(CrawlSpider):
    name = 'DockerDocs_Url'
    allowed_domains = ['47.52.73.177']
    start_urls = ['http://47.52.73.177:8888/']
    
    rules = (
        Rule(LinkExtractor(allow=('', ), deny=('#.*?', 'term*?', 'v1.*?',)), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        redis_q.lpush('docs:start_urls', response.url)