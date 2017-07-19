FROM registry.aliyuncs.com/slzcc/python:3
RUN git clone https://github.com/slzcc/Scrapy-Docker-Docs.git && \
    cd Scrapy-Docker-Docs && \
    pip install -r package.txt

ENV REDIS_DB_HOST=127.0.0.1 \
    REDIS_DB_PORT=6379 \
    ELASTICSEARCH_DB_SERVER=http://localhost:9200 \
    ELASTICSEARCH_DATA_INDEX=docker-docs \
    ELASTICSEARCH_DATA_TYPE=item \
    CONCURRENT_REQUESTS=32 \
    DOWNLOAD_DELAY=1

WORKDIR /Scrapy-Docker-Docs

CMD ["python", "main.py"]
