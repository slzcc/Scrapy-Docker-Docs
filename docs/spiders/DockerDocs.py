# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from docs.items import DocsItem
import html2text, re, os
from scrapy_redis.spiders import RedisSpider

class DockerdocsSpider(RedisSpider):
    name = 'DockerDocs'
    allowed_domains = [os.getenv("Domains")]
    redis_key = os.getenv("REDIS_KEY")

    Lists = []

    def parse(self, response):
        yield scrapy.Request(url=response.url, callback=self.pares_data)

    def pares_data(self, response):
        item = DocsItem()

        item['url'] = response.url
        item['description'] = response.xpath('//section[@class="section"]/h1/text()').extract()[0]
        item['title'] = response.xpath('//title/text()').extract()[0]

        item['data'] = html2text.html2text(response.xpath('//section[@class="section"]').extract()[0])
        if re.findall('\*\*此内容.*?\*\*', item['data']):
            item['data'] = re.split('\*\*此内容.*?\*\*\s', item['data'])[1]
        if re.findall('>', item['data']):
            item['data'] = re.sub('>\s', "", item['data'])
            item['data'] = re.sub('>', "", item['data'])
        if re.findall('<', item['data']):
            item['data'] = re.sub('<\s', "", item['data'])
            item['data'] = re.sub('<', "", item['data'])
        if re.findall('^#{1}?', item['data']):
            item['data'] = re.sub('^#{1}? \w+.*', "", item['data'])
        if re.findall('\s#{1}?', item['data']):
            item['data'] = re.sub('\s#{1}? \w+.*', "", item['data'])
        if re.findall('##', item['data']):
            item['data'] = re.sub('##\s', "", item['data'])
        if re.findall('#', item['data']):
            item['data'] = re.sub('#', "", item['data'])
        if re.findall('\*\*', item['data']):
            item['data'] = re.sub('\*\*\s', "", item['data'])
            item['data'] = re.sub('\*\*', "", item['data'])
        if re.findall('\*', item['data']):
            item['data'] = re.sub('\*', "", item['data'])
            item['data'] = re.sub('\*\s', "", item['data'])
        if re.findall('Estimated reading time: .* minute.*', item['data']):
            item['data'] = re.sub('.* minute.*\s', "", item['data'])
        if re.findall('^#{2,}', item['data']):
            item['data'] = re.sub('^#{2,} \w*', "", item['data'])
        if re.findall('\[.*\]\(.*\)', item['data']):
            item['data'] = re.sub('\[.*\]\(.*\)\s', "", item['data'])
            item['data'] = re.sub('\[.*\]\(.*\)', "", item['data'])
        if re.findall('\n', item['data']):
            item['data'] = re.sub('\n', "", item['data'])

        item['data'] = item['data'][:150] + "..."
        return item