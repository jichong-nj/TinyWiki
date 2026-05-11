# TinyWiki 离线 Docker 部署方案（后端端口8080）

---

## 第一阶段：在有网络的环境准备部署包

### 步骤1：前端配置修改（必须）

由于是离线部署，前端需要正确配置 API 地址。

**修改 `frontend/src/axios.ts` 文件：**

```typescript
// 修改第4行，根据您的服务器IP或域名配置
const instance = axios.create({
  // 如果服务器有域名，使用域名
  // baseURL: 'http://your-server-ip:8080/api',  // 或者使用您的域名
  baseURL: 'http://localhost:8080/api',  // 保持原样也可以，如果在同一台机器访问
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json'
  }
})
```

### 步骤2：前端打包

```bash
cd /home/jichong/Projects/TinyWiki/frontend

# 安装依赖
npm install

# 打包
npm run build
```

### 步骤3：创建离线部署所需的文件

在项目根目录创建以下文件：

**1. Dockerfile（在项目根目录）：**

```dockerfile
# Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装系统依赖（用于处理 PDF、图片等）
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY knowledge_base/ ./knowledge_base/

# 工作目录
WORKDIR /app/knowledge_base

# 暴露端口（改为8080）
EXPOSE 8080

# 启动命令
CMD ["gunicorn", "knowledge_base.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120"]
```

**2. docker-compose.yml（在项目根目录）：**

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: tinywiki
      POSTGRES_USER: tinywiki_user
      POSTGRES_PASSWORD: tinywiki_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: always

  web:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn knowledge_base.wsgi:application --bind 0.0.0.0:8080 --workers 4 --timeout 120"
    volumes:
      - ./knowledge_base:/app/knowledge_base
      - static_volume:/app/knowledge_base/staticfiles
      - media_volume:/app/knowledge_base/media
      - storage_volume:/app/knowledge_base/storage
    ports:
      - "8080:8080"
    depends_on:
      - db
    environment:
      - DEBUG=False
      - SECRET_KEY=django-insecure-8q*4d2@=q@w$f%i@kqsdf0#$if=+ou&&3^6bnko&!l2c#zeh%n
      - ALLOWED_HOSTS=*
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
  postgres_data:
  static_volume:
  media_volume:
  storage_volume:
