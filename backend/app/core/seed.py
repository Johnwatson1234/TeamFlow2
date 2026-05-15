from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.entities import (
    AIReportHistory,
    AITaskSuggestion,
    CollaborationEvent,
    ContributionEvidence,
    ContributionScore,
    Conversation,
    ConversationMember,
    Document,
    DocumentVersion,
    FileResource,
    GitCommit,
    GitRepository,
    Message,
    Milestone,
    Notification,
    Project,
    ProjectInvitation,
    ProjectMember,
    PullRequest,
    RiskAlert,
    Task,
    TaskActivity,
    User,
)
from app.utils.serializers import dump_json


def avatar(name: str) -> str:
    return f"https://api.dicebear.com/7.x/adventurer/svg?seed={name}"


def seed_database() -> None:
    db = SessionLocal()
    try:
        _seed_users(db)
        db.commit()
        _seed_project_graph(db)
        _seed_extra_projects(db)
        _seed_pending_invites_for_default_user(db)
        db.commit()
    finally:
        db.close()


def _seed_users(db: Session) -> None:
    users = [
        ("zhangsan", "张三", "zhangsan@stu.edu.cn", "13800000001", "组长", "leader", "负责项目推进与协作管理。"),
        ("lisi", "李四", "lisi@stu.edu.cn", "13800000002", "后端开发", "student", "负责接口设计与服务层实现。"),
        ("wangwu", "王五", "wangwu@stu.edu.cn", "13800000003", "前端开发", "student", "负责页面实现与交互联调。"),
        ("zhaoliu", "赵六", "zhaoliu@stu.edu.cn", "13800000004", "数据库设计", "student", "负责数据库与测试数据。"),
        ("sunqi", "孙七", "sunqi@stu.edu.cn", "13800000005", "文档负责人", "student", "负责文档与资料沉淀。"),
        ("zhouba", "周八", "zhouba@stu.edu.cn", "13800000006", "成员", "student", "预备成员。"),
        ("wujiu", "吴九", "wujiu@stu.edu.cn", "13800000007", "前端开发", "student", "待邀请成员。"),
        ("teacher", "王老师", "wanglaoshi@university.edu.cn", "13800000008", "指导教师", "teacher", "负责课程设计指导与审计。"),
        ("chenlaoshi", "陈老师", "chenlaoshi@university.edu.cn", "13800000009", "审计教师", "teacher", "负责过程化评分与建议。"),
    ]
    for username, display_name, email, phone, title, role, bio in users:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            continue
        db.add(
            User(
                username=username,
                password_hash=get_password_hash("123456"),
                display_name=display_name,
                email=email,
                phone=phone,
                avatar=avatar(username),
                title=title,
                system_role=role,
                bio=bio,
            )
        )
    db.flush()


