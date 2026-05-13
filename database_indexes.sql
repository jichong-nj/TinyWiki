-- ============================================
-- TinyWiki 数据库索引优化脚本
-- 生成时间: 2026-05-12
-- ============================================

-- ============================================
-- 1. 基础索引（性能优化）
-- ============================================

-- Document 表索引
-- 发布状态索引（最常用查询）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_document_publish_status
ON documents_document (publish_status);

-- 分析状态索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_document_analysis_status
ON documents_document (analysis_status);

-- 目录索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_document_directory
ON documents_document (directory_id);

-- 文件夹索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_document_folder
ON documents_document (folder_id);

-- 创建时间索引（用于排序）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_document_created_at
ON documents_document (created_at DESC);

-- 更新时间索引（用于排序）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_document_updated_at
ON documents_document (updated_at DESC);

-- 文件名索引（唯一性检查）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_document_filename
ON documents_document (filename);

-- ============================================
-- 2. 复合索引（多条件查询优化）
-- ============================================

-- 发布状态 + 目录（文档树查询）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_document_publish_directory
ON documents_document (publish_status, directory_id)
WHERE publish_status = 'published';

-- 发布状态 + 文件夹（文件夹内文档查询）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_document_publish_folder
ON documents_document (publish_status, folder_id)
WHERE publish_status = 'published';

-- 目录 + 文件夹 + 发布状态（复杂文档查询）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_document_directory_folder_publish
ON documents_document (directory_id, folder_id, publish_status);

-- ============================================
-- 3. 全文搜索索引（已存在，但确认配置）
-- ============================================

-- 确认全文搜索索引存在
-- 注意：search_vector 字段的索引由Django自动管理
-- 如果需要手动创建，可以使用：
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_document_search_vector
-- ON documents_document USING gin (search_vector);

-- ============================================
-- 4. DocumentChunk 表索引（向量搜索优化）
-- ============================================

-- 文档关联索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documentchunk_document
ON documents_documentchunk (document_id);

-- chunk索引（顺序读取）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documentchunk_chunk_index
ON documents_documentchunk (chunk_index);

-- 向量索引（pgvector）
-- 注意：pgvector 会自动为 VectorField 创建合适的索引
-- 如果需要手动创建，可以使用：
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documentchunk_embedding_vector
-- ON documents_documentchunk USING ivfflat (embedding_vector vector_cosine_ops)
-- WITH (lists = 100);

-- ============================================
-- 5. Folder 表索引（树形结构优化）
-- ============================================

-- 目录索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_folder_directory
ON documents_folder (directory_id);

-- 父文件夹索引（树形查询）
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_folder_parent
ON documents_folder (parent_id);

-- 复合索引：目录 + 父文件夹
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_folder_directory_parent
ON documents_folder (directory_id, parent_id);

-- ============================================
-- 6. Directory 表索引
-- ============================================

-- 知识库索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_directory_knowledge_base
ON documents_directory (knowledge_base_id);

-- ============================================
-- 7. DocumentVersion 表索引
-- ============================================

-- 文档关联索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documentversion_document
ON documents_documentversion (document_id);

-- 版本号索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documentversion_version
ON documents_documentversion (version_number);

-- 复合唯一索引已存在：(document_id, version_number)

-- ============================================
-- 8. Permission 表索引
-- ============================================

-- 用户索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_permission_user
ON documents_permission (user_id);

-- 目录索引
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_permission_directory
ON documents_permission (directory_id);

-- 复合唯一索引已存在：(user_id, directory_id)

-- ============================================
-- 9. 外键约束索引（Django自动创建，但确认）
-- ============================================

-- 确认外键索引存在
-- SELECT
--     tc.table_name,
--     tc.constraint_name,
--     tc.constraint_type,
--     kcu.column_name,
--     ccu.table_name AS foreign_table_name,
--     ccu.column_name AS foreign_column_name
-- FROM information_schema.table_constraints AS tc
-- JOIN information_schema.key_column_usage AS kcu
--   ON tc.constraint_name = kcu.constraint_name
--   AND tc.table_schema = kcu.table_schema
-- JOIN information_schema.constraint_column_usage AS ccu
--   ON ccu.constraint_name = tc.constraint_name
--   AND ccu.table_schema = tc.table_schema
-- WHERE tc.constraint_type = 'FOREIGN KEY'
--   AND tc.table_name LIKE 'documents_%';

-- ============================================
-- 10. 索引维护和监控
-- ============================================

-- 查看索引使用情况
-- SELECT
--     schemaname,
--     tablename,
--     indexname,
--     idx_scan,
--     idx_tup_read,
--     idx_tup_fetch
-- FROM pg_stat_user_indexes
-- WHERE schemaname = 'public'
--   AND tablename LIKE 'documents_%'
-- ORDER BY idx_scan DESC;

-- 查看未使用索引（可能需要清理）
-- SELECT
--     schemaname,
--     tablename,
--     indexname,
--     idx_scan,
--     pg_size_pretty(pg_relation_size(indexrelid)) as index_size
-- FROM pg_stat_user_indexes
-- WHERE schemaname = 'public'
--   AND tablename LIKE 'documents_%'
--   AND idx_scan = 0
-- ORDER BY pg_relation_size(indexrelid) DESC;

-- ============================================
-- 11. 索引重建脚本（如果需要）
-- ============================================

-- 重建所有索引（离线操作，生产环境谨慎使用）
-- REINDEX SCHEMA CONCURRENTLY public;

-- 或者单独重建特定索引
-- REINDEX INDEX CONCURRENTLY idx_document_publish_status;

-- ============================================
-- 12. 性能监控查询
-- ============================================

-- 慢查询分析
-- SELECT
--     query,
--     calls,
--     total_time,
--     mean_time,
--     rows
-- FROM pg_stat_statements
-- WHERE query LIKE '%documents_document%'
--   AND mean_time > 1000  -- 超过1秒的查询
-- ORDER BY mean_time DESC
-- LIMIT 10;

-- 表大小统计
-- SELECT
--     schemaname,
--     tablename,
--     pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
--     pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
--     pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
-- FROM pg_tables
-- WHERE schemaname = 'public'
--   AND tablename LIKE 'documents_%'
-- ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ============================================
-- 执行说明
-- ============================================
-- 1. 在数据库中执行上述CREATE INDEX语句
-- 2. 使用 CONCURRENTLY 选项创建索引，避免阻塞写入操作
-- 3. 监控索引效果和系统性能
-- 4. 定期清理未使用的索引
-- 5. 考虑分区表（如果数据量很大）