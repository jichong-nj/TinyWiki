# TinyWiki - 企业级知识库管理系统

TinyWiki 是一个基于 Django + Vue + PostgreSQL 的企业级知识库管理系统，支持文档管理、全文搜索、AI 问答和权限管理等功能。

---

## 功能特性

- 📚 **知识库管理**：创建和管理多个知识库，按业务或部门划分
- 📄 **文档管理**：支持 Markdown 编辑、多种文件格式导入（Word/PPT/PDF/Excel/Markdown/TXT）
- 🔍 **智能搜索**：结合全文索引和向量检索，支持关键词搜索和语义搜索
- 🤖 **AI 助手**：基于 RAG 的智能问答，支持多轮对话
- 🔐 **权限管理**：支持知识库级和目录级权限分配，支持管理员和普通用户角色
- 🐳 **Docker 部署**：一键部署，支持内网离线部署

---

## 技术栈

- **后端**：Django + Django REST Framework
- **前端**：Vue 3 + TypeScript + Vite
- **数据库**：PostgreSQL + pgvector + zhparser（中文分词）
- **搜索**：PostgreSQL 全文索引 + pgvector 向量检索
- **部署**：Docker + Docker Compose + Nginx

---

## 快速开始（Docker 模式）

### 前置要求

- Docker 和 Docker Compose 已安装
- 4GB+ 内存

### 1. 克隆项目

```bash
git clone <repository-url>
cd TinyWiki
```

### 2. 启动服务

```bash
# 首次启动（会构建镜像并初始化数据库）
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
```

### 3. 访问系统

- 前端地址：http://localhost
- 后端 API：http://localhost:8080
- Django Admin：http://localhost:8080/admin/

---

## 创建管理员用户

### 方法一：通过 Docker 命令创建

```bash
# 进入 web 容器
docker compose exec web python manage.py createsuperuser
```

按照提示输入：
- 用户名（Username）
- 邮箱（Email address，可选）
- 密码（Password，需要输入两次）

### 方法二：通过 Django Admin 创建

1. 访问 http://localhost:8080/admin/
2. 登录后在 Users 部分添加新用户
3. 可以设置用户权限和角色

---

## 进入数据库

### 进入 PostgreSQL 容器

```bash
# 进入数据库容器
docker compose exec db psql -U tinywiki_user -d tinywiki
```

### 常用数据库操作

```sql
-- 查看所有表
\dt

-- 查看文本搜索配置
\dF

-- 测试中文分词
SELECT to_tsvector('chinese', '这是一段中文测试文本');

-- 退出
\q
```

### 数据库备份和恢复

```bash
# 备份数据库
docker compose exec db pg_dump -U tinywiki_user tinywiki > backup_$(date +%Y%m%d).sql

# 恢复数据库
cat backup_20260512.sql | docker compose exec -T db psql -U tinywiki_user tinywiki
```

---

## 配置 AI 模型

1. 使用管理员账号登录系统
2. 点击左下角"管理后台"
3. 进入"系统设置"页面
4. 配置以下模型：
   - **文本生成模型**：对话用的大语言模型
   - **Embedding 模型**：用于向量检索
   - **Rerank 模型**（可选）：用于重排序搜索结果

所有模型支持 OpenAI 兼容的 API 接口。

---

## 内网离线部署

### 1. 打包部署包

```bash
# 运行打包脚本
./package.sh
```

脚本会生成 `dist/tinywiki-deploy-v1.0.0.tar.gz`，包含：
- 所有 Docker 镜像
- docker-compose 配置
- 初始化脚本
- 部署说明文档

### 2. 内网部署

```bash
# 1. 解压部署包
tar -xzf tinywiki-deploy-v1.0.0.tar.gz
cd tinywiki-deploy-v1.0.0

# 2. 加载 Docker 镜像
docker load -i tinywiki-postgres.tar
docker load -i tinywiki-web.tar
docker load -i tinywiki-nginx.tar

# 3. 启动服务
docker compose -f docker-compose.prod.yml up -d
```

详细部署说明请参考 `DEPLOY.md` 文件。

---

## 目录结构

```
TinyWiki/
├── docs/                    # 文档目录
│   ├── 知识库使用说明.md
│   └── 管理员使用说明.md
├── frontend/                # 前端代码（Vue 3）
├── knowledge_base/          # 后端代码（Django）
│   ├── accounts/            # 用户账户模块
│   ├── api/                 # API 模块
│   ├── documents/           # 文档管理模块
│   └── knowledge_base/      # Django 项目配置
├── postgres/                # PostgreSQL 配置
│   ├── Dockerfile           # 自定义数据库镜像
│   └── initdb/              # 数据库初始化脚本
├── docker-compose.yml       # 开发环境配置
├── docker-compose.prod.yml  # 生产环境配置
├── package.sh               # 打包脚本
└── README.md                # 本文件
```

---

## 常见问题

### Q: 如何查看服务日志？

```bash
# 查看所有服务日志
docker compose logs -f

# 只查看 web 服务日志
docker compose logs -f web

# 只查看 db 服务日志
docker compose logs -f db
```

### Q: 如何重启服务？

```bash
# 重启所有服务
docker compose restart

# 重启某个服务
docker compose restart web
```

### Q: 数据库初始化失败怎么办？

如果自动初始化失败，可以手动执行初始化脚本：

```bash
# 进入数据库容器
docker compose exec db psql -U tinywiki_user -d tinywiki

# 在 psql 中执行手动初始化脚本
\i /docker-entrypoint-initdb.d/init-manual.sql
```

### Q: AI 功能无法使用？

1. 检查系统设置中的 AI 配置
2. 确认 API Key 和 Base URL 正确
3. 在配置页面点击"测试"按钮验证连接

---

## 文档

更多详细文档请参考：
- [知识库使用说明](docs/知识库使用说明.md) - 普通用户使用指南
- [管理员使用说明](docs/管理员使用说明.md) - 管理员操作指南

---

## License

MIT License
