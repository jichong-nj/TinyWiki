# 知识库管理系统 - 实现计划

## [ ] Task 1: 项目初始化与基础配置
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 创建 Django 项目和应用结构
  - 配置数据库连接（SQLite/PostgreSQL）
  - 配置 DRF、认证、跨域等基础设置
- **Acceptance Criteria Addressed**: None（基础设施）
- **Test Requirements**:
  - `programmatic` TR-1.1: Django 项目启动成功，数据库连接正常
  - `programmatic` TR-1.2: DRF API 基础配置生效，返回正确响应格式

## [ ] Task 2: 用户认证模块实现
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 实现账号密码登录/注册接口
  - 实现 JWT Token 认证机制
  - 实现用户管理接口（CRUD）
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: POST /api/auth/login 正确返回 JWT Token
  - `programmatic` TR-2.2: Token 过期时间正确（24小时）
  - `programmatic` TR-2.3: 无效凭证返回 401 状态码

## [ ] Task 3: 核心数据模型设计与实现
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 实现知识库（KnowledgeBase）模型
  - 实现知识目录（Directory）模型
  - 实现文件夹（Folder）模型
  - 实现文档（Document）模型
  - 实现文档版本（DocumentVersion）模型
  - 实现权限关联（Permission）模型
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-3.1: 三级目录结构数据关系正确
  - `programmatic` TR-3.2: 文档版本自动递增（v1, v2, v3...）
  - `programmatic` TR-3.3: 文档状态字段正确存储（发布状态、分析状态）

## [ ] Task 4: 文件导入与格式转换模块
- **Priority**: P0
- **Depends On**: Task 3
- **Description**: 
  - 实现文件上传接口
  - 集成 Markdown/Word/PPT/PDF 转 Markdown 的转换工具
  - 实现批量导入功能
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-4.1: 上传 .md 文件直接存储成功
  - `programmatic` TR-4.2: 上传 .docx/.pptx/.pdf 文件正确转换为 Markdown
  - `programmatic` TR-4.3: 批量导入多个文件成功

## [ ] Task 5: 目录管理 API 实现
- **Priority**: P0
- **Depends On**: Task 3
- **Description**: 
  - 实现知识库 CRUD 接口
  - 实现知识目录 CRUD 接口
  - 实现文件夹 CRUD 接口
  - 实现目录树结构查询接口
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-5.1: 知识库创建/删除/更新功能正常
  - `programmatic` TR-5.2: 知识目录创建/删除/更新功能正常
  - `programmatic` TR-5.3: 目录树接口返回正确的层级结构

## [ ] Task 6: 权限管理 API 实现
- **Priority**: P0
- **Depends On**: Task 2, Task 3
- **Description**: 
  - 实现权限分配接口（为目录分配管理员）
  - 实现权限验证中间件
  - 实现权限查询接口
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-6.1: 目录管理员只能访问授权目录下的内容
  - `programmatic` TR-6.2: 超级管理员可以管理所有目录
  - `programmatic` TR-6.3: 普通成员只能访问授权目录

## [ ] Task 7: 文档编辑与预览 API
- **Priority**: P0
- **Depends On**: Task 3, Task 6
- **Description**: 
  - 实现文档创建/编辑接口
  - 实现文档预览接口
  - 实现文档删除接口
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: 文档创建成功，自动生成 v1 版本
  - `programmatic` TR-7.2: 文档编辑成功，自动生成新版本
  - `programmatic` TR-7.3: 无权限用户无法编辑文档

## [ ] Task 8: 文档状态管理 API
- **Priority**: P0
- **Depends On**: Task 3, Task 6
- **Description**: 
  - 实现文档发布接口（未发布 → 已发布）
  - 实现分析状态更新接口
  - 实现状态查询接口
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-8.1: 发布文档后状态变为"已发布"
  - `programmatic` TR-8.2: 已发布文档无法撤回
  - `programmatic` TR-8.3: 分析状态正确更新

## [ ] Task 9: 版本管理 API
- **Priority**: P0
- **Depends On**: Task 3, Task 7
- **Description**: 
  - 实现版本历史查询接口
  - 实现版本对比接口
  - 实现版本回滚接口
- **Acceptance Criteria Addressed**: AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-9.1: 版本历史按时间倒序排列
  - `programmatic` TR-9.2: 版本对比返回正确的 diff 结果
  - `programmatic` TR-9.3: 版本回滚后生成新的版本号

## [ ] Task 10: AI 模型配置管理
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 实现 AI 模型配置数据模型
  - 实现配置 CRUD 接口
  - 实现测试连接接口
  - API Key 加密存储
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-10.1: API Key 在数据库中加密存储
  - `programmatic` TR-10.2: 测试连接接口正确验证模型连通性
  - `programmatic` TR-10.3: 配置按优先级（全局 → 知识库 → 目录）生效

## [ ] Task 11: 文档分析异步任务
- **Priority**: P0
- **Depends On**: Task 8, Task 10
- **Description**: 
  - 实现 Celery 异步任务队列
  - 实现 embedding 生成任务
  - 实现全文索引构建任务
  - 实现分析状态更新
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-11.1: 文档发布后自动进入分析队列
  - `programmatic` TR-11.2: 分析完成后状态正确更新
  - `programmatic` TR-11.3: 文档修改后自动重新分析