def _seed_project_graph(db: Session) -> None:
    users = {user.username: user for user in db.query(User).all()}
    existing_project = db.query(Project).filter(Project.name == "课程设计-小组协作管理系统").first()
    if existing_project:
        return
    project = Project(
        name="课程设计-小组协作管理系统",
        course_name="软件工程课程设计",
        description="本系统用于管理课程设计过程中的任务分配、文档协作、代码提交、讨论沟通与贡献评估，实现全过程可追溯、可视化与智能分析。",
        status="进行中",
        category="课程设计",
        start_date="2024-04-19",
        due_date="2024-06-15 23:59",
        repo_url="github.com/teamflow/course-design-system",
        advisor_name="王老师",
        advisor_email="wanglaoshi@university.edu.cn",
        tags_json=dump_json(["课程设计", "Java", "Spring Boot", "MySQL", "协作管理"]),
        owner_id=users["zhangsan"].id,
    )
    db.add(project)
    db.flush()

    members = [
        ("zhangsan", "组长", "全部权限", 82, "在线"),
        ("lisi", "后端开发", "编辑权限", 68, "在线"),
        ("wangwu", "前端开发", "编辑权限", 75, "离开"),
        ("zhaoliu", "数据库设计", "编辑权限", 54, "在线"),
        ("sunqi", "文档负责人", "只读权限", 46, "离线"),
        ("teacher", "教师", "查看权限", 0, "在线"),
    ]
    db.add_all(
        ProjectMember(
            project_id=project.id,
            user_id=users[username].id,
            role=role,
            permission_level=permission,
            workload=workload,
            online_status=status,
        )
        for username, role, permission, workload, status in members
    )
    db.flush()

    invitations = [
        ProjectInvitation(
            project_id=project.id,
            inviter_id=users["zhangsan"].id,
            invitee_id=users["zhouba"].id,
            role="成员",
            message="可填写邀请说明，帮助对方了解加入项目的目的与分工。",
            status="pending",
        ),
        ProjectInvitation(
            project_id=project.id,
            inviter_id=users["zhangsan"].id,
            invitee_id=users["wujiu"].id,
            role="前端开发",
            message="需要一位前端同学协助消息页和任务页交互细节优化。",
            status="accepted",
            responded_at=datetime.utcnow() - timedelta(days=1),
        ),
        ProjectInvitation(
            project_id=project.id,
            inviter_id=users["zhangsan"].id,
            invitee_id=users["chenlaoshi"].id,
            role="成员",
            message="邀请协助审阅课设材料。",
            status="rejected",
            responded_at=datetime.utcnow() - timedelta(days=2),
        ),
        ProjectInvitation(
            project_id=project.id,
            inviter_id=users["lisi"].id,
            invitee_id=users["wangwu"].id,
            role="前端开发",
            message="图书管理系统项目邀请。",
            status="pending",
        ),
        ProjectInvitation(
            project_id=project.id,
            inviter_id=users["wangwu"].id,
            invitee_id=users["zhangsan"].id,
            role="后端开发",
            message="校园二手交易平台邀请。",
            status="pending",
        ),
        ProjectInvitation(
            project_id=project.id,
            inviter_id=users["zhaoliu"].id,
            invitee_id=users["zhangsan"].id,
            role="数据分析师",
            message="大数据分析可视化系统邀请。",
            status="pending",
        ),
    ]
    db.add_all(invitations)
    db.flush()

    milestone_names = [
        ("需求分析", "2024-05-05", "已完成"),
        ("总体设计", "2024-05-12", "已完成"),
        ("详细设计", "2024-05-19", "进行中"),
        ("编码实现", "2024-05-26", "待开始"),
        ("系统测试", "2024-06-02", "待开始"),
        ("验收交付", "2024-06-09", "待开始"),
    ]
    milestones = []
    for index, (name, due_date, status) in enumerate(milestone_names):
        milestone = Milestone(
            project_id=project.id,
            name=name,
            due_date=due_date,
            status=status,
            order_index=index,
        )
        milestones.append(milestone)
    db.add_all(milestones)
    db.flush()

    task_specs = [
        ("需求调研与分析", "TODO", "中", 0, "李四", "2024-05-22", milestones[2].id, "", "REQ-202405-001"),
        ("技术选型评估", "TODO", "低", 0, "王五", "2024-05-24", milestones[2].id, "", "REQ-202405-002"),
        ("数据库设计", "TODO", "中", 0, "孙七", "2024-05-25", milestones[2].id, "", "REQ-202405-003"),
        ("用户模块开发", "IN_PROGRESS", "高", 60, "张三", "2024-05-20", milestones[2].id, "", "REQ-202405-007"),
        ("任务模块开发", "IN_PROGRESS", "高", 45, "赵六", "2024-05-21", milestones[2].id, "", "REQ-202405-008"),
        ("消息模块开发", "IN_PROGRESS", "中", 30, "周八", "2024-05-23", milestones[2].id, "", "REQ-202405-009"),
        ("文档导出功能开发", "BLOCKED", "高", 10, "吴九", "2024-05-19", milestones[3].id, "接口未定义", "REQ-202405-010"),
        ("权限控制优化", "BLOCKED", "中", 20, "陈老师", "2024-05-18", milestones[3].id, "设计评审未通过", "REQ-202405-011"),
        ("项目配置模块", "REVIEW", "中", 90, "李四", "2024-05-17", milestones[2].id, "", "REQ-202405-012"),
        ("文件上传下载功能", "REVIEW", "中", 80, "王五", "2024-05-16", milestones[2].id, "", "REQ-202405-013"),
        ("日志审计模块", "REVIEW", "低", 70, "孙七", "2024-05-15", milestones[2].id, "", "REQ-202405-014"),
        ("登录功能开发", "DONE", "高", 100, "张三", "2024-05-10", milestones[1].id, "", "REQ-202405-015"),
        ("注册功能开发", "DONE", "中", 100, "赵六", "2024-05-09", milestones[1].id, "", "REQ-202405-016"),
        ("项目创建功能", "DONE", "中", 100, "周八", "2024-05-08", milestones[1].id, "", "REQ-202405-017"),
    ]
    name_to_username = {
        "张三": "zhangsan",
        "李四": "lisi",
        "王五": "wangwu",
        "赵六": "zhaoliu",
        "孙七": "sunqi",
        "周八": "zhouba",
        "吴九": "wujiu",
        "陈老师": "chenlaoshi",
    }
    tasks = []
    for title, status, priority, progress, owner_name, due_date, milestone_id, blocker, req in task_specs:
        response_status = {
            "TODO": "待接收" if progress == 0 else "未分配",
            "IN_PROGRESS": "处理中",
            "BLOCKED": "阻塞中",
            "REVIEW": "待验收",
            "DONE": "已完成",
        }[status]
        task = Task(
            project_id=project.id,
            milestone_id=milestone_id,
            title=title,
            description=f"围绕 {title} 完成项目交付要求，并和相关成员进行协同推进。",
            status=status,
            response_status=response_status,
            priority=priority,
            progress=progress,
            assignee_id=users[name_to_username[owner_name]].id if owner_name in name_to_username else None,
            due_date=due_date,
            start_date="2024-05-08",
            blocker_reason=blocker,
            related_requirement=req,
            related_document="用户模块设计文档 v1.2",
            related_commit="a1b2c3d",
            created_by=users["zhangsan"].id,
        )
        tasks.append(task)
    db.add_all(tasks)
    db.flush()

    group = Conversation(
        project_id=project.id,
        conversation_type="project_group",
        name="项目群聊",
        created_by=users["zhangsan"].id,
        is_pinned=True,
    )
    task_conv = Conversation(
        project_id=project.id,
        conversation_type="task",
        related_task_id=tasks[3].id,
        name=f"任务 #{tasks[3].id} 用户模块开发",
        created_by=users["zhangsan"].id,
        is_pinned=True,
    )
    task_conv2 = Conversation(
        project_id=project.id,
        conversation_type="task",
        related_task_id=tasks[2].id,
        name=f"任务 #{tasks[2].id} 数据库设计",
        created_by=users["zhangsan"].id,
    )
    system_conv = Conversation(
        project_id=project.id,
        conversation_type="system",
        name="系统通知",
        created_by=users["zhangsan"].id,
    )
    db.add_all([group, task_conv, task_conv2, system_conv])
    db.flush()

    project_usernames = ["zhangsan", "lisi", "wangwu", "zhaoliu", "sunqi", "teacher"]
    memberships = []
    for conversation in [group, task_conv, task_conv2, system_conv]:
        for username in project_usernames:
            memberships.append(
                ConversationMember(
                    conversation_id=conversation.id,
                    user_id=users[username].id,
                )
            )
    db.add_all(memberships)
    db.flush()

    messages = [
        Message(project_id=project.id, conversation_id=task_conv.id, sender_id=users["lisi"].id, content="@前端组 新的登录接口已开发完成，请对接测试哈。", message_type="text"),
        Message(project_id=project.id, conversation_id=task_conv.id, sender_id=users["wangwu"].id, content="收到，我这边先调试一下，有问题 @李四", message_type="text"),
        Message(project_id=project.id, conversation_id=task_conv.id, sender_id=users["lisi"].id, content='@GetMapping("/user/info")\npublic Result<UserInfo> getUserInfo(){\n    return Result.success(userService.getUserInfo());\n}', message_type="code", code_language="Java"),
        Message(project_id=project.id, conversation_id=task_conv.id, sender_id=users["zhaoliu"].id, content="关联任务 #23 用户模块开发\n接口文档已更新，包含登录、注册、用户信息接口", message_type="task"),
        Message(project_id=project.id, conversation_id=task_conv.id, sender_id=users["zhangsan"].id, content="用户模块接口文档 v1.2.docx\n1.24 MB", message_type="file"),
        Message(project_id=project.id, conversation_id=task_conv.id, sender_id=users["sunqi"].id, content="第 3 个接口的返回码是不是少了 401？", message_type="text"),
        Message(project_id=project.id, conversation_id=group.id, sender_id=users["zhangsan"].id, content="本周我们先把文档和看板完善起来，演示链路要跑顺。", message_type="text"),
        Message(project_id=project.id, conversation_id=system_conv.id, sender_id=users["teacher"].id, content="AI 项目经理已生成本周周报，请查看。", message_type="text"),
    ]
    db.add_all(messages)
    db.flush()

    activities = [
        ("updated", "李四 更新了任务进度 60% -> 68%", tasks[3].id, users["lisi"].id),
        ("uploaded", "李四 上传了文件 用户模块接口文档 v1.2.docx", tasks[3].id, users["lisi"].id),
        ("changed", "王五 将截止日期延后 1 天 变更为 2024-06-05", tasks[3].id, users["wangwu"].id),
        ("commented", "赵六 留下评论 请大家评审接口文档", tasks[3].id, users["zhaoliu"].id),
        ("started", "孙七 将任务状态从 待处理 -> 进行中", tasks[0].id, users["sunqi"].id),
    ]
    db.add_all(
        TaskActivity(
            task_id=task_id,
            project_id=project.id,
            actor_id=actor,
            activity_type=activity_type,
            content=content,
            from_value="",
            to_value="",
        )
        for activity_type, content, task_id, actor in activities
    )

    documents = [
        Document(
            project_id=project.id,
            title="需求分析说明书",
            content="# 需求分析说明书\n\n梳理用户角色与业务流程。",
            author_id=users["lisi"].id,
            updated_by_id=users["lisi"].id,
            version_count=2,
            permission_status="团队可编辑",
            tags_json=dump_json(["需求", "分析"]),
            related_task_id=tasks[0].id,
        ),
        Document(
            project_id=project.id,
            title="系统设计说明书",
            content="# 系统设计说明书\n\n系统采用前后端分离架构。",
            author_id=users["wangwu"].id,
            updated_by_id=users["wangwu"].id,
            version_count=3,
            permission_status="团队可编辑",
            tags_json=dump_json(["设计", "架构"]),
            related_task_id=tasks[3].id,
        ),
        Document(
            project_id=project.id,
            title="数据库设计说明书",
            content="# 数据库设计说明书\n\n包含 ER 图与核心表结构。",
            author_id=users["zhaoliu"].id,
            updated_by_id=users["zhaoliu"].id,
            version_count=1,
            permission_status="团队可编辑",
            tags_json=dump_json(["数据库"]),
            related_task_id=tasks[4].id,
        ),
        Document(
            project_id=project.id,
            title="接口设计说明书",
            content="# 接口设计说明书\n\n描述认证、项目、任务与消息接口。",
            author_id=users["sunqi"].id,
            updated_by_id=users["sunqi"].id,
            version_count=1,
            permission_status="团队可编辑",
            tags_json=dump_json(["接口"]),
            related_task_id=tasks[3].id,
        ),
    ]
    db.add_all(documents)
    db.flush()

    db.add_all(
        [
            DocumentVersion(document_id=documents[1].id, version_label="v1.3", summary="完善系统架构与模块描述", content=documents[1].content, author_id=users["zhangsan"].id, added_words=48, modified_words=22),
            DocumentVersion(document_id=documents[1].id, version_label="v1.2", summary="完善功能模块表格", content=documents[1].content, author_id=users["lisi"].id, added_words=30, modified_words=18),
            DocumentVersion(document_id=documents[1].id, version_label="v1.1", summary="补充总体架构图", content=documents[1].content, author_id=users["wangwu"].id, added_words=16, modified_words=8),
        ]
    )

    file_rows = [
        ("需求规格说明书 v1.2.docx", "文档", "需求分析", "lisi", "v1.2", "已通过", 12, "需求", "2.4 MB"),
        ("系统设计报告 v0.9.pptx", "演示文稿", "系统设计", "wangwu", "v0.9", "待评审", 6, "设计", "4.8 MB"),
        ("数据库设计 v1.1.xlsx", "表格", "数据库设计", "zhaoliu", "v1.1", "已通过", 9, "数据库", "1.2 MB"),
        ("接口文档 v1.0.pdf", "PDF", "接口开发", "sunqi", "v1.0", "已通过", 15, "接口", "1.0 MB"),
        ("用户模块代码.zip", "压缩包", "用户模块开发", "zhangsan", "v2.3", "待评审", 18, "代码", "12.6 MB"),
        ("数据库ER图 v1.0.png", "图片", "数据库设计", "wangwu", "v1.0", "退回修改", 3, "数据库", "860 KB"),
        ("项目演示录屏.mp4", "视频", "系统演示", "lisi", "v1.0", "已通过", 21, "演示", "48 MB"),
        ("API接口定义.json", "代码", "接口开发", "zhaoliu", "v1.4", "已通过", 7, "接口", "320 KB"),
    ]
    db.add_all(
        FileResource(
            project_id=project.id,
            name=name,
            file_type=file_type,
            related_task=related_task,
            uploader_id=users[uploader].id,
            version_label=version_label,
            review_status=status,
            download_count=downloads,
            category=category,
            storage_path=f"/需求文档/{name}",
            size_label=size,
            description="项目需求文档，包含功能需求、非功能需求等。",
            comments_json=dump_json(
                [
                    {"author": "王五", "time": "2024-05-18 16:40", "content": "整体结构清晰，建议补充性能需求章节。"},
                    {"author": "张三", "time": "2024-05-18 16:55", "content": "已根据建议补充，并以 v1.2 版本提交。"},
                ]
            ),
        )
        for name, file_type, related_task, uploader, version_label, status, downloads, category, size in file_rows
    )

    events = [
        ("task", "张三 创建了任务", "单元测试与集成测试", "task", tasks[0].id, users["zhangsan"].id, 4.0),
        ("message", "孙七 发表了讨论", "关于任务依赖关系的调整", "message", messages[0].id, users["sunqi"].id, 3.0),
        ("file", "赵六 上传了文档", "需求规格说明书 v1.2.docx", "file", 1, users["zhaoliu"].id, 2.5),
        ("code", "李四 提交了代码到仓库", "feat: 完成任务分配模块开发", "commit", 1, users["lisi"].id, 5.0),
        ("task", "王五 更新了任务进度", "任务：界面原型设计", "task", tasks[3].id, users["wangwu"].id, 4.0),
    ]
    db.add_all(
        CollaborationEvent(
            project_id=project.id,
            actor_id=actor_id,
            event_type=event_type,
            title=title,
            content=content,
            related_type=related_type,
            related_id=related_id,
            score_value=score,
        )
        for event_type, title, content, related_type, related_id, actor_id, score in events
    )

    score_rows = [
        ("zhangsan", 92.5, 24, 18, 22, 14, 14, 10, 38),
        ("lisi", 78.1, 19, 12, 18, 14, 15, 8, 30),
        ("wangwu", 65.2, 14, 10, 12, 13, 16, 7, 24),
        ("zhaoliu", 45.6, 11, 8, 10, 8, 8, 4, 16),
        ("sunqi", 32.8, 8, 6, 4, 6, 8, 3, 12),
        ("zhouba", 20.7, 5, 3, 4, 4, 4, 2, 8),
    ]
    db.add_all(
        ContributionScore(
            project_id=project.id,
            user_id=users[username].id,
            total_score=total,
            task_score=task_score,
            document_score=document_score,
            code_score=code_score,
            response_score=response_score,
            stability_score=stability_score,
            completed_tasks=done_count,
            collaboration_events=event_count,
        )
        for username, total, task_score, document_score, code_score, response_score, stability_score, done_count, event_count in score_rows
    )

    evidence_rows = [
        ("zhangsan", "代码提交", "完成权限管理模块核心提交", 8.5, "commit", 1),
        ("lisi", "文档贡献", "补充系统架构章节", 6.2, "document", documents[1].id),
        ("wangwu", "任务完成", "完成文件共享页视觉收敛", 7.1, "task", tasks[9].id),
        ("zhaoliu", "评审参与", "参与数据库设计评审", 4.2, "review", 2),
        ("sunqi", "消息讨论", "在接口讨论中推动统一返回结构", 3.5, "message", messages[1].id),
    ]
    db.add_all(
        ContributionEvidence(
            project_id=project.id,
            user_id=users[username].id,
            evidence_type=evidence_type,
            summary=summary,
            score=score,
            related_type=related_type,
            related_id=related_id,
        )
        for username, evidence_type, summary, score, related_type, related_id in evidence_rows
    )

    risk_rows = [
        ("3 个任务已延期", "高", 88, "请关注并及时调整计划", "建议重新分配资源或拆分任务。", "进度风险", "05-18"),
        ("代码提交频率下降", "中", 63, "近 3 天提交次数减少约 45%", "先合并 develop 分支，增加代码同步频率。", "代码风险", "05-18"),
        ("文档更新滞后", "低", 34, "2 个文档超过 7 天未更新", "安排文档负责人补齐最新流程图与接口说明。", "文档风险", "05-17"),
        ("检测到 12 个文件存在合并冲突风险", "高", 92, "修改热点集中在任务列表与权限模块", "建议尽快处理以避免产生大面积冲突。", "合并风险", "05-18"),
    ]
    db.add_all(
        RiskAlert(
            project_id=project.id,
            title=title,
            level=level,
            score=score,
            reason=reason,
            suggestion=suggestion,
            risk_type=risk_type,
            due_at=due_at,
        )
        for title, level, score, reason, suggestion, risk_type, due_at in risk_rows
    )

    repo = GitRepository(
        project_id=project.id,
        name="teamflow-course-design",
        url="github.com/teamflow/course-design-system.git",
        default_branch="main",
        sync_status="success",
        webhook_status="configured",
        last_synced_at="2024-05-18 16:42",
        ci_status="通过",
        total_commits=128,
    )
    db.add(repo)
    db.flush()

    commit_rows = [
        ("zhangsan", "a1b2c3d", "feature/auth", "修改 6 个文件", 142, 23, 85, 92, "#23"),
        ("wangwu", "b2c3d4e", "develop", "修改 3 个文件", 28, 11, 78, 81, "#18"),
        ("zhaoliu", "c3d4e5f", "feature/doc", "修改 1 个文件", 56, 0, 92, 90, "#12"),
        ("sunqi", "d4e5f6g", "feature/db", "修改 4 个文件", 196, 3, 88, 84, "#15"),
        ("zhouba", "e5f6g7h", "feature/ui", "perf: 5 个文件", 87, 14, 76, 80, "#25"),
        ("wujiu", "f6g7h8i", "hotfix/issue-41", "修改 2 个文件", 23, 7, 80, 72, "#41"),
        ("zhangsan", "g7h8i9j", "main", "修改 2 个文件", 12, 2, 70, 76, ""),
    ]
    db.add_all(
        GitCommit(
            project_id=project.id,
            user_id=users[username].id,
            commit_hash=commit_hash,
            branch_name=branch,
            message=message,
            changed_files_json=dump_json(
                [
                    "src/views/TaskList.vue",
                    "src/api/task.ts",
                    "src/store/user.ts",
                ]
            ),
            added_lines=added,
            deleted_lines=deleted,
            risk_score=risk,
            quality_score=quality,
            related_task=task_ref,
        )
        for username, commit_hash, branch, message, added, deleted, risk, quality, task_ref in commit_rows
    )

    pr_rows = [
        ("feat: 用户登录与权限控制", "feature/auth", "zhangsan", "待审核", ["lisi", "wangwu"]),
        ("fix: 修复任务列表分页问题", "fix/pagination", "wangwu", "待审核", ["zhangsan"]),
        ("feat: 数据库初始化脚本", "feature/db", "sunqi", "已通过", ["zhangsan", "lisi"]),
        ("perf: 优化图表渲染性能", "feature/chart", "zhouba", "修改中", ["wangwu"]),
        ("chore: 依赖版本升级", "chore/deps", "zhangsan", "已合并", []),
    ]
    db.add_all(
        PullRequest(
            project_id=project.id,
            title=title,
            branch_name=branch,
            author_id=users[author].id,
            status=status,
            reviewers_json=dump_json(reviewers),
        )
        for title, branch, author, status, reviewers in pr_rows
    )

    suggestion = AITaskSuggestion(
        project_id=project.id,
        title="TeamFlow AI 任务规划",
        input_payload=dump_json(
            {
                "projectName": project.name,
                "deadline": project.due_date,
                "techStack": "Vue 3, TypeScript, FastAPI, SQLite",
                "members": [
                    {"name": "张三", "role": "组长"},
                    {"name": "李四", "role": "后端开发"},
                    {"name": "王五", "role": "前端开发"},
                    {"name": "赵六", "role": "数据库设计"},
                    {"name": "孙七", "role": "文档负责人"},
                ],
            }
        ),
        output_payload=dump_json(
            {
                "phases": [
                    {"step": 1, "title": "需求分析", "date": "5.06 - 5.12"},
                    {"step": 2, "title": "系统设计", "date": "5.13 - 5.19"},
                    {"step": 3, "title": "编码实现", "date": "5.20 - 6.02"},
                    {"step": 4, "title": "测试与整合", "date": "6.03 - 6.09"},
                    {"step": 5, "title": "验收与文档", "date": "6.10 - 6.12"},
                ],
                "tasks": [
                    {"name": "数据库设计（ER 图）", "owner": "李四", "priority": "高", "hours": "8h", "deadline": "5-15", "status": "进行中"},
                    {"name": "功能模块设计", "owner": "张三", "priority": "高", "hours": "12h", "deadline": "5-16", "status": "进行中"},
                    {"name": "接口设计（API）", "owner": "王五", "priority": "中", "hours": "8h", "deadline": "5-17", "status": "未开始"},
                    {"name": "UI 原型设计", "owner": "赵六", "priority": "中", "hours": "10h", "deadline": "5-18", "status": "未开始"},
                    {"name": "技术选型与方案说明书", "owner": "孙七", "priority": "低", "hours": "6h", "deadline": "5-19", "status": "未开始"},
                ],
                "risks": [
                    {"name": "需求理解不一致", "level": "高", "impact": "返工，进度延迟", "suggestion": "组织需求评审，明确范围"},
                    {"name": "接口设计不合理", "level": "中", "impact": "联调困难，返工", "suggestion": "遵循 REST 规范，尽早评审"},
                    {"name": "时间估算偏差", "level": "中", "impact": "任务延期", "suggestion": "预留 20% 缓冲，持续跟踪"},
                    {"name": "成员经验不足", "level": "低", "impact": "效率降低", "suggestion": "合理分配任务，结对互助"},
                ],
                "suggestions": [
                    "当前处于系统设计阶段，建议在 5/19 前完成设计评审，为编码预留缓冲时间。",
                    "可并行推进数据库设计与 API 设计，提高效率。",
                    "建议每两天进行一次阶段同步，及时对齐设计细节。",
                ],
            }
        ),
        status="confirmed",
    )
    db.add(suggestion)
    db.add(
        AIReportHistory(
            project_id=project.id,
            report_type="weekly",
            content="本周项目完成了用户模块接口设计和项目设置页视觉收敛，风险主要集中在文档导出功能阻塞与合并冲突上，建议优先清理热点文件。",
        )
    )

    notification_rows = [
        ("zhangsan", "project_invite", "周八 @你", "在任务「用户模块接口开发」中提到了你", "message", messages[0].id, False),
        ("zhangsan", "task_assigned", "任务已分配给你", "任务「数据库表结构设计」已分配给你", "task", tasks[2].id, False),
        ("zhangsan", "task_comment", "孙七 评论了你的任务", "在任务「需求分析报告撰写」中评论了你", "task", tasks[0].id, False),
        ("zhangsan", "document", "文档已更新", "《需求规格说明书 v1.2》已更新", "document", documents[0].id, True),
        ("zhangsan", "risk", "风险预警", "检测到「用户模块接口开发」存在延期风险", "risk", 1, False),
        ("zhangsan", "message", "新回复", "「接口设计讨论」中有新回复", "message", task_conv.id, True),
        ("zhouba", "project_invite", f"{project.name}", "邀请你加入课程设计项目", "project", project.id, False),
        ("wujiu", "project_invite", f"{project.name}", "邀请你担任前端开发", "project", project.id, True),
        ("teacher", "system", "AI 项目经理周报", "请查看本周项目周报和风险总结", "ai", suggestion.id, False),
    ]
    db.add_all(
        Notification(
            user_id=users[username].id,
            project_id=project.id,
            type=type_,
            title=title,
            content=content,
            ref_type=ref_type,
            ref_id=ref_id,
            is_read=is_read,
            read_at=datetime.utcnow() if is_read else None,
        )
        for username, type_, title, content, ref_type, ref_id, is_read in notification_rows
    )


