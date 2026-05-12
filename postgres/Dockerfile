# 基于 pgvector 官方镜像，添加中文分词支持
FROM pgvector/pgvector:pg16

# 配置国内 apt 镜像（阿里云）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list 2>/dev/null || true
RUN sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list 2>/dev/null || true
RUN sed -i 's/apt.postgresql.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/pgdg.list 2>/dev/null || true

# 安装编译依赖
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    postgresql-server-dev-16 \
    wget \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# 安装 pg_jieba 中文分词插件（使用 gitee 镜像加速）
RUN git clone --depth=1 https://gitee.com/mirrors/pg_jieba.git /tmp/pg_jieba \
    && cd /tmp/pg_jieba \
    && git submodule update --init --recursive \
    && mkdir -p build \
    && cd build \
    && cmake .. \
    && make \
    && make install \
    && rm -rf /tmp/pg_jieba

# 配置完成！
