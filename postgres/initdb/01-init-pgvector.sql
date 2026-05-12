-- 初始化 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建中文文本搜索配置（基于 simple，因为 pgvector 镜像可能没有 jieba）
CREATE TEXT SEARCH CONFIGURATION IF NOT EXISTS chinese (COPY = simple);
