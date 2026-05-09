# 知识库管理系统 - 产品需求文档

## Overview

- **Summary**: 一个企业级知识库管理系统，支持多种格式文件导入、三级目录结构管理、权限控制、文档版本管理、AI 驱动的 RAG 知识库检索，并提供公开 Wiki 浏览站点。
- **Purpose**: 解决企业内部知识文档的统一管理、版本追溯、智能检索和安全共享问题，提升团队协作效率和知识资产价值。
- **Target Users**: 企业员工、产品经理、技术文档管理员、知识读者等。

## Goals

- 支持批量导入 Markdown/Word/PPT/PDF 文件并自动转换为 Markdown 格式存储
- 实现三级目录结构（知识库 → 知识目录 → 子文件夹/文件）的管理
- 按二级目录（知识目录）进行权限分配和分权治理
- 提供文档版本管理，支持版本对比与回滚
- 实现文档发布流程（草稿 → 已发布）和分析状态管理（embedding + 全文索引）
- 提供公开 Wiki 浏览站点，支持全文检索和 RAG 智能问答
- 集中管理 AI 模型配置（文本生成、Embedding、Rerank、图文分析）

## Non-Goals (Out of Scope)

- 实时协作编辑（多人同时编辑同一文档）
- 离线编辑功能
- 移动端原生应用
- 多语言国际化支持
- 高级报表分析功能

## Background & Context

- **后端**: Django + Django REST Framework 框架
- **前端**: Vue 3 + TypeScript + Vite 构建工具
- **UI 框架**: Element Plus 组件库
- **用户认证**: 账号密码登录 + JWT Token
- **Wiki 站点**: 需要登录才能访问
- **文档分析**: embedding + 全文索引构建（RAG 知识库）

## Functional Requirements

- **FR-1**: 文件导入 - 支持批量导入 Markdown/Word/PPT/PDF 格式，自动转换为 Markdown 存储
- **FR-2**: 目录管理 - 实现三级目录结构的创建、删除、重命名、移动操作
- **FR-3**: 权限管理 - 支持知识库超级管理员、目录管理员、普通成员三级角色权限
- **FR-4**: 文档编辑 - 提供 Markdown 在线编辑器，支持左右分屏预览
- **FR-5**: 状态管理 - 文档发布状态（未发布/已发布）和分析状态（未分析/已分析）管理
- **FR-6**: 版本管理 - 自动生成版本号，支持版本历史查看、对比和回滚
- **FR-7**: AI 配置 - 集中管理文本生成、Embedding、Rerank、图文分析模型配置
- **FR-8**: Wiki 浏览 - 只读浏览已发布文档，支持目录树导航和文件内 TOC
- **FR-9**: 智能检索 - 支持全文搜索和 RAG 语义检索
- **FR-10**: 智能问答 - 基于知识库内容的 AI 问答功能，支持引用来源展示

## Non-Functional Requirements

- **NFR-1**: 安全性 - API Key 加密存储，界面脱敏显示
- **NFR-2**: 性能 - 文档分析异步处理，不阻塞用户操作
- **NFR-3**: 可扩展性 - 支持多模型配置，按优先级（全局 → 知识库 → 目录）生效
- **NFR-4**: 可用性 - 系统状态实时或近实时更新

## Constraints

- **Technical**: Django 框架、DRF API、账号密码认证、Wiki 需要登录
- **Business**: MVP 第一期优先完成核心功能
- **Dependencies**: 外部 AI 模型服务（OpenAI/Anthropic/Cohere 等）

## Assumptions

- 用户已具备基础的 Markdown 编辑知识
- 系统部署在    
- 系统部署在内网或可访问外部 AI API 的环境
- 文档分析队列采用异步任务处理

## Acceptance Criteria

### AC-1: 文件导入功能

