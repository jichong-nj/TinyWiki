-- 手动初始化脚本
-- 如果自动初始化没成功，手动执行这个脚本

\c tinywiki

-- 1. 创建扩展
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS zhparser;

-- 2. 创建中文搜索配置
DROP TEXT SEARCH CONFIGURATION IF EXISTS chinese;
CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);
ALTER TEXT SEARCH CONFIGURATION chinese 
    ADD MAPPING FOR n,v,a,i,e,l,x WITH simple;

-- 验证
\dF
SELECT '初始化完成！' AS status;