def _seed_extra_projects(db: Session) -> None:
    users = {user.username: user for user in db.query(User).all()}
    demos = [
        {
            "name": "软件工程实践课程设计",
            "course_name": "软件工程课程设计",
            "description": "软件工程实验全过程管理与工具实现。",
            "category": "课程设计",
            "owner": "lisi",
            "status": "进行中",
            "due_date": "2024-06-15 23:59",
            "repo_slug": "software-engineering-lab",
            "members": [("lisi", "组长"), ("zhangsan", "后端开发"), ("wangwu", "前端开发"), ("zhaoliu", "数据库设计"), ("sunqi", "文档负责人")],
            "focus": ["需求梳理", "接口设计", "任务联动", "联调测试", "答辩准备"],
        },
        {
            "name": "智能问答系统开发",
            "course_name": "人工智能应用实践",
            "description": "面向教育领域的智能问答系统研究与实现。",
            "category": "科研项目",
            "owner": "wangwu",
            "status": "进行中",
            "due_date": "2024-07-01 23:59",
            "repo_slug": "qa-research-platform",
            "members": [("wangwu", "组长"), ("zhangsan", "产品设计"), ("lisi", "后端开发"), ("sunqi", "文档负责人")],
            "focus": ["知识库建模", "问答引擎开发", "提示词优化", "评测集构建", "论文材料整理"],
        },
        {
            "name": "ACM 集训队管理平台",
            "course_name": "竞赛项目管理",
            "description": "用于集训队训练与比赛过程管理。",
            "category": "竞赛项目",
            "owner": "zhaoliu",
            "status": "进行中",
            "due_date": "2024-05-30 23:59",
            "repo_slug": "acm-training-board",
            "members": [("zhaoliu", "组长"), ("zhangsan", "后端开发"), ("wangwu", "前端开发"), ("zhouba", "成员")],
            "focus": ["训练计划管理", "队员评分", "题库导入", "比赛复盘", "成长画像"],
        },
        {
            "name": "毕业设计：推荐系统",
            "course_name": "毕业设计",
            "description": "基于协同过滤的个性化推荐系统设计。",
            "category": "课程设计",
            "owner": "sunqi",
            "status": "进行中",
            "due_date": "2024-06-05 23:59",
            "repo_slug": "recommendation-capstone",
            "members": [("sunqi", "组长"), ("zhangsan", "项目成员"), ("lisi", "算法支持"), ("wangwu", "前端实现")],
            "focus": ["需求分析", "召回策略", "排序模型", "界面联调", "实验报告"],
        },
        {
            "name": "竞赛训练协作面板",
            "course_name": "算法竞赛专题训练",
            "description": "围绕训练计划、榜单与题解沉淀的竞赛协作项目。",
            "category": "竞赛项目",
            "owner": "zhangsan",
            "status": "进行中",
            "due_date": "2024-06-18 23:59",
            "repo_slug": "contest-collaboration-dashboard",
            "members": [("zhangsan", "组长"), ("wangwu", "前端开发"), ("zhouba", "训练负责人"), ("lisi", "数据分析")],
            "focus": ["训练日历", "题单管理", "榜单分析", "错题复盘", "周报生成"],
        },
        {
            "name": "开源社团门户改版",
            "course_name": "学生组织数字化改造",
            "description": "面向社团招新、活动发布与资料沉淀的门户改版项目。",
            "category": "其他项目",
            "owner": "zhangsan",
            "status": "进行中",
            "due_date": "2024-06-28 23:59",
            "repo_slug": "club-portal-revamp",
            "members": [("zhangsan", "负责人"), ("sunqi", "内容运营"), ("wangwu", "前端实现"), ("lisi", "接口支持")],
            "focus": ["信息架构梳理", "首页改版", "活动发布", "权限分层", "上线巡检"],
        },
        {
            "name": "旧版项目存档示例",
            "course_name": "历史项目",
            "description": "历史项目归档，仅供查看。",
            "category": "其他项目",
            "owner": "teacher",
            "status": "已结束",
            "due_date": "2024-04-01 23:59",
            "repo_slug": "archived-project-sample",
            "members": [("teacher", "教师"), ("zhangsan", "成员"), ("lisi", "成员")],
            "focus": ["归档整理", "答辩材料", "复盘总结", "过程审计", "成果展示"],
        },
    ]
    for item in demos:
        project = db.query(Project).filter(Project.name == item["name"]).first()
        if not project:
            project = Project(name=item["name"], course_name=item["course_name"], owner_id=users[item["owner"]].id)
            db.add(project)
            db.flush()
        project.course_name = item["course_name"]
        project.description = item["description"]
        project.status = item["status"]
        project.category = item["category"]
        project.start_date = "2024-04-19"
        project.due_date = item["due_date"]
        project.repo_url = f"github.com/teamflow/{item['repo_slug']}"
        project.advisor_name = "王老师"
        project.advisor_email = "wanglaoshi@university.edu.cn"
        project.tags_json = dump_json([item["category"], "TeamFlow 演示", item["course_name"]])
        project.owner_id = users[item["owner"]].id
        db.flush()
        for index, (username, role) in enumerate(item["members"]):
            _ensure_project_member(
                db,
                project.id,
                users[username].id,
                role=role,
                permission_level="编辑权限" if "教师" not in role else "查看权限",
                workload=max(25, 84 - index * 8),
                online_status="在线" if index < 2 else "离开",
            )
        planning = _ensure_milestone(
            db,
            project.id,
            "阶段规划",
            due_date="2024-05-20",
            status="已完成" if item["status"] != "已结束" else "已完成",
            order_index=0,
        )
        execution = _ensure_milestone(
            db,
            project.id,
            "开发迭代",
            due_date=item["due_date"],
            status="已完成" if item["status"] == "已结束" else "进行中",
            order_index=1,
        )
        task_statuses = (
            [("DONE", 100), ("DONE", 100), ("DONE", 100), ("DONE", 100), ("DONE", 100)]
            if item["status"] == "已结束"
            else [("DONE", 100), ("IN_PROGRESS", 72), ("IN_PROGRESS", 48), ("REVIEW", 88), ("TODO", 12)]
        )
        tasks = []
        for index, focus in enumerate(item["focus"]):
            owner_username = item["members"][index % len(item["members"])][0]
            status, progress = task_statuses[index]
            task = _ensure_task(
                db,
                project.id,
                focus,
                milestone_id=planning.id if index < 2 else execution.id,
                description=f"{item['name']} 的演示任务：{focus}，用于展示任务协作、进度跟踪和过程记录。",
                status=status,
                response_status=_task_response_status(status, progress),
                priority="高" if index < 2 else "中",
                progress=progress,
                assignee_id=users[owner_username].id,
                due_date=item["due_date"],
                start_date="2024-05-01",
                blocker_reason="等待接口对齐" if status == "REVIEW" else "",
                related_requirement=f"REQ-{project.id:03d}-{index + 1:02d}",
                related_document=f"{item['name']} 演示说明 v1.{index}",
                related_commit=f"{item['repo_slug'][:6]}{index + 1}",
                created_by=users[item["owner"]].id,
            )
            tasks.append(task)
        overview_doc = _ensure_document(
            db,
            project.id,
            f"{item['name']} - 项目说明文档",
            content=f"# {item['name']}\n\n项目分类：{item['category']}\n\n该文档用于展示项目说明、阶段目标与交付范围。",
            author_id=users[item["owner"]].id,
            updated_by_id=users[item["owner"]].id,
            version_count=2,
            permission_status="团队可编辑",
            tags_json=dump_json([item["category"], "项目说明"]),
            related_task_id=tasks[0].id,
        )
        report_doc = _ensure_document(
            db,
            project.id,
            f"{item['name']} - 周报与复盘",
            content=f"# 周报与复盘\n\n本周围绕 {item['focus'][1]}、{item['focus'][2]} 持续推进，整体节奏稳定。",
            author_id=users[item["members"][1][0]].id,
            updated_by_id=users[item["members"][1][0]].id,
            version_count=1,
            permission_status="团队可编辑",
            tags_json=dump_json(["周报", "复盘"]),
            related_task_id=tasks[1].id,
        )
        _ensure_document_version(
            db,
            overview_doc.id,
            "v1.1",
            summary="补充项目范围与演示目标",
            content=overview_doc.content,
            author_id=users[item["owner"]].id,
            added_words=42,
            modified_words=15,
        )
        _ensure_document_version(
            db,
            overview_doc.id,
            "v1.0",
            summary="初始化项目说明文档",
            content=overview_doc.content,
            author_id=users[item["members"][1][0]].id,
            added_words=26,
            modified_words=8,
        )
        group = _ensure_conversation(
            db,
            project.id,
            name=f"{item['name']} 项目群",
            conversation_type="project_group",
            created_by=users[item["owner"]].id,
            is_pinned=True,
        )
        topic = _ensure_conversation(
            db,
            project.id,
            name=f"{item['focus'][1]} 专题讨论",
            conversation_type="task",
            created_by=users[item["owner"]].id,
            related_task_id=tasks[1].id,
            is_pinned=False,
        )
        for username, _role in item["members"]:
            _ensure_conversation_member(db, group.id, users[username].id)
            _ensure_conversation_member(db, topic.id, users[username].id)
        _ensure_message(db, project.id, group.id, users[item["owner"]].id, f"{item['name']} 本周重点推进 {item['focus'][1]} 与 {item['focus'][2]}。", "text")
        _ensure_message(db, project.id, group.id, users[item["members"][1][0]].id, f"我会先把 {item['focus'][2]} 的原型和接口依赖整理出来。", "text")
        _ensure_message(db, project.id, topic.id, users[item["members"][2][0]].id, f"关于 {item['focus'][1]}，建议先补齐测试数据和接口示例。", "text")
        _ensure_message(db, project.id, topic.id, users[item["owner"]].id, f"已同步到任务面板，相关说明见《{overview_doc.title}》。", "task")
        _ensure_file(
            db,
            project.id,
            f"{item['name']}-阶段演示稿.pptx",
            file_type="演示文稿",
            related_task=item["focus"][3],
            uploader_id=users[item["owner"]].id,
            version_label="v1.0",
            review_status="已通过" if item["status"] == "已结束" else "待评审",
            download_count=8,
            category="演示",
            storage_path=f"/演示材料/{item['repo_slug']}/stage-demo.pptx",
            size_label="3.8 MB",
            description="用于项目汇报与前端效果演示。",
            comments_json=dump_json([{"author": "张三", "time": "2024-05-18 20:10", "content": "已补充流程图与核心页面截图。"}]),
        )
        _ensure_file(
            db,
            project.id,
            f"{item['name']}-任务清单.xlsx",
            file_type="表格",
            related_task=item["focus"][0],
            uploader_id=users[item["members"][1][0]].id,
            version_label="v1.2",
            review_status="已通过",
            download_count=11,
            category="计划",
            storage_path=f"/计划清单/{item['repo_slug']}/tasks.xlsx",
            size_label="560 KB",
            description="展示任务拆解、负责人和时间安排。",
            comments_json=dump_json([{"author": "李四", "time": "2024-05-17 11:32", "content": "本周已补齐依赖项与风险标记。"}]),
        )
        _ensure_file(
            db,
            project.id,
            f"{item['name']}-接口草案.pdf",
            file_type="PDF",
            related_task=item["focus"][1],
            uploader_id=users[item["members"][2][0]].id,
            version_label="v0.9",
            review_status="待评审" if item["status"] != "已结束" else "已通过",
            download_count=6,
            category="接口",
            storage_path=f"/接口文档/{item['repo_slug']}/api.pdf",
            size_label="1.1 MB",
            description="用于演示文件中心与评审状态。",
            comments_json=dump_json([]),
        )
        _ensure_event(
            db,
            project.id,
            actor_id=users[item["owner"]].id,
            event_type="project",
            title=f"{item['name']} 更新了阶段计划",
            content=f"新增 {item['focus'][3]} 与 {item['focus'][4]} 的排期说明。",
            related_type="project",
            related_id=project.id,
            score_value=4.5,
        )
        _ensure_event(
            db,
            project.id,
            actor_id=users[item["members"][1][0]].id,
            event_type="document",
            title=f"{item['name']} 更新了周报",
            content=report_doc.title,
            related_type="document",
            related_id=report_doc.id,
            score_value=3.6,
        )
        _ensure_event(
            db,
            project.id,
            actor_id=users[item["members"][2][0]].id,
            event_type="task",
            title=f"{item['name']} 推进了任务协作",
            content=f"任务「{tasks[1].title}」状态已推进到 {tasks[1].progress}%。",
            related_type="task",
            related_id=tasks[1].id,
            score_value=4.0,
        )
        for index, (username, _role) in enumerate(item["members"][:4]):
            _ensure_score(
                db,
                project.id,
                users[username].id,
                total_score=max(58, 90 - index * 8),
                task_score=max(14, 24 - index * 2),
                document_score=max(9, 18 - index * 2),
                code_score=max(8, 20 - index * 3),
                response_score=max(10, 16 - index),
                stability_score=max(9, 15 - index),
                completed_tasks=max(1, 6 - index),
                collaboration_events=max(3, 14 - index * 2),
            )
            _ensure_evidence(
                db,
                project.id,
                users[username].id,
                evidence_type="任务完成" if index < 2 else "文档协作",
                summary=f"{item['name']} 中完成了「{item['focus'][index]}」的关键推进。",
                score=max(3.5, 8.2 - index),
                related_type="task",
                related_id=tasks[index].id,
            )
        if item["status"] != "已结束":
            _ensure_risk(
                db,
                project.id,
                title=f"{item['focus'][2]} 存在协作依赖风险",
                level="中",
                score=66,
                reason=f"{item['focus'][1]} 与 {item['focus'][2]} 的联动事项较多，当前仍有部分依赖待确认。",
                suggestion="建议安排一次短会统一接口、页面和数据口径。",
                risk_type="协作风险",
                due_at="05-20",
            )
            _ensure_risk(
                db,
                project.id,
                title=f"{item['focus'][4]} 材料准备偏慢",
                level="低",
                score=38,
                reason="演示材料与总结内容已开始整理，但信息还不够集中。",
                suggestion="由文档负责人统一汇总页面截图、数据图表和关键记录。",
                risk_type="文档风险",
                due_at="05-23",
            )
        else:
            _ensure_risk(
                db,
                project.id,
                title=f"{item['name']} 已归档",
                level="低",
                score=12,
                reason="项目已完成，当前仅保留过程资料用于查看。",
                suggestion="如需再次启用，可复制项目为新的协作空间。",
                risk_type="归档说明",
                due_at="04-02",
            )
        _ensure_repository(
            db,
            project.id,
            name=item["repo_slug"],
            url=f"github.com/teamflow/{item['repo_slug']}.git",
            default_branch="main",
            sync_status="success",
            webhook_status="configured",
            last_synced_at="2024-05-18 20:30",
            ci_status="通过" if item["status"] != "已结束" else "历史归档",
            total_commits=36 if item["status"] != "已结束" else 18,
        )
        _ensure_commit(
            db,
            project.id,
            users[item["owner"]].id,
            commit_hash=f"{item['repo_slug'][:7]}1",
            branch_name="main",
            message=f"feat: 完成 {item['focus'][0]} 初版",
            changed_files_json=dump_json(["src/views/overview.vue", "src/api/project.ts"]),
            added_lines=86,
            deleted_lines=12,
            risk_score=76,
            quality_score=88,
            related_task=f"#{tasks[0].id}",
        )
        _ensure_commit(
            db,
            project.id,
            users[item["members"][1][0]].id,
            commit_hash=f"{item['repo_slug'][:7]}2",
            branch_name="develop",
            message=f"chore: 跟进 {item['focus'][1]} 的数据联调",
            changed_files_json=dump_json(["src/views/detail.vue", "backend/service/demo.py"]),
            added_lines=54,
            deleted_lines=10,
            risk_score=68,
            quality_score=83,
            related_task=f"#{tasks[1].id}",
        )
        _ensure_commit(
            db,
            project.id,
            users[item["members"][2][0]].id,
            commit_hash=f"{item['repo_slug'][:7]}3",
            branch_name="feature/ui",
            message=f"style: 完善 {item['focus'][3]} 的展示效果",
            changed_files_json=dump_json(["src/components/board.vue", "src/styles/demo.css"]),
            added_lines=43,
            deleted_lines=6,
            risk_score=52,
            quality_score=85,
            related_task=f"#{tasks[3].id}",
        )
        _ensure_pull_request(
            db,
            project.id,
            title=f"{item['name']} 阶段迭代合并",
            branch_name="feature/demo-iteration",
            author_id=users[item["owner"]].id,
            status="待审核" if item["status"] != "已结束" else "已合并",
            reviewers_json=dump_json([item["members"][1][0], item["members"][2][0]]),
        )
        _ensure_notification(
            db,
            user_id=users["zhangsan"].id,
            project_id=project.id,
            type="system",
            title=f"{item['name']} 已同步最新动态",
            content="系统已为默认演示账号补齐项目任务、文档、消息和分析数据。",
            ref_type="project",
            ref_id=project.id,
            is_read=False,
        )
        _ensure_notification(
            db,
            user_id=users[item["owner"]].id,
            project_id=project.id,
            type="project",
            title=f"{item['name']} 生成了演示周报",
            content=f"请查看 {report_doc.title} 与风险概览，准备下次汇报材料。",
            ref_type="document",
            ref_id=report_doc.id,
            is_read=item["owner"] == "zhangsan",
        )
        _ensure_ai_report(
            db,
            project.id,
            report_type="weekly",
            content=f"{item['name']} 本周重点完成了 {item['focus'][0]} 与 {item['focus'][1]}，接下来将继续推进 {item['focus'][2]} 和 {item['focus'][3]}。",
        )


