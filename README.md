# Scrapy-Docker-Docs
Docker Image
```
registry.aliyuncs.com/slzcc/docker-docs:scrapy_redis
```
具体的 环境变量 定义请查看 [!Dockerfile](Dockerfile) 。

1、Docker Run Redis
```
$ docker run -p 6379:6379 -v /data/redis/data:/data --name redis -d registry.aliyuncs.com/slzcc/redis
```

2、Docker Run Redis URL
```
$ docker run --net host -e Start=ss -e REDIS_DB_HOST=127.0.0.1 -d registry.aliyuncs.com/slzcc/docker-docs:scrapy_redis
```
3、Docker Run Elasticsearch Data
```
$ docker run --net host -e REDIS_DB_HOST=127.0.0.1 -e ELASTICSEARCH_DB_SERVER=http://192.168.0.3:9200 -e ELASTICSEARCH_DATA_INDEX=docs-test -d registry.aliyuncs.com/slzcc/docker-docs:scrapy_redis
```
4、Search "docker" to Elasticsearch Data
```
$ curl -X GET http://192.168.0.3:9200/docs-test/item/_search?q=docker&size=100
```
