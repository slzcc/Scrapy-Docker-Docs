from scrapy import cmdline
import os

if os.getenv('Start') == 'URL':
    cmdline.execute("scrapy crawl DockerDocs_Url".split())
else:
    cmdline.execute("scrapy crawl DockerDocs".split())