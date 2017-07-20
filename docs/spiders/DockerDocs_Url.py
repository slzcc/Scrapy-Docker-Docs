# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from docs.items import DocsItem
import html2text, re, redis, os

REDIS_HOST = os.getenv('REDIS_DB_HOST')
REDIS_PORT = int(os.getenv('REDIS_DB_PORT'))

# REDIS_HOST = '127.0.0.1'
# REDIS_PORT = '6379'

redis_q = redis.StrictRedis(connection_pool=redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0))

class DockerdocsSpider(CrawlSpider):
    name = 'DockerDocs_Url'
    allowed_domains = [os.getenv("Domains")]
    start_urls = [os.getenv("DocsURL")]
    
    rules = (
        Rule(LinkExtractor(allow=os.getenv('Rules_All'), deny=os.getenv('Rules_Deny')), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        redis_q.lpush(os.getenv("REDIS_KEY"), response.url)