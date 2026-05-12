-- 初始化所有扩展
-- 这个脚本会在数据库首次创建时自动执行

-- 1. 创建 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 创建 zhparser 中文分词扩展
CREATE EXTENSION IF NOT EXISTS zhparser;

-- 3. 使用 zhparser 创建中文文本搜索配置
CREATE TEXT SEARCH CONFIGURATION IF NOT EXISTS chinese (PARSER = zhparser);

-- 4. 配置中文分词映射
ALTER TEXT SEARCH CONFIGURATION chinese 
    ADD MAPPING FOR n,v,a,i,e,l WITH simple;