def _ensure_project_member(
    db: Session,
    project_id: int,
    user_id: int,
    *,
    role: str,
    permission_level: str,
    workload: int,
    online_status: str,
):
    row = db.query(ProjectMember).filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id).first()
    if not row:
        row = ProjectMember(project_id=project_id, user_id=user_id)
        db.add(row)
    row.role = role
    row.permission_level = permission_level
    row.workload = workload
    row.online_status = online_status
    db.flush()
    return row


def _ensure_milestone(db: Session, project_id: int, name: str, *, due_date: str, status: str, order_index: int):
    row = db.query(Milestone).filter(Milestone.project_id == project_id, Milestone.name == name).first()
    if not row:
        row = Milestone(project_id=project_id, name=name)
        db.add(row)
    row.due_date = due_date
    row.status = status
    row.order_index = order_index
    db.flush()
    return row


def _ensure_task(db: Session, project_id: int, title: str, **attrs):
    row = db.query(Task).filter(Task.project_id == project_id, Task.title == title).first()
    if not row:
        row = Task(project_id=project_id, title=title, created_by=attrs.get("created_by", 0))
        db.add(row)
    for key, value in attrs.items():
        setattr(row, key, value)
    db.flush()
    return row


def _ensure_document(db: Session, project_id: int, title: str, **attrs):
    row = db.query(Document).filter(Document.project_id == project_id, Document.title == title).first()
    if not row:
        row = Document(project_id=project_id, title=title, author_id=attrs.get("author_id", 0), updated_by_id=attrs.get("updated_by_id", 0))
        db.add(row)
    for key, value in attrs.items():
        setattr(row, key, value)
    db.flush()
    return row


