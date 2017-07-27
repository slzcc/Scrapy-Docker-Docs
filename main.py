from scrapy import cmdline
import os

if os.getenv('Start') == 'CHECK':
    os.system("python docs/check_page.py")
elif os.getenv('Start') == 'True':
    cmdline.execute("scrapy crawl DockerDocs".split())
elif os.getenv('Start') == 'URL':
    os.system("python docs/ObtainUrl.py")
else:
    pass