- **Given**: 用户在后台管理系统的文件导入页面
- **When**: 用户选择并上传 Markdown/Word/PPT/PDF 文件
- **Then**: 文件自动转换为 Markdown 格式并存储，保留标题、列表、表格等结构
- **Verification**: `programmatic`
- **Notes**: 支持批量导入

### AC-2: 三级目录结构

- **Given**: 用户有权限访问知识库
- **When**: 用户在侧边栏查看目录树
- **Then**: 展示知识库 → 知识目录 → 子文件夹/文件的三级结构，支持展开/折叠
- **Verification**: `human-judgment`

### AC-12: 左侧导航栏布局

- **Given**: 用户已登录后台管理系统
- **When**: 用户查看左侧导航栏
- **Then**: 显示 Logo、文档、设置等菜单项，设置点击后可以进入大模型配置页面
- **Verification**: `human-judgment`

### AC-13: 主内容区布局

- **Given**: 用户进入文档管理页面
- **When**: 用户查看主内容区
- **Then**: 左侧显示目录树，右侧显示文件列表，支持创建文档操作
- **Verification**: `human-judgment`

### AC-14: 文件状态标签

- **Given**: 用户查看文件列表
- **When**: 文件有状态标签
- **Then**: 显示学习实践、可编辑、可执行等状态标签
- **Verification**: `human-judgment`

### AC-3: 权限分配

- **Given**: 用户是知识库超级管理员
- **When**: 用户进入权限管理页面
- **Then**: 可以为二级目录分配目录管理员，目录管理员只能管理授权目录下的内容
- **Verification**: `programmatic`

### AC-4: 文档编辑与预览

- **Given**: 用户有权限编辑文档
- **When**: 用户进入文档编辑页面
- **Then**: 显示左右分屏（左侧源码/右侧预览），支持全屏编辑和纯预览模式
- **Verification**: `human-judgment`

### AC-5: 文档发布流程

- **Given**: 用户创建或编辑文档
- **When**: 用户点击"发布"按钮
- **Then**: 文档状态变为"已发布"，自动进入分析队列，发布后不可撤回
- **Verification**: `programmatic`

### AC-6: 版本管理

- **Given**: 用户编辑并保存文档
- **When**: 保存成功
- **Then**: 自动生成新版本号（v1, v2, v3...），记录修改时间、修改人信息
- **Verification**: `programmatic`

### AC-7: 版本对比与回滚

- **Given**: 用户在文档版本历史页面
- **When**: 用户选择两个版本进行对比或选择一个版本进行回滚
- **Then**: 高亮展示差异内容，回滚后生成新的版本号
- **Verification**: `programmatic`

### AC-8: AI 模型配置

- **Given**: 用户是系统管理员
- **When**: 用户进入 AI 模型配置页面
- **Then**: 可以配置文本生成、Embedding、Rerank、图文分析模型，支持测试连接
- **Verification**: `programmatic`

### AC-9: Wiki 浏览

- **Given**: 用户已登录 Wiki 站点
- **When**: 用户点击侧边栏目录树中的文件
- **Then**: 在主内容区展示 Markdown 渲染内容，右侧显示 TOC，支持滚动联动
- **Verification**: `human-judgment`

### AC-10: 智能问答

- **Given**: 用户在 Wiki 站点打开智能问答窗口
- **When**: 用户输入问题并选择知识范围
- **Then**: 返回基于知识库内容的回答，并列出引用来源文档
- **Verification**: `human-judgment`

### AC-11: 统计面板

- **Given**: 用户在后台管理系统首页
- **When**: 用户查看顶部导航栏
- **Then**: 显示未发布文档数和待分析文档数，点击可跳转到对应列表页
- **Verification**: `human-judgment`

## Open Questions

- [ ] 分析队列实现技术选型（Celery + Redis / Django Q）
- [ ] 向量数据库选型（ChromaDB / Pinecone / Milvus）
- [ ] 文件存储方案（本地文件系统 / 云存储）