```

**3. nginx.conf（在项目根目录）：**

```nginx
server {
    listen 80;
    server_name localhost;

    # 前端
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # 静态文件
    location /static/ {
        alias /app/knowledge_base/staticfiles/;
    }

    # 媒体文件
    location /media/ {
        alias /app/knowledge_base/media/;
    }

    # 存储文件
    location /storage/ {
        alias /app/knowledge_base/storage/;
    }

    # API 代理到后端8080端口
    location /api/ {
        proxy_pass http://web:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 上传大小限制
    client_max_body_size 100M;
}
```

**4. 创建 .dockerignore 文件（避免复制不必要的文件）：**

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
ENV/
.pytest_cache/
.git/
.gitignore
*.log
.vscode/
.idea/
*.swp
*.swo
*~
node_modules/
frontend/node_modules/
```

### 步骤4：在有网络的环境拉取 Docker 镜像

```bash
cd /home/jichong/Projects/TinyWiki

# 拉取所需的 Docker 镜像
docker pull postgres:15-alpine
docker pull nginx:alpine
docker pull python:3.11-slim

# 构建我们自己的 web 镜像
docker-compose build web
```

### 步骤5：保存 Docker 镜像到文件

```bash
# 保存镜像
docker save -o postgres-15-alpine.tar postgres:15-alpine
docker save -o nginx-alpine.tar nginx:alpine
docker save -o python-311-slim.tar python:3.11-slim
docker save -o tinywiki-web.tar tinywiki_web:latest

# 或者一次性保存所有镜像
docker save postgres:15-alpine nginx:alpine python:3.11-slim tinywiki_web:latest -o tinywiki-images.tar
```

### 步骤6：准备完整的部署包

创建一个部署目录并打包所有需要的文件：

```bash
# 创建部署目录
mkdir -p /home/jichong/tinywiki-deploy
cd /home/jichong/tinywiki-deploy

# 复制项目文件（注意不要复制 node_modules 和其他不必要的文件）
cp -r /home/jichong/Projects/TinyWiki/knowledge_base .
cp -r /home/jichong/Projects/TinyWiki/frontend/dist ./frontend-dist
cp /home/jichong/Projects/TinyWiki/requirements.txt .
cp /home/jichong/Projects/TinyWiki/Dockerfile .
cp /home/jichong/Projects/TinyWiki/docker-compose.yml .
cp /home/jichong/Projects/TinyWiki/nginx.conf .
cp /home/jichong/Projects/TinyWiki/.dockerignore .

# 复制镜像文件
cp /home/jichong/Projects/TinyWiki/tinywiki-images.tar .

# 创建离线部署说明文件
cat > DEPLOY_README.md << 'EOF'
# TinyWiki 离线部署说明

## 前置要求
1. 目标服务器已安装 Docker 和 Docker Compose
2. 服务器有足够的磁盘空间（至少 5GB）

## 部署步骤

1. 加载 Docker 镜像
   ```bash
   docker load -i tinywiki-images.tar
   ```

2. 启动服务
   ```bash
   docker-compose up -d
   ```

3. 创建超级管理员（可选）
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. 访问应用
   - 前端：http://服务器IP
   - 后端API：http://服务器IP:8080/api
   - Django Admin：http://服务器IP:8080/admin

## 常用命令

查看服务状态：
```bash
docker-compose ps
```

查看日志：
```bash
docker-compose logs -f
```

停止服务：
```bash
docker-compose down
```

重启服务：
```bash
docker-compose restart
```

## 数据备份

数据库备份：
```bash
docker-compose exec db pg_dump -U tinywiki_user tinywiki > backup.sql
```

文件备份：
```bash
# 备份存储文件
docker run --rm -v tinywiki_storage_volume:/data -v $(pwd):/backup alpine tar czf /backup/storage-backup.tar.gz -C /data .
```
EOF

# 回到上级目录并打包整个部署包
cd /home/jichong
tar czf tinywiki-deploy-package.tar.gz tinywiki-deploy/
```

---

## 第二阶段：在离线服务器部署

### 步骤1：准备离线服务器

确保离线服务器已安装 Docker 和 Docker Compose：

```bash
# 检查 Docker 版本
docker --version

# 检查 Docker Compose 版本
docker-compose --version
```

**如果没有安装 Docker 和 Docker Compose，请先在有网络的环境下载安装包，然后在离线服务器安装。**

### 步骤2：传输部署包到离线服务器

使用您喜欢的方式（如U盘、移动硬盘、SCP等）将 `tinywiki-deploy-package.tar.gz` 传输到离线服务器。

### 步骤3：在离线服务器解压部署包

```bash
# 解压
tar xzf tinywiki-deploy-package.tar.gz
cd tinywiki-deploy
```

### 步骤4：加载 Docker 镜像

```bash
# 加载镜像
docker load -i tinywiki-images.tar

# 或者如果是分开的镜像文件
# docker load -i postgres-15-alpine.tar
# docker load -i nginx-alpine.tar
# docker load -i python-311-slim.tar
# docker load -i tinywiki-web.tar

# 验证镜像已加载
docker images
```

### 步骤5：修改配置（如果需要）

**如果您需要修改后端端口或者其他配置，先修改以下文件：**

1. **修改后端地址配置**（如果服务器有固定IP或域名）：
   - 修改 `frontend-dist/` 中的前端配置（如果前端需要调用特定IP）

2. **修改 `docker-compose.yml` 中的环境变量**（可选）：
   - `SECRET_KEY`：生产环境请修改为更安全的密钥
   - `ALLOWED_HOSTS`：如果需要限制访问的域名

### 步骤6：启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志，确认服务正常启动
docker-compose logs -f
```

### 步骤7：创建超级管理员（可选但推荐）

```bash
docker-compose exec web python manage.py createsuperuser
```

按提示输入用户名、邮箱和密码。

### 步骤8：验证部署

在浏览器中访问：

- **前端页面**：`http://服务器IP地址`
- **后端API**：`http://服务器IP地址:8080/api`
- **Django Admin**：`http://服务器IP地址:8080/admin`

---

## 第三阶段：运维管理

### 常用命令

```bash
# 查看所有服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f
docker-compose logs -f web
docker-compose logs -f db

# 停止服务
docker-compose down

# 启动服务
docker-compose up -d

# 重启服务
docker-compose restart

# 进入 web 容器
docker-compose exec web bash
```

### 数据备份

#### 1. 数据库备份

```bash
# 备份数据库
docker-compose exec db pg_dump -U tinywiki_user tinywiki > tinywiki-db-backup-$(date +%Y%m%d).sql

# 恢复数据库
cat tinywiki-db-backup-20230101.sql | docker-compose exec -T db psql -U tinywiki_user tinywiki
```

#### 2. 文件备份

```bash
# 备份存储文件
docker run --rm -v tinywiki_storage_volume:/data -v $(pwd):/backup alpine tar czf storage-backup-$(date +%Y%m%d).tar.gz -C /data .

# 备份媒体文件
docker run --rm -v tinywiki_media_volume:/data -v $(pwd):/backup alpine tar czf media-backup-$(date +%Y%m%d).tar.gz -C /data .

# 备份静态文件
docker run --rm -v tinywiki_static_volume:/data -v $(pwd):/backup alpine tar czf static-backup-$(date +%Y%m%d).tar.gz -C /data .

# 恢复存储文件
docker run --rm -v tinywiki_storage_volume:/data -v $(pwd):/backup alpine tar xzf /backup/storage-backup-20230101.tar.gz -C /data
```

### 更新应用

如果需要更新应用，需要在有网络的环境重新构建镜像，然后传输到离线服务器：

```bash
# 在有网络的环境
docker-compose build web
docker save -o tinywiki-web-new.tar tinywiki_web:latest

# 传输到离线服务器，然后
docker-compose stop web
docker-compose rm -f web
docker load -i tinywiki-web-new.tar
docker-compose up -d web
```

---

## 注意事项

1. **防火墙配置**：确保服务器的 80 和 8080 端口对外开放
2. **存储空间**：确保有足够的磁盘空间存储上传的文件和数据库
3. **SECRET_KEY**：生产环境务必修改 `docker-compose.yml` 中的 SECRET_KEY
4. **数据备份**：定期备份数据库和存储文件
5. **日志监控**：定期查看日志，确保系统正常运行
6. **权限设置**：确保 Docker 有足够的权限访问挂载的卷
