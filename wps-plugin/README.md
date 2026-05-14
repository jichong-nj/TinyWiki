# TinyWiki WPS 插件

基于 TinyWiki 知识库的 AI 助手 WPS 插件，使用官方 wpsjs 工具进行开发、调试和打包。

## 项目结构

```
wps-plugin/
├── src/
│   ├── components/
│   │   ├── Login.vue       # 登录组件
│   │   └── AIChat.vue      # AI 聊天组件
│   ├── App.vue             # 应用主组件
│   ├── main.ts             # 入口文件
│   └── axios.ts            # HTTP 请求封装
├── ribbon.xml              # 功能区配置文件
├── ribbon.js               # 功能区交互逻辑
├── taskpane.html           # 任务窗格入口
├── index.html              # 开发预览页面
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## 功能特性

1. **独立登录** - 用户可配置服务器地址，使用 TinyWiki 账号登录
2. **内置模式** - 基于知识库检索的问答
3. **OpenClaw 模式** - 使用 Agent 进行对话，支持附件上传
4. **会话管理** - 支持创建和管理多个会话
5. **WPS 集成** - 通过 WPS 功能区按钮打开侧边任务窗格

## 环境准备

### 1. 安装 wpsjs 全局工具

```bash
npm install -g wpsjs
```

### 2. 安装项目依赖

```bash
cd wps-plugin
npm install
```

## 开发调试

### 启动调试

```bash
npm run dev
```

此命令会：
- 启动本地开发服务器
- 自动打开 WPS 客户端
- 加载插件并启用热更新

WPS 会在功能区显示 "TinyWiki" 标签页，点击 "打开 AI 助手" 即可启动侧边任务窗格。

## 生产构建

### 标准构建

```bash
npm run build
```

构建产物将输出到 `dist` 目录，包含所有必要文件。

### 打包为 EXE (Windows)

```bash
npm run build:exe
```

此命令会将插件打包为独立的 EXE 安装文件，便于分发。

## 使用说明

1. 在 WPS 功能区点击 "TinyWiki" → "打开 AI 助手"
2. 首次打开插件，需要配置服务器地址（默认 `http://localhost:8000/api`）
3. 输入 TinyWiki 账号和密码登录
4. 选择知识库或 Agent
5. 开始对话！

## wpsjs 常用命令

```bash
wpsjs create <project-name>  # 创建新项目
wpsjs debug                  # 调试加载项
wpsjs build                  # 构建加载项
wpsjs build --exe            # 打包为 EXE
```

## 注意事项

- 确保 WPS 客户端已安装并能正常运行
- 开发时会自动启动本地服务器供 WPS 访问
- 生产构建会生成离线可部署的插件文件

