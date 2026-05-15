# Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 使用国内 Debian 镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装系统依赖（用于处理 PDF、图片等）
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libpq-dev \
    gcc \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖（使用国内镜像源，利用 BuildKit 缓存加速）
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 复制后端代码
COPY knowledge_base/ ./knowledge_base/

# 工作目录
WORKDIR /app/knowledge_base

# 暴露端口（改为8080）
EXPOSE 8080

# 启动命令
CMD ["gunicorn", "knowledge_base.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120"]

