#!/bin/bash
set -e

echo "========================================="
echo " TinyWiki 部署打包脚本"
echo "========================================="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 版本号（可以自己改）
VERSION="1.0.0"
PACKAGE_NAME="tinywiki-deploy-v${VERSION}"
OUTPUT_DIR="$SCRIPT_DIR/dist"

echo ""
echo "📦 准备打包环境..."
mkdir -p "$OUTPUT_DIR"
rm -rf "$OUTPUT_DIR"/*

echo ""
echo "🐳 构建并保存 Docker 镜像..."

# 拉取 nginx 镜像（公共镜像，先拉取）
echo "拉取 Nginx 镜像..."
docker pull nginx:alpine

# 构建所有镜像
echo "构建数据库镜像..."
docker-compose build db

echo "构建 Web 镜像..."
docker-compose build web

# 保存所有镜像
echo "保存 Docker 镜像..."
docker save -o "$OUTPUT_DIR/tinywiki-postgres.tar" tinywiki_db:latest || true
docker save -o "$OUTPUT_DIR/tinywiki-web.tar" tinywiki_web:latest || true
docker save -o "$OUTPUT_DIR/tinywiki-nginx.tar" nginx:alpine || true

# 把镜像也复制到部署包里
mkdir -p "$OUTPUT_DIR/$PACKAGE_NAME"
cp "$OUTPUT_DIR/tinywiki-postgres.tar" "$OUTPUT_DIR/$PACKAGE_NAME/" || true
cp "$OUTPUT_DIR/tinywiki-web.tar" "$OUTPUT_DIR/$PACKAGE_NAME/" || true
cp "$OUTPUT_DIR/tinywiki-nginx.tar" "$OUTPUT_DIR/$PACKAGE_NAME/" || true

echo ""
echo "📁 打包部署文件..."

# 创建部署目录结构
mkdir -p "$OUTPUT_DIR/$PACKAGE_NAME"

# 复制必要的文件
cp docker-compose.yml "$OUTPUT_DIR/$PACKAGE_NAME/"
cp -r postgres/ "$OUTPUT_DIR/$PACKAGE_NAME/" 2>/dev/null || true
cp -r knowledge_base/ "$OUTPUT_DIR/$PACKAGE_NAME/" 2>/dev/null || true
cp -r requirements.txt "$OUTPUT_DIR/$PACKAGE_NAME/" 2>/dev/null || true
cp README.md "$OUTPUT_DIR/$PACKAGE_NAME/" 2>/dev/null || true

# 创建内网部署说明
cat > "$OUTPUT_DIR/$PACKAGE_NAME/DEPLOY.md" << 'EOF'
# TinyWiki 内网部署指南

## 前置要求
- Docker 和 Docker Compose 已安装
- 4GB+ 内存

## 部署步骤

### 1. 加载 Docker 镜像
```bash
# 加载数据库镜像
docker load -i tinywiki-postgres.tar

# 加载 Web 镜像
docker load -i tinywiki-web.tar

# 加载 Nginx 镜像
docker load -i tinywiki-nginx.tar
```

### 2. 修改 docker-compose.yml
确保数据库配置正确：
- POSTGRES_DB: tinywiki
- POSTGRES_USER: tinywiki_user
- POSTGRES_PASSWORD: tinywiki_password

### 3. 启动服务
```bash
# 首次启动（会初始化数据库）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 访问
- 前端: http://服务器IP
- 后端: http://服务器IP:8080

## 目录结构
```
tinywiki-deploy-v1.0.0/
├── docker-compose.yml      # Docker Compose 配置
├── postgres/               # 数据库相关配置
├── knowledge_base/         # 后端代码
├── DEPLOY.md               # 本文件
```
EOF

# 创建内网 docker-compose.yml（禁用 build，只用 image）
cat > "$OUTPUT_DIR/$PACKAGE_NAME/docker-compose.prod.yml" << 'EOF'
version: '3.8'

services:
  db:
    # 使用预构建的镜像
    image: tinywiki_db:latest
    environment:
      POSTGRES_DB: tinywiki
      POSTGRES_USER: tinywiki_user
      POSTGRES_PASSWORD: tinywiki_password
    volumes:
      - ./postgres_data:/var/lib/postgresql/data
      - ./postgres/initdb:/docker-entrypoint-initdb.d
    restart: always
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tinywiki_user -d tinywiki"]
      interval: 5s
      timeout: 5s
      retries: 5

  web:
    # 使用预构建的镜像
    image: tinywiki_web:latest
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn knowledge_base.wsgi:application --bind 0.0.0.0:8080 --workers 4 --timeout 120"
    volumes:
      - static_volume:/app/knowledge_base/staticfiles
      - media_volume:/app/knowledge_base/media
      - storage_volume:/app/knowledge_base/storage
    depends_on:
      db:
        condition: service_healthy
    environment:
      DEBUG: "False"
      SECRET_KEY: "django-insecure-this-is-a-simple-secret-key-change-it-in-production"
      ALLOWED_HOSTS: "*"
      POSTGRES_DB: tinywiki
      POSTGRES_USER: tinywiki_user
      POSTGRES_PASSWORD: tinywiki_password
      POSTGRES_HOST: db
      POSTGRES_PORT: "5432"
      CORS_ALLOW_ALL: "True"
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/app/knowledge_base/staticfiles
      - media_volume:/app/knowledge_base/media
      - storage_volume:/app/knowledge_base/storage
      - ./frontend/dist:/usr/share/nginx/html
    depends_on:
      - web
    restart: always

volumes:
  static_volume:
  media_volume:
  storage_volume:
EOF

# 压缩整个包
echo ""
echo "🗜️  压缩打包..."
cd "$OUTPUT_DIR"
tar -czf "${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"

echo ""
echo "========================================="
echo "✅ 打包完成！"
echo "========================================="
echo ""
echo "📦 包文件: $OUTPUT_DIR/${PACKAGE_NAME}.tar.gz"
echo ""
echo "📁 解压后部署: "
echo "   tar -xzf ${PACKAGE_NAME}.tar.gz"
echo "   cd $PACKAGE_NAME"
echo "   docker load -i tinywiki-postgres.tar"
echo "   docker load -i tinywiki-web.tar"
echo "   docker load -i tinywiki-nginx.tar"
echo "   docker-compose -f docker-compose.prod.yml up -d"
echo ""
