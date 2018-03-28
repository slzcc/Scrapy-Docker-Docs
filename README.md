# Scrapy-Docker-Docs
## Docs Search Engine
获取 Docs 网站 URL 并注入 Redis ，Scrapy 从 Redis 获取 URL 开启爬取 150 字符内容数据并注入到 Elasticsearch，被访问的 URL 通过 Redis Set 去重。

Docker Image
```
registry.aliyuncs.com/slzcc/docker-docs:scrapy_redis
# or
slzcc/docker_docs:scrapy_redis
```
具体的 环境变量 定义请查看 [Dockerfile](Dockerfile) 。

1、Docker Run Redis
```
$ docker run -p 6379:6379 -v /data/redis/data:/data --name redis -d registry.aliyuncs.com/slzcc/redis
```

2、Docker Run Obtain URL
```
$ docker run --net host -e Start=URL -e REDIS_DB_HOST=127.0.0.1 -d registry.aliyuncs.com/slzcc/docker-docs:scrapy_redis
```
3、Docker Run Obtain Elasticsearch Data
```
$ docker run --net host -e REDIS_DB_HOST=127.0.0.1 -e ELASTICSEARCH_DB_SERVER=http://192.168.0.3:9200 -e ELASTICSEARCH_DATA_INDEX=docs-test -d registry.aliyuncs.com/slzcc/docker-docs:scrapy_redis
```
4、Search "docker" to Elasticsearch Data
```
$ curl -X GET http://192.168.0.3:9200/docs-test/item/_search?q=docker&size=10&pretty
{
  "took" : 4,
  "timed_out" : false,
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "failed" : 0
  },
  "hits" : {
    "total" : 1190,
    "max_score" : 0.004676234,
    "hits" : [
      {
        "_index" : "docs-test",
        "_type" : "item",
        "_id" : "AV1e-JwLIgU1iav4q5Bx",
        "_score" : 0.004676234,
        "_source" : {
          "url" : "http://47.52.73.177:8888//docker-for-mac/docker-toolbox/",
          "description" : "Docker for Mac vs. Docker Toolbox",
          "title" : "Docker for Mac vs. Docker Toolbox | Docker 中文文档",
          "data" : "If you already have an installation of Docker Toolbox, please read thesetopics first to learn how Docker for Mac and Docker Toolbox differ, and howthe...",
          "@timestamp" : "2017-07-20T07:48:57.449526"
        }
      },
      {
        "_index" : "docs-test",
        "_type" : "item",
        "_id" : "AV1e-N3EIgU1iav4q5Ca",
        "_score" : 0.004538842,
        "_source" : {
          "url" : "http://47.52.73.177:8888//docker-cloud/infrastructure/docker-upgrade/",
          "description" : "Upgrade Docker Engine on a node",
          "title" : "Upgrade Docker Engine on a node | Docker 中文文档",
          "data" : "Docker Cloud helps you manage nodes that have Docker Engine installed on them.You can upgrade the version of Docker Engine on your nodes when new vers...",
          "@timestamp" : "2017-07-20T07:49:14.275538"
        }
      },
...
```
如果注入 Elasticsearch 数据过慢，请启动多个 3 步骤实例，无上限。

5、Check Update New Page And retake the new content:
```
$  docker run --rm -i --net host -e ELASTICSEARCH_DB_SERVER=http://192.168.0.6:9200/ -e ELASTICSEARCH_DATA_INDEX=docs-test -e REDIS_DB_HOST=192.168.0.6 -e Start=CHECK registry.aliyuncs.com/slzcc/docker-docs:scrapy_redis
```
如果更新页面后，被检测到后会把 Redis 和 Elasticsearch 内的数据清除掉后，重新对 Redis List 里面注入需要更新的 URL，第 3 步骤启动的服务会发现有新的 URL 获取后并爬取数据注入到 Elasticsearch 。