def _ensure_document_version(db: Session, document_id: int, version_label: str, **attrs):
    row = db.query(DocumentVersion).filter(DocumentVersion.document_id == document_id, DocumentVersion.version_label == version_label).first()
    if not row:
        row = DocumentVersion(document_id=document_id, version_label=version_label, author_id=attrs.get("author_id", 0))
        db.add(row)
    for key, value in attrs.items():
        setattr(row, key, value)
    db.flush()
    return row


def _ensure_conversation(
    db: Session,
    project_id: int,
    *,
    name: str,
    conversation_type: str,
    created_by: int,
    related_task_id: int | None = None,
    is_pinned: bool = False,
):
    row = db.query(Conversation).filter(Conversation.project_id == project_id, Conversation.name == name).first()
    if not row:
        row = Conversation(project_id=project_id, name=name, created_by=created_by)
        db.add(row)
    row.conversation_type = conversation_type
    row.related_task_id = related_task_id
    row.is_pinned = is_pinned
    db.flush()
    return row


def _ensure_conversation_member(db: Session, conversation_id: int, user_id: int):
    row = db.query(ConversationMember).filter(ConversationMember.conversation_id == conversation_id, ConversationMember.user_id == user_id).first()
    if not row:
        db.add(ConversationMember(conversation_id=conversation_id, user_id=user_id))
        db.flush()


