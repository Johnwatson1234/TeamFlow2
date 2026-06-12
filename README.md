# TeamFlow 2 智能团队协作管理系统

> **面向课程设计的全栈协作过程管理平台 —— 一个整合任务、文档、消息、Git、AI 分析与成员画像的完整软件工程项目**

---

## 📖 文档定位

这份 README 是一份**面向 AI 的程序员级系统说明书**。它的目标不是只告诉你怎么启动项目，而是让任何一个大型语言模型（或新加入的开发者）**在不逐行阅读源码的情况下**，也能完整理解：

- 这个项目解决什么问题、怎么解决的
- 选择了什么技术栈、为什么选择
- 系统架构如何分层、各层职责如何划分
- 数据库有哪些表、表之间如何关联、数据如何流动
- API 接口有哪些、各自的输入输出是什么
- AI 能力如何设计、如何与业务数据结合
- 前端页面如何组织、组件如何通信、状态如何管理
- 成员画像的评分算法是怎么算出来的
- 启动流程、配置方法、调试技巧

---

## 📋 目录

- [1. 项目概述](#1-项目概述)
- [2. 技术栈总览](#2-技术栈总览)
- [3. 系统架构设计](#3-系统架构设计)
- [4. 项目结构详解](#4-项目结构详解)
- [5. 数据库模型（ER 设计与 19 张表详细说明）](#5-数据库模型er-设计与-19-张表详细说明)
- [6. API 接口规范（8 大模块完整端点列表）](#6-api-接口规范8-大模块完整端点列表)
- [7. AI 智能分析系统（核心创新点）](#7-ai-智能分析系统核心创新点)
- [8. 成员画像评分算法（完整数学公式与代码逻辑）](#8-成员画像评分算法完整数学公式与代码逻辑)
- [9. 前端架构设计](#9-前端架构设计)
- [10. 数据流与请求链路](#10-数据流与请求链路)
- [11. 运行与部署](#11-运行与部署)
- [12. 配置说明](#12-配置说明)
- [13. 演示账号与种子数据](#13-演示账号与种子数据)
- [14. 开发约定与设计模式](#14-开发约定与设计模式)
- [15. 常见问题](#15-常见问题)
- [16. 课程设计相关（评分标准、答辩建议）](#16-课程设计相关评分标准答辩建议)

---

## 1. 项目概述

### 1.1 项目定位

TeamFlow 2 是一套面向**高校课程设计、小组作业、团队项目**场景的全栈协作过程管理系统。

与普通 ToDo 或聊天室不同，TeamFlow 2 的核心是**"协作过程管理"**而非"结果管理"：

```
┌───────────────  普通管理系统  ───────────────┐
│  创建任务  →  完成任务  →  看统计           │
└──────────────────────────────────────────────┘

┌───────────────  TeamFlow 2  ───────────────┐
│                                              │
│  创建任务  →  分配  →  接收  →  讨论        │
│     ↓                          ↓            │
│  阻塞处理  →  推进  →  完成  →  事件沉淀    │
│     ↓                          ↓            │
│  文档协作  →  消息沟通  →  Git追踪         │
│     ↓                          ↓            │
│  AI分析   →  贡献评分  →  成员画像         │
│     ↓                          ↓            │
│  风险预警  →  审计证据  →  职业建议        │
│                                              │
└──────────────────────────────────────────────┘
```

### 1.2 核心设计理念

> **以项目为容器 → 以任务为主线 → 以消息为触发 → 以事件为证据 → 以 AI 为分析引擎**

| 层级 | 职责 | 实现方式 |
|------|------|----------|
| 项目容器层 | 定义协作范围和成员边界 | projects / project_members / project_invitations |
| 任务主线层 | 驱动工作推进和状态流转 | tasks / milestones / task_activities |
| 沟通触发层 | 承载实时交流和上下文记录 | conversations / messages / websocket |
| 证据沉淀层 | 收集所有协作行为事件 | collaboration_events / notifications / documents / files / git_commits |
| AI 分析层 | 对沉淀数据进行智能解读 | ai_service / member_insights / llm_service |

### 1.3 业务范围总览

TeamFlow 2 覆盖了以下 16 个业务模块：

| 编号 | 模块 | 核心功能 |
|------|------|----------|
| 1 | 用户与认证 | 注册、登录、JWT 登录态、资料修改、密码修改、用户搜索 |
| 2 | 项目管理 | 创建、列表、详情、编辑、删除、进度总览 |
| 3 | 成员与邀请 | 成员列表、邀请/接受/拒绝机制、角色权限管理 |
| 4 | 任务管理 | 创建/编辑/归档、分配/接收/开始/阻塞/完成任务、活动日志 |
| 5 | 里程碑 | 创建/查看里程碑、任务关联里程碑 |
| 6 | 消息与讨论 | 项目群聊、任务讨论、AI 对话、代码消息、任务引用消息、已读追踪 |
| 7 | 文档协作 | 创建/编辑/删除文档、版本管理（版本号/摘要/字数统计） |
| 8 | 文件管理 | 上传/列表/删除、分类筛选、评审状态追踪 |
| 9 | 通知与提醒 | 通知列表/未读/已读、聚合提醒中心（邀请/任务/通知/时间线） |
| 10 | WebSocket 实时通信 | 心跳 ping/pong、新消息广播、同项目多终端同步 |
| 11 | 仪表盘 | 完成率/进度/活跃度趋势/健康度雷达图/风险摘要/贡献排行 |
| 12 | 协作图谱 | AntV G6 节点关系图：成员↔任务↔文档↔提交 |
| 13 | 贡献分析 | 多维评分（任务/文档/代码/响应/稳定性）+ 证据列表 |
| 14 | 风险管理 | 风险扫描、风险列表、等级/分数/原因/建议、标记解决 |
| 15 | Git 代码分析 | 提交记录/分支/冲突风险/PR/质量分/仓库绑定 |
| 16 | AI 智能助手 | 对话(SSE)、任务规划、周报生成、文档分析、成员画像、职业建议 |

### 1.4 典型使用流程

```
步骤 1: 组长注册账号 → 登录 → 创建项目
步骤 2: 组长搜索用户 → 发送邀请 → 成员接受加入
步骤 3: 组长创建里程碑 → 拆分任务 → 分配给各成员
步骤 4: 成员收到通知 → 查看任务 → 开始处理
步骤 5: 遇阻时标记阻塞 → 在任务会话中讨论 → 解决问题
步骤 6: 同时编辑文档 → 上传文件 → 提交代码(Git)
步骤 7: 组长查看仪表盘 → 风险扫描 → 贡献排行
步骤 8: 使用 AI 生成周报 → 查看成员画像 → 分析职业倾向
```

---

## 2. 技术栈总览

### 2.1 后端技术栈

| 技术 | 版本/说明 | 用途 |
|------|-----------|------|
| Python | 3.12+ | 运行环境 |
| [FastAPI](https://fastapi.tiangolo.com/) | latest | Web 框架：路由、依赖注入、自动生成 OpenAPI 文档 |
| [Uvicorn](https://www.uvicorn.org/) | latest | ASGI 服务器，支持热重载(--reload) |
| [SQLAlchemy](https://www.sqlalchemy.org/) | 2.x | ORM：声明式模型、Session 管理、关系映射 |
| [Pydantic](https://docs.pydantic.dev/) | 2.x | 请求体校验、响应序列化、类型安全 |
| SQLite | - | 零配置数据库，适合课程项目本地演示 |
| [PyJWT](https://pyjwt.readthedocs.io/) | latest | JWT Token 生成与校验 |
| [Passlib](https://passlib.readthedocs.io/) | latest | bcrypt 密码哈希 |
| [HTTPX](https://www.python-httpx.org/) | latest | 异步 HTTP 客户端，调用 LLM API |
| python-multipart | latest | 文件上传解析 |
| pypdf | latest | PDF 文件文本提取 |
| python-docx | latest | Word(.docx) 文本提取 |
| python-pptx | latest | PPT(.pptx) 文本提取 |
| email-validator | latest | 邮箱格式校验 |

### 2.2 前端技术栈

| 技术 | 用途 |
|------|------|
| [Vue 3](https://vuejs.org/) (Composition API) | 前端核心框架，`<script setup>` 语法 |
| [TypeScript](https://www.typescriptlang.org/) | 类型安全，接口定义 |
| [Vite](https://vitejs.dev/) | 开发服务器(HMR)、生产构建 |
| [Vue Router 4](https://router.vuejs.org/) | SPA 路由、导航守卫 |
| [Pinia](https://pinia.vuejs.org/) | 状态管理（4 个 Store：user/project/ai/notification） |
| [Element Plus](https://element-plus.org/) | UI 组件库：表格、表单、对话框、菜单、标签等 |
| [Axios](https://axios-http.com/) | HTTP 客户端，统一拦截器封装 |
| [ECharts 6](https://echarts.apache.org/) | 数据可视化：折线图、雷达图、饼图 |
| [AntV G6 5](https://g6.antv.antgroup.com/) | 关系图谱渲染：节点/边/力导向布局 |
| [Day.js](https://day.js.org/) | 轻量日期处理库 |
| @element-plus/icons-vue | Element Plus 图标组件 |

### 2.3 外部服务依赖

| 服务 | 用途 |
|------|------|
| LLM API（兼容 OpenAI 格式） | AI 对话、任务规划、周报、画像分析 |
| DiceBear Avatar API | 自动生成演示用户头像 |

---

## 3. 系统架构设计

### 3.1 五层架构模型

```
┌──────────────────────────────────────────────────────────────┐
│                    1. 表现层 (Presentation)                    │
│  Vue 3 SPA: Login / Register / ProjectList / 17 子页面       │
│  Element Plus + ECharts + AntV G6 + 自定义组件               │
├──────────────────────────────────────────────────────────────┤
│                    2. 接口层 (Interface)                       │
│  Axios HTTP 封装  ←──────→  FastAPI REST API (JSON)          │
│  WebSocket 客户端  ←──────→  WebSocket (/ws/{project_id})    │
│  SSE EventSource   ←──────→  AI 流式对话 (text/event-stream) │
├──────────────────────────────────────────────────────────────┤
│                    3. 业务层 (Business Logic)                  │
│  services/: ai_service / llm_service / member_insights /     │
│             presenters                                        │
│  core/: security(JWT) / realtime(WebSocket) / seed(演示数据)  │
├──────────────────────────────────────────────────────────────┤
│                    4. 数据层 (Data Access)                     │
│  models/entities.py: 19 个 SQLAlchemy 模型类                  │
│  db/session.py: Session 工厂                                  │
│  SQLite 文件: backend/data/teamflow.db                       │
│  上传文件: backend/uploads/                                   │
├──────────────────────────────────────────────────────────────┤
│                    5. 外部能力层 (External)                    │
│  LLM API (兼容 OpenAI /chat/completions 格式)                │
│  DiceBear (头像生成)                                          │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 请求处理链路（一次完整的 API 调用）

```
前端 Vue 组件
    │
    ├──→ api/http.ts (Axios 实例)
    │       │ 自动注入 Authorization header
    │       │ 统一 baseURL /api
    │       │ 统一错误拦截
    │       │
    │       └──→ GET/POST/PUT/DELETE → FastAPI Router
    │                                       │
    │                                       ├──→ Depends(get_current_user)
    │                                       │       解析 JWT → 查询用户
    │                                       │
    │                                       ├──→ Depends(ensure_project_member)
    │                                       │       校验用户是否属于该项目
    │                                       │
    │                                       ├──→ Route Handler
    │                                       │       解析 Pydantic 请求体
    │                                       │       调用 services/ 或直接 ORM
    │                                       │
    │                                       ├──→ SQLAlchemy Session
    │                                       │       CRUD → SQLite
    │                                       │
    │                                       └──→ JSONResponse
    │                                               序列化后返回前端
    │
    └──→ Pinia Store 更新 → Vue 响应式渲染
```

### 3.3 WebSocket 实时通信链路

```
前端 MessagesView.vue
    │
    ├── 建立 WebSocket 连接
    │   new WebSocket("ws://127.0.0.1:8000/ws/{projectId}")
    │
    ├── 心跳维持
    │   客户端每 30s 发送 { type: "ping" }
    │   服务端回复 { type: "pong" }
    │
    └── 接收实时消息事件
        服务端广播 { type: "new_message", data: { ... } }
        前端更新消息列表 + 未读计数
```

### 3.4 AI 对话流式链路 (SSE)

```
前端 AIView.vue
    │
    ├── POST /api/projects/{id}/ai/chat/stream
    │   请求体: { prompt, route_name, route_path, page_context, ... }
    │
    └── 接收 SSE 流
        event: plan    → AI 的处理计划
        event: token   → 逐 token 的文字输出
        event: action  → AI 决定执行的操作（导航/创建任务/生成报告...）
        event: done    → 对话结束，返回最终结果
```

---

## 4. 项目结构详解

```
TeamFlow2/
│
├── backend/                                    # FastAPI 后端服务
│   ├── app/
│   │   ├── api/                                # API 层
│   │   │   ├── deps.py                         # 依赖注入函数
│   │   │   │   └── get_current_user(): JWT 解析 → 返回 User 对象
│   │   │   │   └── ensure_project_member(): 校验用户是否为项目成员
│   │   │   ├── router.py                       # 路由聚合（8 个子路由注册）
│   │   │   └── routes/                         # 业务路由模块
│   │   │       ├── auth.py                     # POST /auth/register, /auth/login, GET /auth/me, PUT /auth/me, PUT /auth/password
│   │   │       ├── projects.py                 # 项目 CRUD + 成员管理 + 邀请 + 仪表盘 + 贡献 + Git 全部端点
│   │   │       ├── tasks.py                    # 任务 CRUD + 里程碑 + 任务动作(分配/接受/阻塞/完成) + 活动日志
│   │   │       ├── conversations.py            # 会话 CRUD + 消息发送/列表/已读/删除
│   │   │       ├── documents.py                # 文档 CRUD + 版本列表/创建版本
│   │   │       ├── files.py                    # 文件上传(FormData) + 列表/删除/分类
│   │   │       ├── notifications.py            # 通知列表/未读数/已读
│   │   │       ├── ai.py                       # AI 对话(SSE流式)/任务规划/周报/文档分析/文件分析/动作执行
│   │   │       └── websocket.py                # WebSocket 连接端点 /ws/{project_id}
│   │   │
│   │   ├── core/                               # 核心基础设施
│   │   │   ├── config.py                       # 环境变量加载(.env → os.environ) + 全局配置常量
│   │   │   │   └── DATABASE_URL, SECRET_KEY, ALGORITHM, LLM_*
│   │   │   ├── security.py                     # JWT 创建/校验 + bcrypt 密码哈希/验证
│   │   │   ├── realtime.py                     # WebSocket 连接管理器(ConnectionManager)
│   │   │   │   └── connect/disconnect/broadcast(project_id, message)
│   │   │   └── seed.py                         # 种子数据初始化器
│   │   │       └── 创建 9 个用户 + 8 个项目 + 成员关系 + 任务 + 文档 + 消息 + Git 提交 + 通知...
│   │   │
│   │   ├── db/                                 # 数据库层
│   │   │   └── session.py                      # SQLAlchemy engine + SessionLocal + Base
│   │   │       └── engine: sqlite:///backend/data/teamflow.db
│   │   │       └── get_db(): FastAPI 依赖，每请求一个 Session
│   │   │
│   │   ├── models/                             # 数据模型层
│   │   │   └── entities.py                     # 全部 19 张表的 SQLAlchemy ORM 模型定义
│   │   │       └── User, Project, ProjectMember, ProjectInvitation, Milestone
│   │   │       └── Task, TaskActivity, Conversation, ConversationMember, Message
│   │   │       └── Notification, Document, DocumentVersion, FileResource
│   │   │       └── CollaborationEvent, ContributionScore, ContributionEvidence
│   │   │       └── RiskAlert, GitRepository, GitCommit, PullRequest
│   │   │       └── AITaskSuggestion, AIReportHistory
│   │   │
│   │   ├── schemas/                            # Pydantic Schema 层
│   │   │   └── common.py                       # 公共响应模型(PaginatedResponse等)
│   │   │
│   │   ├── services/                           # 服务层（核心业务逻辑）
│   │   │   ├── llm_service.py                  # LLM API 调用封装
│   │   │   │   └── complete_text(): 调用 LLM 返回纯文本
│   │   │   │   └── complete_json(): 调用 LLM 返回解析后的 JSON（含重试）
│   │   │   │   └── _extract_json_object(): 从 LLM 响应中提取 JSON
│   │   │   │   └── 兼容 OpenAI /chat/completions 格式
│   │   │   ├── ai_service.py                   # AI 助手核心逻辑
│   │   │   │   └── build_project_snapshot(): 构建项目上下文快照（注入给 LLM）
│   │   │   │   └── build_chat_completion(): 对话：snapshot + prompt → LLM → reply + actions
│   │   │   │   └── execute_actions(): 执行 AI 返回的操作指令
│   │   │   │   └── generate_project_plan(): 任务规划
│   │   │   │   └── generate_weekly_report(): 周报生成
│   │   │   │   └── analyze_document/analyze_file(): 文档/文件分析
│   │   │   │   └── ALLOWED_ACTIONS: 12 种 AI 可执行操作白名单
│   │   │   ├── member_insights.py              # 成员贡献分析引擎
│   │   │   │   └── build_contribution_payload(): 主入口，协调全部分析流程
│   │   │   │   └── _build_member_metrics(): 个人指标聚合（关键词分析 + 五维评分）
│   │   │   │   └── _build_score_row(): 评分行 → 贡献排行榜
│   │   │   │   └── _build_profile(): 画像构建（规则引擎）
│   │   │   │   └── _build_profile_with_llm(): 画像增强（LLM 分析）
│   │   │   │   └── 关键词分类：IDEA/COORDINATION/RISK/ACTION 四组词库
│   │   │   └── presenters.py                   # 数据序列化/格式化工具
│   │   │       └── serialize_project/task/message/document/file/member/risk/invitation...
│   │   │       └── build_dashboard_payload(): 仪表盘聚合数据
│   │   │       └── build_graph_payload(): 协作图谱数据
│   │   │       └── build_git_payload(): Git 概览数据
│   │   │       └── build_reminder_payload(): 提醒中心数据
│   │   │       └── build_user_map(): 用户 ID → User 对象映射
│   │   │
│   │   ├── utils/                              # 工具层
│   │   │   └── serializers.py                  # dump_json() / parse_json()
│   │   │
│   │   └── main.py                             # FastAPI 应用入口
│   │       ├── 创建数据库表 (Base.metadata.create_all)
│   │       ├── 初始化种子数据 (seed_database)
│   │       ├── 注册 CORS 中间件
│   │       ├── 挂载 api_router (prefix="/api")
│   │       └── 健康检查端点 GET /
│   │
│   ├── data/                                   # SQLite 数据库文件目录
│   │   └── teamflow.db                         # (启动时自动生成)
│   ├── uploads/                                # 文件上传存储目录
│   ├── requirements.txt                        # Python 依赖清单
│   ├── .env.example                            # 环境变量模板
│   └── seed_all.py                             # 独立种子脚本（备用）
│
├── frontend/                                   # Vue 3 前端应用
│   ├── src/
│   │   ├── api/
│   │   │   ├── http.ts                         # Axios 实例封装
│   │   │   │   └── baseURL: VITE_API_BASE_URL 或 "http://127.0.0.1:8000/api"
│   │   │   │   └── 请求拦截器：自动注入 Authorization: Bearer {token}
│   │   │   │   └── 响应拦截器：401 → 清除 token → 跳转登录
│   │   │   └── index.ts                        # 全部 API 函数定义
│   │   │       └── authApi: login/register/getMe/updateMe/updatePassword/search
│   │   │       └── projectApi: list/create/detail/update/delete/dashboard
│   │   │       └── memberApi: list/invite/invitations/accept/reject/updateRole/remove
│   │   │       └── taskApi: list/my/listByProject/create/detail/update/delete/assign/...
│   │   │       └── conversationApi: list/create/detail/messages/send/read/delete
│   │   │       └── documentApi: list/create/detail/update/delete/versions/createVersion
│   │   │       └── fileApi: list/upload/delete
│   │   │       └── notificationApi: list/unreadCount/read/readAll
│   │   │       └── aiApi: chatStream(SSE)/planning/confirmPlan/weeklyReport/fileAnalysis/executeActions
│   │   │       └── 以及 contribution/graph/risk/git/reminder/milestone/audit 等
│   │   │
│   │   ├── router/
│   │   │   └── index.ts                        # Vue Router 配置
│   │   │       ├── /login → LoginView
│   │   │       ├── /register → RegisterView
│   │   │       ├── /projects → ProjectListView
│   │   │       └── /project/:id/...
│   │   │           ├── dashboard → DashboardView
│   │   │           ├── tasks → TasksView
│   │   │           ├── milestones → MilestonesView
│   │   │           ├── messages → MessagesView
│   │   │           ├── documents → DocumentsView
│   │   │           ├── documents/editor → DocumentEditorView
│   │   │           ├── files → FilesView
│   │   │           ├── graph → GraphView
│   │   │           ├── contribution → ContributionView
│   │   │           ├── career → CareerInsightsView
│   │   │           ├── risk → RiskView
│   │   │           ├── git → GitView
│   │   │           ├── ai → AIView
│   │   │           ├── settings → SettingsView
│   │   │           ├── reminders → RemindersView
│   │   │           ├── audit → AuditView
│   │   │           └── 导航守卫: beforeEach(检查 token → 未登录 → /login)
│   │   │
│   │   ├── stores/                             # Pinia 状态管理
│   │   │   ├── user.ts                         # useUserStore
│   │   │   │   └── state: token, user, isLoggedIn
│   │   │   │   └── actions: login/logout/register/fetchMe/updateMe
│   │   │   ├── project.ts                      # useProjectStore
│   │   │   │   └── state: currentProject, projects, members, dashboard
│   │   │   │   └── actions: fetchProjects/selectProject/fetchDashboard/...
│   │   │   ├── ai.ts                           # useAIStore
│   │   │   │   └── state: conversation, messages, isStreaming
│   │   │   │   └── actions: sendMessage(SSE流式)/fetchConversation/...
│   │   │   └── notification.ts                 # useNotificationStore
│   │   │       └── state: notifications, unreadCount
│   │   │       └── actions: fetch/fetchUnread/markRead/markAllRead
│   │   │
│   │   ├── layouts/
│   │   │   └── ProjectLayout.vue               # 项目内统一布局
│   │   │       ├── 左侧边栏: 项目名称 + 17 子页面导航菜单
│   │   │       ├── 右侧主体: <router-view />
│   │   │       └── 右下角浮动: AIAssistantDock 组件
│   │   │
│   │   ├── components/common/                  # 通用可复用组件
│   │   │   ├── AIAssistantDock.vue             # AI 助手浮窗（拖拽/最小化/对话界面）
│   │   │   ├── AppViewport.vue                 # 页面视口容器（统一 padding/背景）
│   │   │   ├── GraphCanvas.vue                 # 协作关系图画布（AntV G6 集成）
│   │   │   ├── LineChart.vue                   # 折线图组件（ECharts 封装）
│   │   │   ├── RadarChart.vue                  # 雷达图组件（ECharts 封装）
│   │   │   └── StatCard.vue                    # 统计卡片组件（图标+数值+标签）
│   │   │
│   │   ├── views/                              # 页面视图
│   │   │   ├── auth/
│   │   │   │   ├── LoginView.vue               # 登录页（用户名+密码表单）
│   │   │   │   └── RegisterView.vue            # 注册页
│   │   │   ├── projects/
│   │   │   │   └── ProjectListView.vue         # 项目列表（卡片网格 + 创建弹窗）
│   │   │   └── project/                        # 项目内 17 个功能页
│   │   │       ├── DashboardView.vue           # 仪表盘：统计卡片+折线图+雷达图+事件时间线
│   │   │       ├── TasksView.vue               # 任务看板：状态列(TODO/DOING/REVIEW/DONE/BLOCKED)
│   │   │       ├── MilestonesView.vue          # 里程碑：时间线 + 进度
│   │   │       ├── MessagesView.vue            # 即时通信：会话列表+聊天窗口+代码消息+引用
│   │   │       ├── DocumentsView.vue           # 文档列表：表格+搜索+创建
│   │   │       ├── DocumentEditorView.vue      # 文档编辑器：富文本+版本管理+关联任务
│   │   │       ├── FilesView.vue               # 文件管理：上传+分类表格+评审状态
│   │   │       ├── GraphView.vue               # 关系图谱：G6 画布+节点筛选
│   │   │       ├── ContributionView.vue        # 贡献评估：排行榜+多维雷达图+证据列表
│   │   │       ├── CareerInsightsView.vue      # 职业画像：个人画像卡片+雷达图+建议
│   │   │       ├── RiskView.vue                # 风险预警：风险卡片+等级颜色+解决操作
│   │   │       ├── GitView.vue                 # Git 追踪：提交列表+分支图+PR+冲突文件
│   │   │       ├── AIView.vue                  # AI 助手页：对话界面+任务规划+周报按钮
│   │   │       ├── SettingsView.vue            # 项目设置：基本信息+成员管理+邀请
│   │   │       ├── RemindersView.vue           # 提醒中心：邀请/任务/通知/时间线聚合
│   │   │       └── AuditView.vue               # 审计视图：分类统计+事件列表
│   │   │
│   │   ├── utils/
│   │   │   └── apiError.ts                     # API 错误统一处理（toast 提示）
│   │   ├── App.vue                             # 根组件
│   │   └── main.ts                             # 应用入口
│   │       ├── createApp → use Pinia → use Router → mount
│   │       └── 全局注册 Element Plus 中文语言包
│   │
│   ├── package.json                            # Node 依赖配置
│   └── vite.config.ts                          # Vite 配置
│       └── proxy: /api → http://127.0.0.1:8000 (开发代理)
│
├── collect_code.py                             # 代码汇总脚本（生成 code.txt）
├── code.txt                                    # 全部源代码汇总文件
├── 开发文档.md                                  # 开发文档
├── 现有功能清单.md                              # 功能清单
├── 通信方案.md                                  # 通信与协作闭环优化方案
└── 要求.md                                     # 软件工程课程设计要求
```

---

## 5. 数据库模型（ER 设计与 19 张表详细说明）

### 5.1 数据库概览

- **数据库类型**：SQLite（文件: `backend/data/teamflow.db`）
- **ORM 框架**：SQLAlchemy 2.x
- **表总数**：19 张
- **设计原则**：以 `project` 为核心，所有业务实体均通过 `project_id` 外键关联

### 5.2 核心实体关系图（ER）

```
                          ┌─────────────┐
                          │    users    │
                          │  (用户表)    │
                          └──────┬──────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
    ┌─────▼─────┐         ┌─────▼─────┐          ┌─────▼─────┐
    │ projects  │◄────────│  project  │          │   tasks   │
    │  (项目表)  │  owner  │ _members  │          │  (任务表)  │
    └─────┬─────┘         └───────────┘          └─────┬─────┘
          │                                            │
    ┌─────┼─────────────────────────────┐              │
    │     │                             │              │
    ▼     ▼                             ▼              ▼
┌───────┐┌───────┐┌──────────────┐┌───────────┐┌──────────────┐
│project││ docu- ││ conversation ││  message  ││ task_activity│
│invita-││ ments ││  (会话表)     ││  (消息表)  ││ (任务活动日志) │
│tions  ││(文档) │└──────┬───────┘└───────────┘└──────────────┘
└───────┘└───┬───┘       │
             │     ┌─────▼──────────┐
      ┌──────▼──┐ │conversation     │
      │document │ │_member          │
      │_version │ │(会话成员/已读)   │
      └─────────┘ └────────────────┘

┌──────────┐  ┌────────────┐  ┌──────────────┐
│  files   │  │ milestone  │  │notification  │
│(文件资源) │  │ (里程碑)    │  │  (通知表)     │
└──────────┘  └────────────┘  └──────────────┘

┌──────────────┐  ┌───────────────┐  ┌───────────────┐
│ collaboration│  │ contribution  │  │ contribution  │
│ _event       │  │ _score        │  │ _evidence     │
│ (协作事件)    │  │ (贡献评分)     │  │ (贡献证据)     │
└──────────────┘  └───────────────┘  └───────────────┘

┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│risk_alert│  │git_repos │  │git_commit│  │pull_req  │
│(风险预警) │  │(仓库绑定) │  │(提交记录) │  │(合并请求) │
└──────────┘  └──────────┘  └──────────┘  └──────────┘

┌───────────────┐  ┌───────────────┐
│ai_task_       │  │ai_report_     │
│suggestion     │  │history        │
│(AI 任务规划)   │  │(AI 报告历史)   │
└───────────────┘  └───────────────┘
```

### 5.3 全部 19 张表详细说明

#### 表 1: `users` — 用户表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| username | VARCHAR(50) UNIQUE | 登录用户名 |
| password_hash | VARCHAR(255) | bcrypt 哈希密码 |
| display_name | VARCHAR(100) | 显示名称 |
| email | VARCHAR(120) UNIQUE | 邮箱 |
| phone | VARCHAR(30) | 电话 |
| avatar | VARCHAR(255) | 头像 URL |
| system_role | VARCHAR(30) | 系统角色：student/teacher/admin |
| status | VARCHAR(30) | 状态：active/inactive |
| title | VARCHAR(50) | 头衔/职位 |
| bio | TEXT | 个人简介 |
| created_at | DATETIME | 注册时间 |

#### 表 2: `projects` — 项目表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| name | VARCHAR(120) | 项目名称 |
| course_name | VARCHAR(120) | 课程名称 |
| description | TEXT | 项目描述 |
| status | VARCHAR(30) | 状态：进行中/已完成/已归档 |
| category | VARCHAR(50) | 分类：course/competition/research |
| start_date | VARCHAR(30) | 开始日期 |
| due_date | VARCHAR(30) | 截止日期 |
| repo_url | VARCHAR(255) | 代码仓库地址 |
| advisor_name | VARCHAR(100) | 指导教师姓名 |
| advisor_email | VARCHAR(120) | 指导教师邮箱 |
| tags_json | TEXT | 标签 JSON 数组 |
| owner_id | INTEGER FK→users | 项目创建者 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 表 3: `project_members` — 项目成员表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| project_id | INTEGER FK→projects | 所属项目 |
| user_id | INTEGER FK→users | 成员用户 |
| role | VARCHAR(50) | 角色：组长/后端开发/前端开发/文档负责人/成员... |
| permission_level | VARCHAR(50) | 权限：全部权限/编辑权限/只读权限 |
| workload | INTEGER | 工作负载（0-100） |
| online_status | VARCHAR(30) | 在线状态 |
| joined_at | DATETIME | 加入时间 |

#### 表 4: `project_invitations` — 项目邀请表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| project_id | INTEGER FK→projects | 目标项目 |
| inviter_id | INTEGER FK→users | 邀请人 |
| invitee_id | INTEGER FK→users | 被邀请人 |
| role | VARCHAR(50) | 邀请的角色 |
| message | TEXT | 邀请附言 |
| status | VARCHAR(30) | pending/accepted/rejected/expired/revoked |
| created_at | DATETIME | 发送时间 |
| responded_at | DATETIME | 响应时间 |

#### 表 5: `milestones` — 里程碑表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| project_id | INTEGER FK→projects | 所属项目 |
| name | VARCHAR(120) | 里程碑名称 |
| due_date | VARCHAR(30) | 截止日期 |
| status | VARCHAR(30) | 状态：待开始/进行中/已完成 |
| order_index | INTEGER | 排序序号 |

#### 表 6: `tasks` — 任务表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| project_id | INTEGER FK→projects | 所属项目 |
| milestone_id | INTEGER FK→milestones | 关联里程碑(可空) |
| title | VARCHAR(160) | 任务标题 |
| description | TEXT | 任务描述 |
| status | VARCHAR(30) | TODO/IN_PROGRESS/REVIEW/DONE/BLOCKED |
| response_status | VARCHAR(30) | 响应状态：未分配/待接收/已接收/处理中 |
| priority | VARCHAR(30) | 优先级：高/中/低 |
| progress | INTEGER | 进度百分比 0-100 |
| assignee_id | INTEGER FK→users | 负责人(可空) |
| due_date | VARCHAR(30) | 截止日期 |
| start_date | VARCHAR(30) | 开始日期 |
| blocker_reason | VARCHAR(255) | 阻塞原因 |
| related_requirement | VARCHAR(120) | 关联需求 |
| related_document | VARCHAR(120) | 关联文档 |
| related_commit | VARCHAR(120) | 关联提交 |
| archived | BOOLEAN | 是否归档（软删除） |
| created_by | INTEGER FK→users | 创建者 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 表 7: `task_activities` — 任务活动日志表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| task_id | INTEGER FK→tasks | 关联任务 |
| project_id | INTEGER FK→projects | 所属项目 |
| actor_id | INTEGER FK→users | 操作人 |
| activity_type | VARCHAR(50) | created/assigned/accepted/started/blocked/completed/commented |
| from_value | VARCHAR(120) | 变更前值 |
| to_value | VARCHAR(120) | 变更后值 |
| content | TEXT | 活动描述 |
| created_at | DATETIME | 发生时间 |

#### 表 8: `conversations` — 会话表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| project_id | INTEGER FK→projects | 所属项目 |
| conversation_type | VARCHAR(30) | project_group/task/ai_assistant |
| related_task_id | INTEGER FK→tasks | 关联任务(可空，task 类型时必填) |
| name | VARCHAR(120) | 会话名称 |
| created_by | INTEGER FK→users | 创建者 |
| is_pinned | BOOLEAN | 是否置顶 |
| created_at | DATETIME | 创建时间 |

#### 表 9: `conversation_members` — 会话成员表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| conversation_id | INTEGER FK→conversations | 关联会话 |
| user_id | INTEGER FK→users | 成员用户 |
| last_read_message_id | INTEGER | 最后已读消息 ID |
| last_read_at | DATETIME | 最后阅读时间 |
| mute_flag | BOOLEAN | 是否免打扰 |
| joined_at | DATETIME | 加入时间 |

#### 表 10: `messages` — 消息表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| project_id | INTEGER FK→projects | 所属项目 |
| conversation_id | INTEGER FK→conversations | 所属会话 |
| sender_id | INTEGER FK→users | 发送者 |
| reply_to_message_id | INTEGER FK→messages | 回复的消息(可空) |
| message_type | VARCHAR(30) | text/code/task/file_analysis |
| content | TEXT | 消息内容 |
| code_language | VARCHAR(30) | 代码语言(代码消息时) |
| metadata_json | TEXT | 扩展元数据 JSON |
| client_msg_id | VARCHAR(100) | 客户端消息幂等 ID |
| status | VARCHAR(30) | sent/delivered/read |
| created_at | DATETIME | 发送时间 |

#### 表 11: `notifications` — 通知表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| user_id | INTEGER FK→users | 接收用户 |
| project_id | INTEGER FK→projects | 关联项目(可空) |
| type | VARCHAR(50) | project_invite/task_assigned/message_mentioned/task_status_changed... |
| title | VARCHAR(120) | 通知标题 |
| content | TEXT | 通知内容 |
| ref_type | VARCHAR(50) | 关联实体类型 |
| ref_id | INTEGER | 关联实体 ID |
| is_read | BOOLEAN | 是否已读 |
| created_at | DATETIME | 创建时间 |
| read_at | DATETIME | 阅读时间 |

#### 表 12: `documents` — 文档表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| project_id | INTEGER FK→projects | 所属项目 |
| title | VARCHAR(160) | 文档标题 |
| content | TEXT | 文档正文 |
| author_id | INTEGER FK→users | 作者 |
| updated_by_id | INTEGER FK→users | 最近更新人 |
| version_count | INTEGER | 版本总数 |
| permission_status | VARCHAR(30) | 权限状态 |
| tags_json | TEXT | 标签 JSON |
| related_task_id | INTEGER FK→tasks | 关联任务(可空) |
| is_deleted | BOOLEAN | 软删除标记 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 表 13: `document_versions` — 文档版本表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| document_id | INTEGER FK→documents | 关联文档 |
| version_label | VARCHAR(30) | 版本号（v1.0/v1.1/v2.0...） |
| summary | VARCHAR(255) | 版本摘要 |
| content | TEXT | 版本完整内容 |
| author_id | INTEGER FK→users | 版本作者 |
| added_words | INTEGER | 新增字数 |
| modified_words | INTEGER | 修改字数 |
| created_at | DATETIME | 创建时间 |

#### 表 14: `file_resources` — 文件资源表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| project_id | INTEGER FK→projects | 所属项目 |
| name | VARCHAR(160) | 文件名 |
| file_type | VARCHAR(30) | 文件类型：文档/代码/图片/PPT/Excel |
| related_task | VARCHAR(120) | 关联任务 |
| uploader_id | INTEGER FK→users | 上传者 |
| version_label | VARCHAR(30) | 版本号 |
| review_status | VARCHAR(30) | 评审状态：待评审/已通过/需修改/已驳回 |
| download_count | INTEGER | 下载次数 |
| category | VARCHAR(50) | 分类：需求/设计/开发/测试/部署/文档/其他 |
| storage_path | VARCHAR(255) | 存储路径 |
| size_label | VARCHAR(30) | 文件大小（格式化的字符串） |
| description | TEXT | 文件描述 |
| comments_json | TEXT | 评论列表 JSON |
| created_at | DATETIME | 上传时间 |
| updated_at | DATETIME | 更新时间 |

#### 表 15: `collaboration_events` — 协作事件表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| project_id | INTEGER FK→projects | 所属项目 |
| actor_id | INTEGER FK→users | 操作人 |
| event_type | VARCHAR(50) | project/task/message/document/file/commit |
| title | VARCHAR(160) | 事件标题 |
| content | TEXT | 事件内容 |
| related_type | VARCHAR(50) | 关联实体类型 |
| related_id | INTEGER | 关联实体 ID |
| score_value | FLOAT | 事件分值 |
| created_at | DATETIME | 发生时间 |

#### 表 16: `contribution_scores` — 贡献评分表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| project_id | INTEGER FK→projects | 所属项目 |
| user_id | INTEGER FK→users | 被评分用户 |
| total_score | FLOAT | 总分 |
| task_score | FLOAT | 任务分(0-35) |
| document_score | FLOAT | 文档分(0-10) |
| code_score | FLOAT | 代码分(0-15) |
| response_score | FLOAT | 响应分(0-25) |
| stability_score | FLOAT | 稳定性分(0-15) |
| completed_tasks | INTEGER | 完成任务数 |
| collaboration_events | INTEGER | 协作事件总数 |
| updated_at | DATETIME | 更新时间 |

#### 表 17: `contribution_evidence` — 贡献证据表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| project_id | INTEGER FK→projects | 所属项目 |
| user_id | INTEGER FK→users | 被评分用户 |
| evidence_type | VARCHAR(50) | 证据类型：任务/文档/代码/消息/协作 |
| summary | VARCHAR(255) | 证据摘要 |
| score | FLOAT | 证据分值 |
| related_type | VARCHAR(50) | 关联类型 |
| related_id | INTEGER | 关联 ID |
| created_at | DATETIME | 创建时间 |

#### 表 18: `risk_alerts` — 风险预警表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| project_id | INTEGER FK→projects | 所属项目 |
| title | VARCHAR(160) | 风险标题 |
| level | VARCHAR(30) | 风险等级：高/中/低 |
| score | FLOAT | 风险分数 |
| reason | TEXT | 风险原因 |
| suggestion | TEXT | 建议措施 |
| status | VARCHAR(30) | open/resolved |
| risk_type | VARCHAR(50) | 进度/质量/资源/技术/沟通 |
| due_at | VARCHAR(30) | 应处理截止时间 |
| created_at | DATETIME | 创建时间 |

#### 表 19: `git_repositories` / `git_commits` / `pull_requests` — Git 分析表

**git_repositories**（仓库绑定）：
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| project_id | INTEGER FK→projects | 所属项目 |
| name | VARCHAR(120) | 仓库名 |
| url | VARCHAR(255) | 仓库地址 |
| default_branch | VARCHAR(50) | 默认分支 |
| sync_status | VARCHAR(30) | 同步状态 |
| webhook_status | VARCHAR(30) | Webhook 配置状态 |
| last_synced_at | VARCHAR(30) | 最近同步时间 |
| ci_status | VARCHAR(30) | CI 状态 |
| total_commits | INTEGER | 提交总数 |

**git_commits**（提交记录）：
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| project_id | INTEGER FK→projects | 所属项目 |
| user_id | INTEGER FK→users | 提交者 |
| commit_hash | VARCHAR(40) | 提交哈希 |
| branch_name | VARCHAR(60) | 分支名 |
| message | VARCHAR(255) | 提交信息 |
| changed_files_json | TEXT | 变更文件列表 JSON |
| added_lines | INTEGER | 新增行数 |
| deleted_lines | INTEGER | 删除行数 |
| risk_score | FLOAT | 冲突风险评分 |
| quality_score | FLOAT | 代码质量评分 |
| related_task | VARCHAR(60) | 关联任务 |
| created_at | DATETIME | 提交时间 |

**pull_requests**（合并请求）：id, project_id, title, branch_name, author_id, status, reviewers_json, updated_at

**ai_task_suggestions**（AI 任务规划）：id, project_id, title, input_payload(JSON), output_payload(JSON), status, created_at

**ai_report_history**（AI 报告历史）：id, project_id, report_type(weekly/member_insights), content, created_at

### 5.4 数据库关键索引

| 表 | 索引字段 | 用途 |
|----|----------|------|
| users | username UNIQUE | 登录查找 |
| users | email UNIQUE | 邮箱查找 |
| projects | owner_id FK | 按创建者查询项目 |
| project_members | (project_id, user_id) | 成员唯一性 |
| tasks | (project_id, status) | 按项目+状态筛选任务 |
| tasks | assignee_id FK | "我的任务"查询 |
| messages | (conversation_id, created_at) | 按会话获取消息时间线 |
| notifications | (user_id, is_read) | 未读通知查询 |
| collaboration_events | (project_id, actor_id) | 成员协作事件追踪 |

---

## 6. API 接口规范（8 大模块完整端点列表）

### 6.1 全局路由前缀

所有 API 路由挂载在 `/api` 前缀下：

```python
# backend/app/api/router.py
api_router.include_router(auth.router,         prefix="/auth",          tags=["auth"])
api_router.include_router(projects.router,     prefix="/projects",      tags=["projects"])
api_router.include_router(tasks.router,                                   tags=["tasks"])
api_router.include_router(conversations.router,                           tags=["conversations"])
api_router.include_router(documents.router,                               tags=["documents"])
api_router.include_router(files.router,                                   tags=["files"])
api_router.include_router(notifications.router,                           tags=["notifications"])
api_router.include_router(ai.router,           prefix="/ai",            tags=["ai"])
api_router.include_router(websocket.router,                               tags=["websocket"])
```

### 6.2 认证模块 `/api/auth`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/auth/register` | 用户注册 | 否 |
| POST | `/api/auth/login` | 用户登录，返回 JWT token | 否 |
| GET | `/api/auth/me` | 获取当前用户信息 | JWT |
| PUT | `/api/auth/me` | 更新个人信息（display_name/email/phone/bio/avatar） | JWT |
| PUT | `/api/auth/password` | 修改密码（需提供 old_password + new_password） | JWT |
| GET | `/api/auth/search?q={keyword}` | 搜索用户 | JWT |

### 6.3 项目模块 `/api/projects`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/projects` | 获取"我的项目"列表 | JWT |
| POST | `/api/projects` | 创建项目（自动将自己设为组长） | JWT |
| GET | `/api/projects/{id}` | 项目详情 | JWT+成员 |
| PUT | `/api/projects/{id}` | 编辑项目信息 | JWT+成员 |
| DELETE | `/api/projects/{id}` | 删除项目 | JWT+成员 |
| GET | `/api/projects/{id}/dashboard` | 仪表盘聚合数据 | JWT+成员 |
| GET | `/api/projects/{id}/graph` | 协作图谱数据 | JWT+成员 |
| GET | `/api/projects/{id}/contributions` | 贡献分析数据 | JWT+成员 |
| POST | `/api/projects/{id}/contributions/refresh` | 重新计算贡献分 | JWT+成员 |
| GET | `/api/projects/{id}/risks` | 风险列表 | JWT+成员 |
| POST | `/api/projects/{id}/risks/scan` | 触发风险扫描 | JWT+成员 |
| PUT | `/api/projects/{id}/risks/{risk_id}/resolve` | 标记风险已解决 | JWT+成员 |
| GET | `/api/projects/{id}/git` | Git 概览数据 | JWT+成员 |
| GET | `/api/projects/{id}/members` | 成员列表 | JWT+成员 |
| PUT | `/api/projects/{id}/members/{user_id}` | 修改成员角色/权限 | JWT+成员 |
| DELETE | `/api/projects/{id}/members/{user_id}` | 移除成员 | JWT+成员 |
| POST | `/api/projects/{id}/invitations` | 发送邀请 | JWT+成员 |
| GET | `/api/projects/{id}/invitations` | 项目邀请记录 | JWT+成员 |
| DELETE | `/api/projects/{id}/invitations/{inv_id}` | 撤回邀请 | JWT+成员 |
| GET | `/api/projects/me/invitations` | "我收到的邀请"列表 | JWT |
| POST | `/api/projects/invitations/{inv_id}/accept` | 接受邀请 | JWT |
| POST | `/api/projects/invitations/{inv_id}/reject` | 拒绝邀请 | JWT |
| GET | `/api/projects/{id}/reminders` | 提醒中心聚合数据 | JWT+成员 |

### 6.4 任务模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/projects/{id}/tasks` | 项目任务列表 | JWT+成员 |
| GET | `/api/me/tasks` | "我的任务"（跨项目） | JWT |
| POST | `/api/projects/{id}/tasks` | 创建任务（自动创建关联会话） | JWT+成员 |
| GET | `/api/tasks/{id}` | 任务详情 | JWT+成员 |
| PUT | `/api/tasks/{id}` | 编辑任务 | JWT+成员 |
| DELETE | `/api/tasks/{id}` | 归档任务（软删除） | JWT+成员 |
| POST | `/api/tasks/{id}/assign` | 分配任务 | JWT+成员 |
| POST | `/api/tasks/{id}/accept` | 接受任务 | JWT+成员 |
| POST | `/api/tasks/{id}/start` | 开始处理 | JWT+成员 |
| POST | `/api/tasks/{id}/block` | 标记阻塞 | JWT+成员 |
| POST | `/api/tasks/{id}/complete` | 完成任务 | JWT+成员 |
| GET | `/api/tasks/{id}/activities` | 任务活动日志 | JWT+成员 |
| GET | `/api/projects/{id}/milestones` | 里程碑列表 | JWT+成员 |
| POST | `/api/projects/{id}/milestones` | 创建里程碑 | JWT+成员 |

### 6.5 会话与消息模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/projects/{id}/conversations` | 会话列表 | JWT+成员 |
| POST | `/api/projects/{id}/conversations` | 创建会话 | JWT+成员 |
| GET | `/api/conversations/{id}` | 会话详情 | JWT+成员 |
| GET | `/api/conversations/{id}/messages` | 会话消息列表 | JWT+成员 |
| POST | `/api/conversations/{id}/messages` | 发送消息（触发WebSocket广播） | JWT+成员 |
| PUT | `/api/conversations/{id}/read` | 标记会话已读 | JWT+成员 |
| DELETE | `/api/messages/{id}` | 删除消息 | JWT+发送者 |

### 6.6 文档模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/projects/{id}/documents` | 文档列表 | JWT+成员 |
| POST | `/api/projects/{id}/documents` | 创建文档 | JWT+成员 |
| GET | `/api/documents/{id}` | 文档详情 | JWT+成员 |
| PUT | `/api/documents/{id}` | 编辑文档 | JWT+成员 |
| DELETE | `/api/documents/{id}` | 删除文档（软删除） | JWT+成员 |
| GET | `/api/documents/{id}/versions` | 版本列表 | JWT+成员 |
| POST | `/api/documents/{id}/versions` | 创建新版本 | JWT+成员 |

### 6.7 文件模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/projects/{id}/files` | 文件列表（支持?category=筛选） | JWT+成员 |
| POST | `/api/projects/{id}/files/upload` | 上传文件（FormData） | JWT+成员 |
| DELETE | `/api/files/{id}` | 删除文件 | JWT+成员 |
| GET | `/api/files/{id}/download` | 下载文件 | JWT+成员 |

### 6.8 通知模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/notifications` | 通知列表 | JWT |
| GET | `/api/notifications/unread-count` | 未读通知数量 | JWT |
| PUT | `/api/notifications/{id}/read` | 标记单条已读 | JWT |
| PUT | `/api/notifications/read-all` | 全部标记已读 | JWT |

### 6.9 AI 模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/ai/planning` | AI 任务规划 | JWT+成员 |
| POST | `/api/ai/planning/{id}/confirm` | 确认规划（写入Task表） | JWT+成员 |
| POST | `/api/ai/reports/weekly?project_id={id}` | 生成周报 | JWT+成员 |
| GET | `/api/projects/{id}/ai/conversation` | 获取AI对话历史 | JWT+成员 |
| POST | `/api/projects/{id}/ai/chat/stream` | AI对话（SSE流式） | JWT+成员 |
| POST | `/api/projects/{id}/ai/file-analysis` | 文档/文件AI分析 | JWT+成员 |
| POST | `/api/projects/{id}/ai/actions/execute` | 执行AI返回的操作指令 | JWT+成员 |

### 6.10 WebSocket

| 协议 | 路径 | 说明 |
|------|------|------|
| ws:// | `/ws/{project_id}` | 项目实时通信端点 |

### 6.11 认证机制详解

```
POST /api/auth/login  {username, password}
       ↓
1. 查询用户
2. bcrypt.verify(password)
3. 创建 JWT: payload={sub:user.id}, expires=7天, algorithm=HS256
4. 返回 {access_token}

后续请求: Authorization: Bearer <JWT>
       ↓
get_current_user() → 解析token → 查询DB → 返回User对象
```

---

## 7. AI 智能分析系统（核心创新点）

### 7.1 设计原则

**AI不是独立聊天机器人，而是"基于协作上下文的分析引擎"。**

AI的输入不只是用户的一句话，而是包含：
- 当前项目的完整信息（名称、成员、进度）
- 当前用户所在页面的上下文（路由、选中的任务/文档/成员）
- 项目的结构化数据（任务列表、文档列表、仪表盘数据等）

### 7.2 上下文快照机制 (build_project_snapshot)

每次AI调用前，后端构建一个 `snapshot`，根据当前页面注入对应数据：

| 用户所在页面 | 快照中注入的数据 |
|-------------|-----------------|
| Dashboard | 仪表盘完整数据（统计卡片、图表、风险、贡献排行） |
| Tasks | 任务列表 + 当前选中任务详情 |
| Messages | 会话列表 + 当前会话消息历史 |
| Documents | 文档列表 + 当前文档完整内容 |
| Contribution | 贡献排行 + 证据列表 |
| Graph | 协作图谱节点/边数据 |
| Git | 提交/分支/PR数据 |
| Settings | 项目基本信息 + 成员列表 |

### 7.3 AI对话流程 (SSE流式)

```
POST /api/projects/{id}/ai/chat/stream
  {prompt, route_name, route_path, page_context, auto_execute}
    ↓
1. 构建项目上下文快照
2. 组装 System Prompt + User Prompt
3. 调用 LLM API (complete_json, temperature=0.35, max_tokens=2000)
4. LLM返回 JSON: {reply, actions[]}
5. SSE流式输出:
   event:plan   → AI的处理计划
   event:token  → 逐token回复文本
   event:action → AI决定的操作
   event:done   → 最终快照+执行结果
6. 如果auto_execute=true，自动执行actions中的安全操作
```

### 7.4 AI可执行操作（12种白名单）

```python
ALLOWED_ACTIONS = {
    "navigate_page",             # 页面导航
    "open_task",                 # 打开任务详情
    "open_document",             # 打开文档详情
    "open_file",                 # 打开文件详情
    "create_task",               # 创建任务
    "update_task",               # 更新任务
    "accept_task",               # 接受任务
    "block_task",                # 标记阻塞
    "complete_task",             # 完成任务
    "create_milestone",          # 创建里程碑
    "generate_weekly_report",    # 生成周报
    "scan_risks",                # 扫描风险
    "recalculate_contribution",  # 重新计算贡献分
}
```

### 7.5 AI任务规划

输入: 用户自然语言描述 + 项目上下文快照
输出: JSON {summary, phases[{step,title,date}], tasks[{name,owner,priority,hours,deadline}], risks[{name,level,suggestion}], suggestions[]}
确认后 → confirm_plan → 写入Task表

### 7.6 AI周报生成

输入: 仪表盘数据快照 → LLM(temperature=0.35, max_tokens=1400) → 纯文本中文周报（本周进展/风险与问题/下周建议） → 存入AIReportHistory表

### 7.7 AI文档/文件分析

输入: 文档内容(最多12000字) 或 文件(PDF/DOCX/PPTX文本提取)
输出: JSON {summary, scale, workload, grade, risks[], suggestions[], extracted_excerpt}

---

## 8. 成员画像评分算法（完整数学公式与代码逻辑）

### 8.1 评分架构

系统对每个项目成员进行**五维贡献评分**，满分100分：

| 维度 | 满分 | 权重 | 说明 |
|------|------|------|------|
| task_score（任务分） | 35 | 35% | 完成任务数量、进度、加权进度 |
| response_score（响应分） | 25 | 25% | 想法贡献、协调沟通、风险识别 |
| code_score（代码分） | 15 | 15% | 代码消息、提交次数、代码行数 |
| stability_score（稳定性分） | 15 | 15% | 持续投入、稳定性、阻塞情况 |
| document_score（文档分） | 10 | 10% | 文档数量、版本数量、字数贡献 |

**总分 = task_score + document_score + code_score + response_score + stability_score**

### 8.2 五维评分公式（Python实现）

```python
# ── 任务分 (0-35) ──
task_score = clamp(
    completed_tasks * 13
    + in_progress_tasks * 5
    + review_tasks * 4
    + weighted_progress * 6
    + completed_activities * 2,
    0, 35
)

# ── 文档分 (0-10) ──
document_score = clamp(
    document_count * 4
    + document_version_count * 2
    + min(total_versions / 200, 2),
    0, 10
)

# ── 代码分 (0-15) ──
code_score = clamp(
    len(code_messages) * 3
    + commit_count * 4
    + min(added_lines / 120, 4),
    0, 15
)

# ── 响应分 (0-25) ──
response_score = clamp(
    useful_idea_count * 4.5
    + coordination_count * 2
    + risk_count * 2
    + task_reference_count * 2.5
    + min(avg_message_length / 18, 3),
    0, 25
)

# ── 稳定性分 (0-15) ──
stability_score = clamp(
    5 + completed_tasks * 2
    + review_tasks * 1.5
    + min(len(activities) * 0.6, 4)
    - blocked_tasks * 2
    - blocked_activities,
    0, 15
)
```

### 8.3 关键词分析引擎

系统通过四组预定义关键词库自动分析消息内容：

```python
IDEA_KEYWORDS = ["建议","可以","方案","思路","优化","改成","不如","要不","是否","应该","考虑","idea"]
COORDINATION_KEYWORDS = ["同步","联调","对接","评审","一起","麻烦","辛苦","确认","跟进","配合"]
RISK_KEYWORDS = ["风险","阻塞","bug","异常","问题","延期","超时","失败","缺少","未定义"]
ACTION_KEYWORDS = ["完成","已开发","已更新","已处理","已修复","已提交","已对接","实现","上线"]

PRIORITY_WEIGHT = {"高": 1.4, "中": 1.1, "低": 0.8}  # 任务优先级权重系数
```

对每条消息进行关键词匹配，统计：
- **idea_count**: 提出建设性想法的次数
- **useful_idea_count**: 有价值的想法（内容长度≥18且有具体行动/风险/接口提及）
- **coordination_count**: 协调沟通次数
- **risk_count**: 风险识别次数
- **action_count**: 执行行动次数
- **mention_count**: @提及他人次数

### 8.4 画像标签引擎

```python
ROLE_LIBRARY = {
    "执行推进型": ["后端开发", "前端开发", "实施交付"],
    "协调沟通型": ["项目经理助理", "产品经理", "测试协调"],
    "技术攻坚型": ["后端开发", "架构预研", "算法/平台开发"],
    "方案策划型": ["产品策划", "需求分析", "解决方案工程师"],
    "沉淀整理型": ["测试开发", "技术文档", "数据运营"],
}
```

系统根据用户的五维评分分布自动归类到以上5种画像类型之一。

### 8.5 雷达图维度

```python
radar = [
    {"name": "讨论活跃", "value": clamp(message_count*14 + coordination_count*10, 0, 100)},
    {"name": "想法贡献", "value": clamp(idea_count*22 + useful_idea_count*16, 0, 100)},
    {"name": "任务落地", "value": clamp(completed_tasks*30 + avg_task_progress*0.6, 0, 100)},
    {"name": "技术输出", "value": clamp(code_message_count*26 + commit_count*18, 0, 100)},
    {"name": "文档沉淀", "value": clamp(document_count*30 + document_version_count*14, 0, 100)},
]
```

### 8.6 LLM增强画像

当配置了LLM API Key时，系统会额外调用LLM对成员进行深度画像分析：

**输入给LLM的数据**:
- 成员基本信息（display_name）
- 量化指标（消息数、想法数、完成任务数、平均进度、文档数、代码消息数、提交数）
- 消息样本（最近4条讨论消息 + 1条代码消息）

**LLM输出**:
- profile_label: 画像类型标签
- communication_style: 沟通风格描述
- personality_summary: 性格倾向总结
- contribution_summary: 贡献总评
- strengths: 优势列表
- risks: 风险点列表
- recommended_roles: 推荐岗位方向
- career_recommendation: 职业发展建议

**兜底策略**: 当LLM不可用时，系统使用规则引擎（_build_profile）生成画像，保证功能始终可用。

---

## 9. 前端架构设计

### 9.1 组件树

```
App.vue
├── LoginView.vue / RegisterView.vue          (未登录状态)
│
└── ProjectLayout.vue                          (登录后)
    ├── 左侧边栏 (el-menu)
    │   └── 17个子页面导航链接
    │
    ├── <router-view>                          (右侧主内容区)
    │   ├── ProjectListView.vue
    │   ├── DashboardView.vue
    │   │   ├── StatCard.vue × N
    │   │   ├── LineChart.vue
    │   │   └── RadarChart.vue
    │   ├── TasksView.vue
    │   ├── MessagesView.vue
    │   ├── DocumentsView.vue
    │   ├── DocumentEditorView.vue
    │   ├── FilesView.vue
    │   ├── GraphView.vue
    │   │   └── GraphCanvas.vue (AntV G6)
    │   ├── ContributionView.vue
    │   │   └── RadarChart.vue
    │   ├── CareerInsightsView.vue
    │   │   └── RadarChart.vue
    │   ├── RiskView.vue
    │   ├── GitView.vue
    │   ├── AIView.vue
    │   ├── SettingsView.vue
    │   ├── RemindersView.vue
    │   ├── AuditView.vue
    │   └── MilestonesView.vue
    │
    └── AIAssistantDock.vue                    (右下角浮动AI助手)
```

### 9.2 路由设计

```typescript
// router/index.ts
const routes = [
  { path: '/login', component: LoginView },
  { path: '/register', component: RegisterView },
  { path: '/projects', component: ProjectListView, meta: { requiresAuth: true } },
  {
    path: '/project/:id',
    component: ProjectLayout,
    meta: { requiresAuth: true },
    children: [
      { path: 'dashboard', component: DashboardView },
      { path: 'tasks', component: TasksView },
      { path: 'milestones', component: MilestonesView },
      { path: 'messages', component: MessagesView },
      { path: 'documents', component: DocumentsView },
      { path: 'documents/editor', component: DocumentEditorView },
      { path: 'files', component: FilesView },
      { path: 'graph', component: GraphView },
      { path: 'contribution', component: ContributionView },
      { path: 'career', component: CareerInsightsView },
      { path: 'risk', component: RiskView },
      { path: 'git', component: GitView },
      { path: 'ai', component: AIView },
      { path: 'settings', component: SettingsView },
      { path: 'reminders', component: RemindersView },
      { path: 'audit', component: AuditView },
    ]
  },
  { path: '/', redirect: '/projects' },
]

// 导航守卫: beforeEach检查token → 未登录跳转/login
```

### 9.3 状态管理 (Pinia Stores)

| Store | 文件 | 职责 |
|-------|------|------|
| useUserStore | stores/user.ts | token, user, isLoggedIn, login/logout/register/fetchMe |
| useProjectStore | stores/project.ts | currentProject, projects, members, dashboard |
| useAIStore | stores/ai.ts | conversation, messages, isStreaming, sendMessage(SSE) |
| useNotificationStore | stores/notification.ts | notifications, unreadCount, markRead |

### 9.4 API层架构

```
api/http.ts
  └── axios实例: baseURL = VITE_API_BASE_URL || "http://127.0.0.1:8000/api"
       ├── 请求拦截器: headers.Authorization = `Bearer ${token}`
       └── 响应拦截器: 401 → 清除token → router.push('/login')

api/index.ts
  └── 按模块组织: authApi, projectApi, taskApi, conversationApi,
       documentApi, fileApi, notificationApi, aiApi, ...
```

### 9.5 通用组件说明

| 组件 | 功能 | 依赖 |
|------|------|------|
| AIAssistantDock.vue | 可拖拽浮窗，AI对话界面，支持SSE流式输出 | useAIStore |
| AppViewport.vue | 统一页面容器，padding/背景/滚动 | - |
| GraphCanvas.vue | 协作图谱渲染，节点/边/力导向布局 | AntV G6 5 |
| LineChart.vue | 折线图封装，活跃度趋势等 | ECharts 6 |
| RadarChart.vue | 雷达图封装，健康度/能力评估 | ECharts 6 |
| StatCard.vue | 统计卡片，图标+数值+标签 | @element-plus/icons-vue |

---

## 10. 数据流与请求链路

### 10.1 整体数据流

```
用户操作 → Vue组件 → api/index.ts → Axios → HTTP Request
    ↓                                                ↓
状态更新 ← Pinia Store ← JSON响应 ← 序列化 ← FastAPI路由处理器
    ↓                                                ↓
响应式渲染 ← Vue 模板 ← 数据绑定             services/ → ORM → SQLite
```

### 10.2 任务完整生命周期数据流

```
1. 组长创建任务
   POST /api/projects/{id}/tasks
   → Task表插入 → 自动创建Conversation(task类型) → 生成TaskActivity(created)
   → 生成CollaborationEvent → 发送Notification给assignee

2. 组长分配任务
   POST /api/tasks/{id}/assign
   → Task.assignee_id更新 → response_status="待接收"
   → TaskActivity(assigned) → Notification(task_assigned)

3. 成员接受任务
   POST /api/tasks/{id}/accept
   → response_status="已接收" → TaskActivity(accepted)

4. 成员开始处理
   POST /api/tasks/{id}/start
   → status="IN_PROGRESS" → TaskActivity(started)

5. 成员在任务会话中讨论
   POST /api/conversations/{id}/messages
   → Message表插入 → TaskActivity(commented)
   → WebSocket广播给同项目所有连接

6. 遇阻标记阻塞
   POST /api/tasks/{id}/block
   → status="BLOCKED" → TaskActivity(blocked)

7. 完成验收
   POST /api/tasks/{id}/complete
   → status="DONE" → progress=100 → TaskActivity(completed)
   → CollaborationEvent(task_completed)
```

### 10.3 邀请加入流程

```
组长 POST /api/projects/{id}/invitations {invitee_id, role, message}
    → ProjectInvitation表插入(status="pending")
    → Notification(project_invite)发送给被邀请者

被邀请者 GET /api/projects/me/invitations
    → 查看待处理邀请

被邀请者 POST /api/projects/invitations/{id}/accept
    → status="accepted" → ProjectMember表插入
    → Notification发送给组长

被邀请者 POST /api/projects/invitations/{id}/reject
    → status="rejected"
```

---

## 11. 运行与部署

### 11.1 环境要求

- Python 3.12+
- Node.js 18+（推荐 20 LTS）
- npm 或 pnpm

### 11.2 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选，不配置也可运行）
copy .env.example .env

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后自动执行：
1. 创建数据库表（Base.metadata.create_all）
2. 初始化种子数据（9个用户 + 8个项目 + 完整协作数据）
3. 暴露 API 文档

### 11.3 前端启动

```bash
cd frontend
npm install
npm run dev
```

默认地址：
- 前端: `http://localhost:5173`
- 后端API: `http://127.0.0.1:8000/api`
- Swagger文档: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 11.4 访问系统

打开浏览器访问 `http://localhost:5173`，使用演示账号登录（见第13节）。

---

## 12. 配置说明

### 12.1 后端环境变量 (backend/.env)

| 变量名 | 含义 | 默认值 |
|--------|------|--------|
| TEAMFLOW_LLM_API_KEY | LLM接口密钥 | 空（不配置则AI功能降级为规则引擎） |
| TEAMFLOW_LLM_BASE_URL | LLM接口地址 | `https://token-plan-cn.xiaomimimo.com/v1` |
| TEAMFLOW_LLM_MODEL | 模型名称 | `mimo-v2.5-pro` |
| TEAMFLOW_LLM_TIMEOUT_SECONDS | 请求超时(秒) | `20` |

### 12.2 前端环境变量

| 变量名 | 含义 | 默认值 |
|--------|------|--------|
| VITE_API_BASE_URL | 后端API地址 | `http://127.0.0.1:8000/api` |

### 12.3 LLM配置示例

**智谱GLM**:
```env
TEAMFLOW_LLM_API_KEY=your-zhipu-api-key
TEAMFLOW_LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
TEAMFLOW_LLM_MODEL=glm-4-flash
```

**Ollama本地**:
```env
TEAMFLOW_LLM_API_KEY=ollama
TEAMFLOW_LLM_BASE_URL=http://localhost:11434/v1
TEAMFLOW_LLM_MODEL=qwen2.5:7b
```

**Mimo（默认）**:
```env
TEAMFLOW_LLM_API_KEY=your-mimo-key
TEAMFLOW_LLM_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
TEAMFLOW_LLM_MODEL=mimo-v2.5-pro
```

### 12.4 无LLM时的行为

如果未配置LLM API Key：
- 传统功能（任务/消息/文档/文件/通知/仪表盘/图谱）完全正常
- AI对话功能无法使用（返回错误提示）
- 成员画像使用规则引擎兜底，仍可生成评分和基本画像
- 周报/任务规划/文档分析功能不可用

---

## 13. 演示账号与种子数据

### 13.1 演示账号（密码统一: 123456）

| 用户名 | 显示名 | 系统角色 | 项目角色 | 说明 |
|--------|--------|----------|----------|------|
| zhangsan | 张三 | student | 组长 | 项目负责人 |
| lisi | 李四 | student | 后端开发 | 核心开发 |
| wangwu | 王五 | student | 前端开发 | 核心开发 |
| zhaoliu | 赵六 | student | 数据库设计 | 数据库负责人 |
| sunqi | 孙七 | student | 文档负责人 | 文档沉淀 |
| zhouba | 周八 | student | 成员 | 预备成员 |
| wujiu | 吴九 | student | 前端开发 | 待邀请成员 |
| teacher | 王老师 | teacher | 指导教师 | 指导老师 |
| chenlaoshi | 陈老师 | teacher | 审计教师 | 过程化评估 |

### 13.2 种子数据内容

启动后端时自动初始化以下数据：

| 数据类型 | 数量 | 说明 |
|----------|------|------|
| 用户 | 9个 | 7个学生 + 2个教师 |
| 项目 | 8个 | 含课程设计、竞赛、科研等类型 |
| 项目成员 | 多组 | 每个项目3-7人 |
| 任务 | 多个 | 覆盖TODO/DOING/REVIEW/DONE/BLOCKED各状态 |
| 里程碑 | 多个 | 3-4阶段里程碑 |
| 文档 | 多个 | 含需求文档、设计文档、测试报告等 |
| 消息 | 多条 | 群聊、任务讨论、代码消息 |
| Git提交 | 多条 | 模拟提交记录（含分支、冲突风险） |
| 通知 | 多条 | 邀请通知、任务分配通知 |
| 协作事件 | 多条 | 项目创建、任务完成、文档编辑等 |
| 风险预警 | 多个 | 进度风险、质量风险、资源风险 |

### 13.3 重置数据库

删除 `backend/data/teamflow.db` 后重启后端即可自动重建。

---

## 14. 开发约定与设计模式

### 14.1 后端设计模式

| 模式 | 应用位置 | 说明 |
|------|----------|------|
| 依赖注入 | api/deps.py | FastAPI Depends: get_db, get_current_user, ensure_project_member |
| 服务层模式 | services/ | 路由只负责接收/返回，业务逻辑在services/ |
| 序列化器模式 | services/presenters.py | 统一将ORM对象转为前端可用JSON |
| 工厂模式 | core/seed.py | 种子数据创建采用工厂函数 |
| 观察者模式 | core/realtime.py | WebSocket连接管理器(ConnectionManager) |

### 14.2 前端设计模式

| 模式 | 应用位置 | 说明 |
|------|----------|------|
| 组合式API | 所有.vue | Vue 3 Composition API (<script setup>) |
| 状态管理模式 | stores/ | Pinia stores替代全局状态 |
| 拦截器模式 | api/http.ts | Axios请求/响应拦截器统一处理token和错误 |
| 布局组件模式 | layouts/ProjectLayout.vue | 统一项目内布局，子页面通过router-view渲染 |
| 容器/展示分离 | components/common/ | 通用组件与业务页面分离 |

### 14.3 命名约定

- **后端路由文件**: 按业务模块命名（auth.py, projects.py, tasks.py...）
- **前端页面**: 以View结尾（DashboardView.vue, TasksView.vue...）
- **API函数**: 以模块名+Api命名（authApi, projectApi, taskApi...）
- **数据库表**: 小写+下划线（project_members, task_activities...）
- **Python模块**: 小写+下划线（ai_service.py, member_insights.py...）

### 14.4 安全策略

- 密码使用 bcrypt 哈希存储（不存明文）
- JWT Token 7天过期，密钥通过环境变量配置
- API 通过依赖注入做双重校验：用户认证 + 项目成员校验
- AI 操作使用白名单机制（ALLOWED_ACTIONS），只允许12种安全操作
- 文件上传限制在项目内，通过成员校验控制访问

---

## 15. 常见问题

| 问题 | 解决方案 |
|------|----------|
| 前端能打开但数据不显示 | 确认后端运行在8000端口，检查VITE_API_BASE_URL配置 |
| 登录失败 | 默认密码是123456，如数据被清空重启后端即重新初始化 |
| AI功能不能用 | 检查TEAMFLOW_LLM_API_KEY是否配置，未配置时画像功能仍可用规则引擎 |
| 数据库坏了想重置 | 删除backend/data/teamflow.db后重启后端 |
| 文件上传失败 | 检查backend/uploads/是否存在且有写权限 |
| 端口被占用 | 修改uvicorn的--port参数和前端VITE_API_BASE_URL |

---

## 16. 课程设计相关（评分标准、答辩建议）

### 16.1 课程设计文档要求

按软件工程课程设计要求，需提交：
- 可行性分析与需求描述
- **传统方法学**: 数据流图（环境图+1层DFD）、系统结构图
- **面向对象方法学**: 类图、用例图
- 界面设计
- 数据库设计
- 选做部分（过程设计/顺序图可选其一）

### 16.2 评分权重

| 评分项目 | 权重 |
|----------|------|
| 选题说明与可行性分析 | 10% |
| 数据流图 | 15% |
| 软件结构 | 10% |
| 类图 | 15% |
| 用例图 | 10% |
| 界面设计 | 10% |
| 数据库设计 | 10% |
| 内容结构与排版 | 10% |
| 选做部分 | 10% |

### 16.3 答辩汇报要点

| 评分项目 | 权重 | 建议 |
|----------|------|------|
| 汇报PPT | 20% | 条理明确、内容全面、美观大方 |
| 讲解 | 30% | 自然流畅、表达清晰、时间恰当 |
| 功能实现 | 40% | 突出TokenFlow的AI智能分析创新点 |
| 回答问题 | 10% | 准备核心技术问题解答 |

### 16.4 项目创新点总结（答辩时重点突出）

1. **五层协作闭环设计**: 项目容器→任务主线→沟通触发→证据沉淀→AI分析
2. **19张表ER模型**: 覆盖协作全生命周期，从邀请到画像
3. **AI上下文快照机制**: AI不只是对话，而是理解当前页面+项目状态
4. **五维贡献评分算法**: 可解释的量化评分，不是黑盒统计
5. **LLM + 规则引擎双轨画像**: 有LLM时深度分析，无LLM时规则兜底
6. **SSE流式AI对话**: 实时输出+动作执行，不只是问答
7. **WebSocket实时通信**: 消息广播、心跳维持、多终端同步
8. **AntV G6协作图谱**: 可视化成员↔任务↔文档↔提交关系网络

---

## 补充文档

仓库中还有以下配套文档：

- [code.txt](./code.txt) — 全部源码汇总文件（可直接发给AI分析）
- [开发文档.md](./开发文档.md) — 项目开发指南
- [现有功能清单.md](./现有功能清单.md) — 完整功能清单
- [通信方案.md](./通信方案.md) — 通信与协作闭环优化方案
- [要求.md](./要求.md) — 软件工程课程设计要求原文
