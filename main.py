from scrapy import cmdline
import os

if os.getenv('Start') == 'URL':
    cmdline.execute("scrapy crawl DockerDocs_Url".split())
elif os.getenv('Start') == True:
    cmdline.execute("scrapy crawl DockerDocs".split())
else:
    cmdline.execute("python docs/ObtainUrl.py".split())