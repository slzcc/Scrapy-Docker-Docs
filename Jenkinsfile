node(){
  stage "GIt"
    git "https://github.com/slzcc/Scrapy-Docker-Docs"

  stage "Build"
    registry_addr="registry.aliyuncs.com"
    maintainer_name="slzcc"
    container_name="docker-docs"
    tag="scrapy_redis"

    sh "docker build -t ${registry_addr}/${maintainer_name}/${container_name}:${tag} . --rm --no-cache"
    echo "****************************************************************************************************************"
    echo "The Demo Image is ${registry_addr}/${maintainer_name}/${container_name}:${tag}"
    echo "****************************************************************************************************************"
  stage('Docker Push')
    input "请确保上述没问题后，Push 远程仓库！"
    sh "docker push ${registry_addr}/${maintainer_name}/${container_name}:${tag}"
}