def _ensure_message(
    db: Session,
    project_id: int,
    conversation_id: int,
    sender_id: int,
    content: str,
    message_type: str,
    code_language: str = "",
):
    row = (
        db.query(Message)
        .filter(
            Message.project_id == project_id,
            Message.conversation_id == conversation_id,
            Message.sender_id == sender_id,
            Message.content == content,
        )
        .first()
    )
    if not row:
        row = Message(project_id=project_id, conversation_id=conversation_id, sender_id=sender_id, content=content)
        db.add(row)
    row.message_type = message_type
    row.code_language = code_language
    db.flush()
    return row


def _ensure_file(db: Session, project_id: int, name: str, **attrs):
    row = db.query(FileResource).filter(FileResource.project_id == project_id, FileResource.name == name).first()
    if not row:
        row = FileResource(project_id=project_id, name=name, uploader_id=attrs.get("uploader_id", 0))
        db.add(row)
    for key, value in attrs.items():
        setattr(row, key, value)
    db.flush()
    return row


def _ensure_event(db: Session, project_id: int, title: str, **attrs):
    row = db.query(CollaborationEvent).filter(CollaborationEvent.project_id == project_id, CollaborationEvent.title == title).first()
    if not row:
        row = CollaborationEvent(project_id=project_id, title=title, actor_id=attrs.get("actor_id", 0))
        db.add(row)
    for key, value in attrs.items():
        setattr(row, key, value)
    db.flush()
    return row


