# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from docs.items import DocsItem
import html2text, re

class DockerdocsSpider(CrawlSpider):
    name = 'DockerDocs'
    allowed_domains = ['47.52.73.177']
    start_urls = ['http://47.52.73.177:8888/']
    
    rules = (
        Rule(LinkExtractor(allow=('', ), deny=('#.*?', 'term*?', )), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = DocsItem()
        item['url'] = response.url
        item['description'] = response.xpath('//section[@class="section"]/h1/text()').extract()[0]
        item['title'] = response.xpath('//title/text()').extract()[0]
        item['data'] = html2text.html2text(response.xpath('//main[@class="col-content content"]').extract()[0])
        if re.findall('\*\*.*?\*\*', item['data']):
            item['data'] = re.split('\*\*.*?\*\*\s', item['data'])[1]
        item['data'] = re.sub('#\s', "", item['data'])[:100] + "..."
        return item