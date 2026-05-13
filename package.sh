#!/bin/bash
set -e

echo "========================================="
echo " TinyWiki 部署打包脚本"
echo "========================================="

tar -zcvf tinywiki-src.tar.gz knowledge_base/ frontend/ nginx.conf docker-compose.yml postgres/ requirements.txt
echo "源代码已打包到 tinywiki-src.tar.gz"

sudo docker save -o tinywiki-all-images.tar nginx:alpine tinywiki-db:latest tinywiki-web:latest
echo "所有镜像已保存到 tinywiki-all-images.tar"

echo "部署打包完成！"