def _ensure_score(db: Session, project_id: int, user_id: int, **attrs):
    row = db.query(ContributionScore).filter(ContributionScore.project_id == project_id, ContributionScore.user_id == user_id).first()
    if not row:
        row = ContributionScore(project_id=project_id, user_id=user_id)
        db.add(row)
    for key, value in attrs.items():
        setattr(row, key, value)
    db.flush()
    return row


def _ensure_evidence(db: Session, project_id: int, user_id: int, summary: str, **attrs):
    row = db.query(ContributionEvidence).filter(ContributionEvidence.project_id == project_id, ContributionEvidence.user_id == user_id, ContributionEvidence.summary == summary).first()
    if not row:
        row = ContributionEvidence(project_id=project_id, user_id=user_id, summary=summary)
        db.add(row)
    for key, value in attrs.items():
        setattr(row, key, value)
    db.flush()
    return row


def _ensure_risk(db: Session, project_id: int, title: str, **attrs):
    row = db.query(RiskAlert).filter(RiskAlert.project_id == project_id, RiskAlert.title == title).first()
    if not row:
        row = RiskAlert(project_id=project_id, title=title)
        db.add(row)
    for key, value in attrs.items():
        setattr(row, key, value)
    db.flush()
    return row


def _ensure_repository(db: Session, project_id: int, name: str, **attrs):
    row = db.query(GitRepository).filter(GitRepository.project_id == project_id, GitRepository.name == name).first()
    if not row:
        row = GitRepository(project_id=project_id, name=name)
        db.add(row)
    for key, value in attrs.items():
        setattr(row, key, value)
    db.flush()
    return row


