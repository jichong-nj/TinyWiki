-- 初始化所有扩展脚本，只会在 PostgreSQL 数据目录为空、容器首次初始化数据库时运行一次。

-- 1. 创建 pgvector 扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 创建 zhparser 中文分词扩展
CREATE EXTENSION IF NOT EXISTS zhparser;

-- 3. 使用 zhparser 创建中文文本搜索配置
-- 先删除已存在的配置，再创建
DROP TEXT SEARCH CONFIGURATION IF EXISTS chinese;
CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);

-- 4. 配置中文分词映射
ALTER TEXT SEARCH CONFIGURATION chinese 
    ADD MAPPING FOR n,v,a,i,e,l,x WITH simple;

-- ============================================
-- 🧪 测试验证语句
-- ============================================

-- 测试 1：验证中文分词
SELECT '测试 1：中文分词' AS test;
SELECT to_tsvector('chinese', '这是一段中文测试文本，用来验证分词效果') AS 分词结果;

-- 测试 2：验证 pgvector
SELECT '测试 2：pgvector 向量操作' AS test;
SELECT '[1,2,3]'::vector(3) AS v1, '[4,5,6]'::vector(3) AS v2;
SELECT '[1,2,3]'::vector(3) <=> '[4,5,6]'::vector(3) AS 余弦距离;
SELECT '[1,2,3]'::vector(3) <-> '[4,5,6]'::vector(3) AS L2距离;

SELECT '✅ 初始化完成！' AS status;
