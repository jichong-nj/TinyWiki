# pgvector 安装和部署指南

## 概述

我们已经将系统从 Python 层的向量计算切换到使用 PostgreSQL 的 pgvector 插件进行向量搜索。

## 本地开发环境安装

### 方法一：使用 Docker（推荐）

这是最简单的方法，我们已经配置好了！

1. **停止旧服务（如果在运行）**
   ```bash
   cd /path/to/your/project
   docker-compose down
   ```

2. **删除旧数据目录（重要！因为数据库格式变了）**
   ```bash
   sudo rm -rf ./postgres_data
   ```

3. **重新构建并启动**
   ```bash
   docker-compose up -d
   ```

4. **应用数据库迁移**
   ```bash
   # 进入 web 容器
   docker-compose exec web bash
   
   # 运行迁移
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **重新发布文档（因为向量字段变了）**
   - 需要重新发布已有文档，让系统用 pgvector 重新生成向量

---

### 方法二：本地 PostgreSQL 安装 pgvector

如果你在本地直接运行 PostgreSQL（不用 Docker）：

#### Ubuntu/Debian:
```bash
# 安装 PostgreSQL 开发包
sudo apt-get install -y postgresql-server-dev-15

# 安装 pgvector
cd /tmp
git clone --branch v0.7.0 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

#### macOS:
```bash
# 使用 Homebrew
brew install postgresql@15 pgvector
```

#### 安装后启用扩展：
```sql
-- 连接到你的数据库
psql -U your_user -d your_db

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 内网部署

### 1. 导出镜像
```bash
# 拉取 pgvector 镜像
docker pull pgvector/pgvector:pg16

# 导出为 tar 文件
docker save -o pgvector-pg16.tar pgvector/pgvector:pg16
docker save -o tinywiki-web.tar tinywiki-web:latest
```

### 2. 传输到内网机器
```bash
scp pgvector-pg16.tar user@internal-server:/path/to/target/
scp tinywiki-web.tar user@internal-server:/path/to/target/
```

### 3. 导入镜像
```bash
docker load -i pgvector-pg16.tar
docker load -i tinywiki-web.tar
```

### 4. 部署
```bash
cd /path/to/project
docker-compose down
# 备份数据（如果需要）
sudo mv ./postgres_data ./postgres_data_backup
# 重新启动
docker-compose up -d
# 运行迁移
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

---

## 数据库迁移说明

### 新增的迁移
我们修改了 `DocumentChunk` 模型：
- 新增 `embedding_vector` 字段（VectorField，1024维）
- 保留旧的 `embedding` 字段用于兼容

### 迁移步骤
```bash
# 1. 生成迁移文件
python manage.py makemigrations

# 2. 应用迁移
python manage.py migrate
```

### 数据迁移
迁移后，**需要重新发布文档**才能在新字段中生成向量。

---

## 验证安装

### 检查 pgvector 是否安装成功
```bash
docker-compose exec db psql -U tinywiki_user -d tinywiki -c "\dx"
```

应该能看到 `vector` 扩展已安装！

### 测试向量搜索
```sql
-- 测试 pgvector 功能
SELECT '[1,2,3]'::vector;
```

---

## 常见问题

### Q: 旧数据怎么办？
A: 需要重新发布文档，系统会自动用 pgvector 重新生成向量。

### Q: 我想保留旧数据？
A: 可以写一个数据迁移脚本，把旧的 JSON 向量数据转换到新的 pgvector 字段。

### Q: 性能怎么样？
A: pgvector 比 Python 层计算快很多！特别是数据量大的时候。

---

## 回滚方案

如果遇到问题需要回滚：

```bash
# 1. 停止服务
docker-compose down

# 2. 恢复旧数据
sudo mv ./postgres_data_backup ./postgres_data

# 3. 用旧配置启动（修改 docker-compose.yml 换回 postgres:15-alpine）

# 4. 回滚代码（git）
git stash
```

---

## 性能优化建议

### 1. 添加 HNSW 索引（数据量大的时候）
```sql
CREATE INDEX ON documents_documentchunk USING hnsw (embedding_vector vector_cosine_ops);
```

### 2. 调整向量维度
如果需要不同的维度（比如 768），修改模型：
```python
embedding_vector = VectorField(dimensions=768, null=True, blank=True)
```

---

## 参考链接

- pgvector GitHub: https://github.com/pgvector/pgvector
- pgvector Django: https://github.com/pgvector/pgvector-python