def _ensure_commit(db: Session, project_id: int, user_id: int, commit_hash: str, **attrs):
    row = db.query(GitCommit).filter(GitCommit.project_id == project_id, GitCommit.commit_hash == commit_hash).first()
    if not row:
        row = GitCommit(project_id=project_id, user_id=user_id, commit_hash=commit_hash, message=attrs.get("message", ""))
        db.add(row)
    row.user_id = user_id
    for key, value in attrs.items():
        setattr(row, key, value)
    db.flush()
    return row


def _ensure_pull_request(db: Session, project_id: int, title: str, **attrs):
    row = db.query(PullRequest).filter(PullRequest.project_id == project_id, PullRequest.title == title).first()
    if not row:
        row = PullRequest(project_id=project_id, title=title, author_id=attrs.get("author_id", 0))
        db.add(row)
    for key, value in attrs.items():
        setattr(row, key, value)
    db.flush()
    return row


def _ensure_notification(db: Session, *, user_id: int, project_id: int | None, title: str, **attrs):
    row = db.query(Notification).filter(Notification.user_id == user_id, Notification.project_id == project_id, Notification.title == title).first()
    if not row:
        row = Notification(user_id=user_id, project_id=project_id, title=title)
        db.add(row)
    for key, value in attrs.items():
        setattr(row, key, value)
    db.flush()
    return row


def _ensure_ai_report(db: Session, project_id: int, report_type: str, content: str):
    row = db.query(AIReportHistory).filter(AIReportHistory.project_id == project_id, AIReportHistory.report_type == report_type).first()
    if not row:
        row = AIReportHistory(project_id=project_id, report_type=report_type, content=content)
        db.add(row)
    else:
        row.content = content
    db.flush()
    return row


def _task_response_status(status: str, progress: int) -> str:
    if status == "DONE":
        return "已完成"
    if status == "IN_PROGRESS":
        return "处理中"
    if status == "REVIEW":
        return "待验收"
    if status == "BLOCKED":
        return "阻塞中"
    return "待接收" if progress == 0 else "未分配"


def _seed_pending_invites_for_default_user(db: Session) -> None:
    users = {user.username: user for user in db.query(User).all()}
    invite_specs = [
        ("图书管理系统", "lisi", "zhangsan", "后端开发", "邀请你加入图书管理系统项目。"),
        ("校园二手交易平台", "wangwu", "zhangsan", "前端开发", "邀请你加入校园二手交易平台项目。"),
        ("大数据分析可视化系统", "zhaoliu", "zhangsan", "数据分析师", "邀请你加入大数据分析可视化系统项目。"),
    ]
    for project_name, inviter, invitee, role, message in invite_specs:
        project = db.query(Project).filter(Project.name == project_name).first()
        if not project:
            project = Project(
                name=project_name,
                course_name="跨项目协作演示",
                description=f"{project_name} 的邀请演示数据。",
                status="进行中",
                category="课程设计",
                start_date="2024-05-01",
                due_date="2024-06-20",
                repo_url=f"github.com/teamflow/{project_name}",
                advisor_name="王老师",
                advisor_email="wanglaoshi@university.edu.cn",
                tags_json=dump_json(["邀请演示"]),
                owner_id=users[inviter].id,
            )
            db.add(project)
            db.flush()
            db.add(
                ProjectMember(
                    project_id=project.id,
                    user_id=users[inviter].id,
                    role="组长",
                    permission_level="全部权限",
                    workload=76,
                    online_status="在线",
                )
            )
        exists = (
            db.query(ProjectInvitation)
            .filter(
                ProjectInvitation.project_id == project.id,
                ProjectInvitation.inviter_id == users[inviter].id,
                ProjectInvitation.invitee_id == users[invitee].id,
                ProjectInvitation.status == "pending",
            )
            .first()
        )
        if exists:
            continue
        db.add(
            ProjectInvitation(
                project_id=project.id,
                inviter_id=users[inviter].id,
                invitee_id=users[invitee].id,
                role=role,
                message=message,
                status="pending",
            )
        )
        db.add(
            Notification(
                user_id=users[invitee].id,
                project_id=project.id,
                type="project_invite",
                title=f"{project_name} 邀请你加入项目",
                content=message,
                ref_type="project",
                ref_id=project.id,
                is_read=False,
            )
        )
