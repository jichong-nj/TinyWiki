# 基于 pgvector 官方镜像，添加中文分词支持
FROM pgvector/pgvector:pg16

# 安装编译依赖
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    postgresql-server-dev-16 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 安装 pg_jieba 中文分词插件
RUN git clone --depth=1 https://github.com/jaiminpan/pg_jieba.git /tmp/pg_jieba \
    && cd /tmp/pg_jieba \
    && git submodule update --init --recursive \
    && mkdir -p build \
    && cd build \
    && cmake .. \
    && make \
    && make install \
    && rm -rf /tmp/pg_jieba

# 配置完成！