## [ ] Task 12: 全文搜索与 RAG 检索 API
- **Priority**: P0
- **Depends On**: Task 3, Task 11
- **Description**: 
  - 实现全文搜索接口
  - 实现 embedding 语义检索接口
  - 实现 Rerank 重排序
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `programmatic` TR-12.1: 全文搜索返回相关文档
  - `programmatic` TR-12.2: 语义检索返回语义相关文档
  - `programmatic` TR-12.3: Rerank 提升检索结果相关性

## [ ] Task 13: 智能问答 API
- **Priority**: P1
- **Depends On**: Task 10, Task 12
- **Description**: 
  - 实现智能问答接口
  - 实现知识范围过滤
  - 实现引用来源展示
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `programmatic` TR-13.1: 根据选定知识范围返回回答
  - `human-judgment` TR-13.2: 回答准确引用知识库内容

## [ ] Task 14: 统计面板 API
- **Priority**: P1
- **Depends On**: Task 3, Task 8
- **Description**: 
  - 实现未发布文档统计接口
  - 实现待分析文档统计接口
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `programmatic` TR-14.1: 未发布文档数统计正确
  - `programmatic` TR-14.2: 待分析文档数统计正确

## [ ] Task 15: Vue 前端项目初始化
- **Priority**: P1
- **Depends On**: Task 1
- **Description**: 
  - 使用 Vite 创建 Vue 3 + TypeScript 项目
  - 安装 Element Plus 组件库
  - 配置 Vue Router
  - 配置 Pinia 状态管理
  - 配置 Axios 拦截器（JWT Token 处理）
- **Acceptance Criteria Addressed**: None（基础设施）
- **Test Requirements**:
  - `programmatic` TR-15.1: Vue 项目启动成功
  - `programmatic` TR-15.2: Element Plus 组件正常渲染
  - `programmatic` TR-15.3: 路由跳转正常

## [ ] Task 16: 后台管理前端页面（基础框架）
- **Priority**: P1
- **Depends On**: Task 2, Task 15
- **Description**: 
  - 创建登录页面（Vue + Element Plus）
  - 创建左侧导航栏（Logo + 菜单：文档、统计、贡献、问答、反馈、发布、设置）
  - 创建顶部导航栏（知识库名称、搜索框、切换Wiki按钮、系统配置）
  - 创建侧边栏目录树组件
- **Acceptance Criteria Addressed**: AC-2, AC-11, AC-12
- **Test Requirements**:
  - `human-judgment` TR-16.1: 登录页面功能正常
  - `human-judgment` TR-16.2: 左侧导航栏展示正确的菜单项
  - `human-judgment` TR-16.3: 顶部导航栏展示当前知识库和统计数据
  - `human-judgment` TR-16.4: 侧边栏目录树支持展开/折叠

## [ ] Task 17: 后台管理前端页面（文档管理）
- **Priority**: P1
- **Depends On**: Task 16
- **Description**: 
  - 创建文档列表页（三级布局：目录树 | 文件列表 | 操作区）
  - 创建文档编辑页（Markdown 编辑器，使用 TipTap 或 Markdown-it）
  - 创建版本历史页（版本对比使用 diff 库）
  - 实现文件状态标签（学习实践、可编辑、可执行等）
- **Acceptance Criteria Addressed**: AC-4, AC-6, AC-7, AC-13, AC-14
- **Test Requirements**:
  - `human-judgment` TR-17.1: 文档列表展示正确，支持筛选
  - `human-judgment` TR-17.2: 文件状态标签显示正确
  - `human-judgment` TR-17.3: Markdown 编辑器左右分屏预览正常
  - `human-judgment` TR-17.4: 版本历史和对比功能正常

## [ ] Task 18: 后台管理前端页面（权限与配置）
- **Priority**: P1
- **Depends On**: Task 16
- **Description**: 
  - 创建权限管理页面
  - 创建 AI 模型配置页面
- **Acceptance Criteria Addressed**: AC-3, AC-8
- **Test Requirements**:
  - `human-judgment` TR-18.1: 权限分配功能正常
  - `human-judgment` TR-18.2: AI 模型配置页面支持测试连接

## [ ] Task 19: Wiki 站点前端页面
- **Priority**: P0
- **Depends On**: Task 2, Task 12, Task 13, Task 15
- **Description**: 
  - 创建 Wiki 登录页面
  - 创建顶部导航栏（知识库选择器、搜索框、智能问答入口）
  - 创建侧边栏目录树
  - 创建文档浏览页（TOC 导航，滚动联动）
  - 创建智能问答弹窗组件
- **Acceptance Criteria Addressed**: AC-9, AC-10
- **Test Requirements**:
  - `human-judgment` TR-19.1: Wiki 登录功能正常
  - `human-judgment` TR-19.2: 文档浏览页面渲染正常，TOC 滚动联动
  - `human-judgment` TR-19.3: 智能问答窗口功能正常，引用来源正确

## [ ] Task 20: 部署与集成
- **Priority**: P2
- **Depends On**: 所有 Task
- **Description**: 
  - 配置 Docker 容器化部署
  - 配置 Nginx 反向代理
  - 配置 SSL/TLS
  - 部署 Redis 缓存
- **Acceptance Criteria Addressed**: None（部署）
- **Test Requirements**:
  - `programmatic` TR-19.1: Docker 容器启动成功
  - `programmatic` TR-19.2: API 接口正常响应