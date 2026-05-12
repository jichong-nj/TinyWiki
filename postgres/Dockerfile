# 基于 pgvector 官方镜像，添加 zhparser 中文分词
FROM pgvector/pgvector:pg16

# 配置国内 apt 镜像（阿里云）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list 2>/dev/null || true; \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list 2>/dev/null || true

# 安装编译依赖
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    postgresql-server-dev-16 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 手动下载安装 SCWS（zhparser 依赖）- 使用官方源
RUN wget -qO- http://www.xunsearch.com/scws/down/scws-1.2.3.tar.bz2 | tar xj -C /tmp \
    && cd /tmp/scws-1.2.3 \
    && ./configure \
    && make \
    && make install \
    && rm -rf /tmp/scws-1.2.3

# 安装 zhparser 中文分词插件
RUN git clone --depth=1 https://gitcode.com/gh_mirrors/zh/zhparser.git /tmp/zhparser \
    && cd /tmp/zhparser \
    && make \
    && make install \
    && rm -rf /tmp/zhparser

# 配置完成！
