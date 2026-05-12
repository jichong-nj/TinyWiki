# 基于 pgvector 官方镜像，添加中文分词支持
FROM pgvector/pgvector:pg16

# 安装编译依赖
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    postgresql-server-dev-16 \
    libscws-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 安装 zhparser 中文分词插件
RUN git clone --depth=1 https://github.com/amutu/zhparser.git /tmp/zhparser \
    && cd /tmp/zhparser \
    && make \
    && make install \
    && rm -rf /tmp/zhparser

# 配置完成！
