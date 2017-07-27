FROM registry.aliyuncs.com/slzcc/python:3
RUN git clone https://github.com/slzcc/Scrapy-Docker-Docs.git && \
    cd Scrapy-Docker-Docs && \
    pip install -r package.txt

COPY dupefilter.py /usr/local/lib/python3.6/site-packages/scrapy_redis/dupefilter.py

ENV REDIS_DB_HOST=127.0.0.1 \
    REDIS_DB_PORT=6379 \
    REDIS_DB_INDEX=0 \
    REDIS_KEY="docs:start_urls" \
    ELASTICSEARCH_DB_SERVER=http://localhost:9200/ \
    ELASTICSEARCH_DATA_INDEX=docs-data \
    ELASTICSEARCH_DATA_TYPE=item \
    ELASTICSEARCH_SHA_TYPE=sha \
    CONCURRENT_REQUESTS=1 \
    DOWNLOAD_DELAY=1 \
    Rules_Deny="('#.*?', 'term*?', 'v1.*?', '.*?md', )" \
    Rules_All="('',)" \
    DocsURL="http://47.52.73.177:8888" \
    Domains="47.52.73.177" \
    Start=True \
    REDIS_DUPEFILTER="DockerDocs:dupefilter" \
    TZ=Asia/Shanghai

WORKDIR /Scrapy-Docker-Docs

CMD ["python", "main.py"]
