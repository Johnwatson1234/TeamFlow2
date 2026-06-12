"""
TeamFlow2 代码汇总脚本
将所有主要源代码按逻辑顺序汇总到 code.txt，方便发给网页 AI 分析项目结构。
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PROJECT_NAME = "TeamFlow2"

TREE_STRUCTURE = r"""
TeamFlow2/
├── backend/                                    # FastAPI 后端服务
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                         # 依赖注入（认证/权限校验）
│   │   │   ├── router.py                       # 路由聚合入口
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py                     # 认证：注册/登录/个人信息
│   │   │       ├── ai.py                       # AI：对话(SSE流式)/规划/报告/分析
│   │   │       ├── projects.py                 # 项目：CRUD/成员/邀请/仪表盘/贡献/风险/Git
│   │   │       ├── tasks.py                    # 任务：CRUD/指派/里程碑/活动日志
│   │   │       ├── conversations.py            # 即时通信：会话/消息/已读
│   │   │       ├── documents.py                # 文档协作：CRUD/版本管理
│   │   │       ├── files.py                    # 文件管理：上传/列表/删除
│   │   │       ├── notifications.py            # 通知系统
│   │   │       └── websocket.py                # WebSocket 实时通信
│   │   ├── core/
│   │   │   ├── config.py                       # 配置管理（环境变量/LLM参数）
│   │   │   ├── security.py                     # JWT 认证 / 密码哈希
│   │   │   ├── realtime.py                     # WebSocket 连接管理器
│   │   │   └── seed.py                         # 演示数据初始化（9用户+完整项目数据）
│   │   ├── db/
│   │   │   └── session.py                      # SQLite 数据库连接
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── entities.py                     # 全部 19 张表的 SQLAlchemy 模型定义
│   │   ├── schemas/
│   │   │   └── common.py                       # 公共 Pydantic 响应模型
│   │   ├── services/
│   │   │   ├── ai_service.py                   # AI 助手核心（上下文快照/规划/周报/分析/动作执行）
│   │   │   ├── llm_service.py                  # LLM API 调用封装（兼容OpenAI格式）
│   │   │   ├── member_insights.py              # 成员贡献评分 / 职业画像分析
│   │   │   └── presenters.py                   # 数据序列化/格式化（项目/任务/成员/图表等）
│   │   ├── utils/
│   │   │   └── serializers.py                  # JSON 序列化/反序列化工具
│   │   ├── __init__.py
│   │   └── main.py                             # FastAPI 应用入口
│   ├── requirements.txt                        # Python 依赖清单
│   └── .env.example                            # 环境变量模板
│
├── frontend/                                   # Vue 3 前端应用
│   ├── src/
│   │   ├── api/
│   │   │   ├── http.ts                         # Axios 封装（拦截器/Token注入）
│   │   │   └── index.ts                        # 全部 API 接口定义（含SSE流式调用）
│   │   ├── router/
│   │   │   └── index.ts                        # 路由配置（17子页面+权限守卫）
│   │   ├── stores/                             # Pinia 状态管理
│   │   │   ├── user.ts                         # 用户认证状态
│   │   │   ├── project.ts                      # 项目数据状态
│   │   │   ├── ai.ts                           # AI 对话状态
│   │   │   └── notification.ts                 # 通知状态
│   │   ├── layouts/
│   │   │   └── ProjectLayout.vue               # 项目布局（侧边栏+AI助手Dock）
│   │   ├── components/common/                  # 通用组件
│   │   │   ├── AIAssistantDock.vue             # AI 助手浮窗
│   │   │   ├── AppViewport.vue                 # 视口容器
│   │   │   ├── GraphCanvas.vue                 # 关系图画布（AntV G6）
│   │   │   ├── LineChart.vue                   # 折线图
│   │   │   ├── RadarChart.vue                  # 雷达图
│   │   │   └── StatCard.vue                    # 统计卡片
│   │   ├── views/
│   │   │   ├── auth/
│   │   │   │   ├── LoginView.vue               # 登录页
│   │   │   │   └── RegisterView.vue            # 注册页
│   │   │   ├── projects/
│   │   │   │   └── ProjectListView.vue         # 项目列表页
│   │   │   └── project/                        # 项目内 17 个子页面
│   │   │       ├── DashboardView.vue           # 仪表盘
│   │   │       ├── TasksView.vue               # 任务管理
│   │   │       ├── MilestonesView.vue          # 里程碑
│   │   │       ├── MessagesView.vue            # 即时通信
│   │   │       ├── DocumentsView.vue           # 文档列表
│   │   │       ├── DocumentEditorView.vue      # 文档编辑器
│   │   │       ├── FilesView.vue               # 文件管理
│   │   │       ├── GraphView.vue               # 关系图谱
│   │   │       ├── ContributionView.vue        # 贡献评估
│   │   │       ├── CareerInsightsView.vue      # 职业画像
│   │   │       ├── RiskView.vue                # 风险预警
│   │   │       ├── GitView.vue                 # Git 追踪
│   │   │       ├── AIView.vue                  # AI 助手页面
│   │   │       ├── SettingsView.vue            # 项目设置
│   │   │       ├── RemindersView.vue           # 提醒管理
│   │   │       └── AuditView.vue               # 审计视图
│   │   ├── utils/
│   │   │   └── apiError.ts                     # API 错误处理
│   │   ├── App.vue                             # 根组件
│   │   └── main.ts                             # 应用入口
│   ├── package.json                            # Node 依赖配置
│   └── vite.config.ts                          # Vite 构建配置
│
├── collect_code.py                             # 本脚本
└── README.md
"""

LONG_FILE_LIMIT = 9000


# ============================================================
# 文件收集顺序（按逻辑依赖排序：底层 -> 上层）
# ============================================================
FILES_BACKEND = [
    # --- 配置 & 基础设施 ---
    ("backend/.env.example", ".env.example（环境变量模板）"),
    ("backend/requirements.txt", "requirements.txt（Python 依赖）"),
    ("backend/app/core/config.py", "core/config.py（配置管理）"),
    ("backend/app/db/session.py", "db/session.py（数据库连接）"),
    ("backend/app/utils/serializers.py", "utils/serializers.py（JSON 工具）"),
    ("backend/app/core/security.py", "core/security.py（JWT / 密码哈希）"),
    # --- 数据模型 & Schema ---
    ("backend/app/models/entities.py", "models/entities.py（全部 19 张表模型）"),
    ("backend/app/schemas/common.py", "schemas/common.py（响应模型）"),
    # --- 服务层 ---
    ("backend/app/core/seed.py", "core/seed.py（演示数据初始化）"),
    ("backend/app/core/realtime.py", "core/realtime.py（WebSocket 管理器）"),
    ("backend/app/services/presenters.py", "services/presenters.py（序列化器）"),
    ("backend/app/services/llm_service.py", "services/llm_service.py（LLM API 调用）"),
    ("backend/app/services/member_insights.py", "services/member_insights.py（贡献/画像）"),
    ("backend/app/services/ai_service.py", "services/ai_service.py（AI 核心逻辑）"),
    # --- API 层 ---
    ("backend/app/api/deps.py", "api/deps.py（注入：认证/权限）"),
    ("backend/app/api/router.py", "api/router.py（路由聚合）"),
    ("backend/app/api/routes/auth.py", "api/routes/auth.py（认证路由）"),
    ("backend/app/api/routes/projects.py", "api/routes/projects.py（项目路由）"),
    ("backend/app/api/routes/tasks.py", "api/routes/tasks.py（任务路由）"),
    ("backend/app/api/routes/conversations.py", "api/routes/conversations.py（聊天路由）"),
    ("backend/app/api/routes/documents.py", "api/routes/documents.py（文档路由）"),
    ("backend/app/api/routes/files.py", "api/routes/files.py（文件路由）"),
    ("backend/app/api/routes/notifications.py", "api/routes/notifications.py（通知路由）"),
    ("backend/app/api/routes/ai.py", "api/routes/ai.py（AI 路由）"),
    ("backend/app/api/routes/websocket.py", "api/routes/websocket.py（WebSocket 路由）"),
    # --- 入口 ---
    ("backend/app/main.py", "app/main.py（FastAPI 应用入口）"),
]

FILES_FRONTEND = [
    # --- 配置 ---
    ("frontend/package.json", "package.json（Node 依赖）"),
    ("frontend/vite.config.ts", "vite.config.ts（Vite 构建配置）"),
    # --- API 层 ---
    ("frontend/src/api/http.ts", "api/http.ts（Axios 封装）"),
    ("frontend/src/api/index.ts", "api/index.ts（全部 API 定义）"),
    # --- 工具 ---
    ("frontend/src/utils/apiError.ts", "utils/apiError.ts（错误处理）"),
    # --- 路由 ---
    ("frontend/src/router/index.ts", "router/index.ts（路由配置）"),
    # --- 状态管理 ---
    ("frontend/src/stores/user.ts", "stores/user.ts（用户状态）"),
    ("frontend/src/stores/project.ts", "stores/project.ts（项目状态）"),
    ("frontend/src/stores/ai.ts", "stores/ai.ts（AI 对话状态）"),
    ("frontend/src/stores/notification.ts", "stores/notification.ts（通知状态）"),
    # --- 布局 ---
    ("frontend/src/layouts/ProjectLayout.vue", "layouts/ProjectLayout.vue（项目布局）"),
    # --- 通用组件 ---
    ("frontend/src/components/common/AIAssistantDock.vue", "components/AIAssistantDock.vue（AI 助手浮窗）"),
    ("frontend/src/components/common/AppViewport.vue", "components/AppViewport.vue（视口容器）"),
    ("frontend/src/components/common/GraphCanvas.vue", "components/GraphCanvas.vue（关系图画布）"),
    ("frontend/src/components/common/LineChart.vue", "components/LineChart.vue（折线图）"),
    ("frontend/src/components/common/RadarChart.vue", "components/RadarChart.vue（雷达图）"),
    ("frontend/src/components/common/StatCard.vue", "components/StatCard.vue（统计卡片）"),
    # --- 认证页面 ---
    ("frontend/src/views/auth/LoginView.vue", "views/LoginView.vue（登录页）"),
    ("frontend/src/views/auth/RegisterView.vue", "views/RegisterView.vue（注册页）"),
    # --- 项目列表 ---
    ("frontend/src/views/projects/ProjectListView.vue", "views/ProjectListView.vue（项目列表）"),
    # --- 项目内页面 ---
    ("frontend/src/views/project/DashboardView.vue", "views/DashboardView.vue（仪表盘）"),
    ("frontend/src/views/project/TasksView.vue", "views/TasksView.vue（任务管理）"),
    ("frontend/src/views/project/MilestonesView.vue", "views/MilestonesView.vue（里程碑）"),
    ("frontend/src/views/project/MessagesView.vue", "views/MessagesView.vue（即时通信）"),
    ("frontend/src/views/project/DocumentsView.vue", "views/DocumentsView.vue（文档列表）"),
    ("frontend/src/views/project/DocumentEditorView.vue", "views/DocumentEditorView.vue（文档编辑器）"),
    ("frontend/src/views/project/FilesView.vue", "views/FilesView.vue（文件管理）"),
    ("frontend/src/views/project/GraphView.vue", "views/GraphView.vue（关系图谱）"),
    ("frontend/src/views/project/ContributionView.vue", "views/ContributionView.vue（贡献评估）"),
    ("frontend/src/views/project/CareerInsightsView.vue", "views/CareerInsightsView.vue（职业画像）"),
    ("frontend/src/views/project/RiskView.vue", "views/RiskView.vue（风险预警）"),
    ("frontend/src/views/project/GitView.vue", "views/GitView.vue（Git 追踪）"),
    ("frontend/src/views/project/AIView.vue", "views/AIView.vue（AI 助手页）"),
    ("frontend/src/views/project/SettingsView.vue", "views/SettingsView.vue（项目设置）"),
    ("frontend/src/views/project/RemindersView.vue", "views/RemindersView.vue（提醒管理）"),
    ("frontend/src/views/project/AuditView.vue", "views/AuditView.vue（审计视图）"),
    # --- 入口 ---
    ("frontend/src/App.vue", "App.vue（根组件）"),
    ("frontend/src/main.ts", "main.ts（应用入口）"),
]


def collect() -> None:
    output_path = ROOT / "code.txt"
    lines: list[str] = []

    lines.append("=" * 80)
    lines.append(f"  {PROJECT_NAME} — 项目完整代码汇总")
    lines.append("  面向软件工程课程设计的全栈智能团队协作管理系统")
    lines.append("=" * 80)
    lines.append("")
    lines.append("## 项目结构图")
    lines.append("")
    lines.append("```")
    lines.append(TREE_STRUCTURE.strip())
    lines.append("```")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")

    all_files = FILES_BACKEND + FILES_FRONTEND

    for rel_path, label in all_files:
        file_path = ROOT / rel_path
        if not file_path.is_file():
            lines.append(f"# [跳过] {label}  — 文件不存在: {rel_path}")
            lines.append("")
            continue

        raw = file_path.read_text(encoding="utf-8", errors="replace")
        truncated = False
        if len(raw) > LONG_FILE_LIMIT:
            raw = raw[:LONG_FILE_LIMIT] + "\n\n... (文件过长，已截断)..."
            truncated = True

        ext = file_path.suffix.lstrip(".")
        lang_map = {
            "py": "python",
            "ts": "typescript",
            "vue": "vue",
            "json": "json",
        }
        lang = lang_map.get(ext, "")

        lines.append("=" * 80)
        lines.append(f"## 文件: {rel_path}")
        lines.append(f"## 说明: {label}")
        if truncated:
            lines.append(f"## 注意: 文件原始大小 {len(raw)} 字符，已截断至头部 {LONG_FILE_LIMIT} 字符")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"```{lang}")
        lines.append(raw.rstrip())
        lines.append("```")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[完成] 已生成 {output_path}，共 {len(all_files)} 个文件。")


if __name__ == "__main__":
    collect()