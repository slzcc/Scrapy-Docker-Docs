import logging
import time
import os
import datetime
import requests as RQ
import json

from elasticsearch import Elasticsearch

from scrapy.dupefilters import BaseDupeFilter
from scrapy.utils.request import request_fingerprint

from . import defaults
from .connection import get_redis_from_settings


logger = logging.getLogger(__name__)

ELASTICSEARCH_SEARCH_SERVERS = os.getenv('ELASTICSEARCH_DB_SERVER')
ELASTICSEARCH_DATA_INDEX = os.getenv('ELASTICSEARCH_DATA_INDEX')
ELASTICSEARCH_DATA_TYPE = os.getenv('ELASTICSEARCH_DATA_TYPE')
ELASTICSEARCH_SHA_TYPE = os.getenv('ELASTICSEARCH_SHA_TYPE')

_es = Elasticsearch(ELASTICSEARCH_SEARCH_SERVERS)
DATA = {}
Num = {
  "took": 1,
  "timed_out": False,
  "_shards": {
    "total": 5,
    "successful": 5,
    "failed": 0
  },
  "hits": {
    "total": 0,
    "max_score": None,
    "hits": []
  }
}

# TODO: Rename class to RedisDupeFilter.
class RFPDupeFilter(BaseDupeFilter):
    """Redis-based request duplicates filter.

    This class can also be used with default Scrapy's scheduler.

    """

    logger = logger

    def __init__(self, server, key, debug=False):
        """Initialize the duplicates filter.

        Parameters
        ----------
        server : redis.StrictRedis
            The redis server instance.
        key : str
            Redis key Where to store fingerprints.
        debug : bool, optional
            Whether to log filtered requests.

        """
        self.server = server
        self.key = key
        self.debug = debug
        self.logdupes = True

    @classmethod
    def from_settings(cls, settings):
        """Returns an instance from given settings.

        This uses by default the key ``dupefilter:<timestamp>``. When using the
        ``scrapy_redis.scheduler.Scheduler`` class, this method is not used as
        it needs to pass the spider name in the key.

        Parameters
        ----------
        settings : scrapy.settings.Settings

        Returns
        -------
        RFPDupeFilter
            A RFPDupeFilter instance.


        """
        server = get_redis_from_settings(settings)
        # XXX: This creates one-time key. needed to support to use this
        # class as standalone dupefilter with scrapy's default scheduler
        # if scrapy passes spider on open() method this wouldn't be needed
        # TODO: Use SCRAPY_JOB env as default and fallback to timestamp.
        key = defaults.DUPEFILTER_KEY % {'timestamp': int(time.time())}
        debug = settings.getbool('DUPEFILTER_DEBUG')
        return cls(server, key=key, debug=debug)

    @classmethod
    def from_crawler(cls, crawler):
        """Returns instance from crawler.

        Parameters
        ----------
        crawler : scrapy.crawler.Crawler

        Returns
        -------
        RFPDupeFilter
            Instance of RFPDupeFilter.

        """
        return cls.from_settings(crawler.settings)

    def request_seen(self, request):
        """Returns True if request was already seen.

        Parameters
        ----------
        request : scrapy.http.Request

        Returns
        -------
        bool

        """
        fp = self.request_fingerprint(request)
        # This returns the number of values added, zero if already exists.
        added = self.server.sadd(self.key, fp)

        URL = ELASTICSEARCH_SEARCH_SERVERS + ELASTICSEARCH_DATA_INDEX + "/" + ELASTICSEARCH_SHA_TYPE + "/" + "_search?q=" + "sha:" + "\"" + fp + "\"" + "&size=1"
        Session = RQ.get(url=URL).content
        print(json.loads(Session))
        for k in json.loads(Session):
            if k == 'error' or k == 'status':
                DATA['timestamp'] = datetime.datetime.now()
                DATA['url'] = request.url
                DATA['sha1'] = fp
                _es.index(index=ELASTICSEARCH_DATA_INDEX, doc_type=ELASTICSEARCH_SHA_TYPE, body=DATA)
                _es.indices.refresh(index=ELASTICSEARCH_DATA_INDEX)
            elif k == 'hits' and json.loads(Session)['hits']['total'] == 0:
                DATA['timestamp'] = datetime.datetime.now()
                DATA['url'] = request.url
                DATA['sha1'] = fp
                _es.index(index=ELASTICSEARCH_DATA_INDEX, doc_type=ELASTICSEARCH_SHA_TYPE, body=DATA)
                _es.indices.refresh(index=ELASTICSEARCH_DATA_INDEX)
            else:
                print("Existing URL :", request.url)

        return added == 0

    def request_fingerprint(self, request):
        """Returns a fingerprint for a given request.

        Parameters
        ----------
        request : scrapy.http.Request

        Returns
        -------
        str

        """
        return request_fingerprint(request)

    def close(self, reason=''):
        """Delete data on close. Called by Scrapy's scheduler.

        Parameters
        ----------
        reason : str, optional

        """
        self.clear()

    def clear(self):
        """Clears fingerprints data."""
        self.server.delete(self.key)

    def log(self, request, spider):
        """Logs given request.

        Parameters
        ----------
        request : scrapy.http.Request
        spider : scrapy.spiders.Spider

        """
        if self.debug:
            msg = "Filtered duplicate request: %(request)s"
            self.logger.debug(msg, {'request': request}, extra={'spider': spider})
        elif self.logdupes:
            msg = ("Filtered duplicate request %(request)s"
                   " - no more duplicates will be shown"
                   " (see DUPEFILTER_DEBUG to show all duplicates)")
            self.logger.debug(msg, {'request': request}, extra={'spider': spider})
            self.logdupes = False
