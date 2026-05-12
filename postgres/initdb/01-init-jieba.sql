-- 初始化 jieba 中文分词
-- 这个镜像应该已经预装了 pg_jieba

-- 创建 jieba 扩展（如果还没有的话）
CREATE EXTENSION IF NOT EXISTS pg_jieba;

-- 创建中文文本搜索配置
CREATE TEXT SEARCH CONFIGURATION IF NOT EXISTS chinese (COPY = simple);
ALTER TEXT SEARCH CONFIGURATION chinese 
    ALTER MAPPING FOR asciiword, word, hword, numword 
    WITH jieba;
