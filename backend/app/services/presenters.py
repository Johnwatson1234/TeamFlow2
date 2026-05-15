from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.entities import (
    CollaborationEvent,
    Conversation,
    ContributionEvidence,
    ContributionScore,
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
from app.utils.serializers import parse_json


def fmt_dt(value):
    if not value:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value)


def user_brief(user: User):
    return {
        "id": user.id,
        "name": user.display_name,
        "email": user.email,
        "avatar": user.avatar,
        "title": user.title,
        "role": user.system_role,
    }


def build_user_map(db: Session):
    return {user.id: user for user in db.query(User).all()}


def serialize_project(project: Project, db: Session, current_user_id: int):
    users = build_user_map(db)
    members = db.query(ProjectMember).filter(ProjectMember.project_id == project.id).all()
    tasks = db.query(Task).filter(Task.project_id == project.id, Task.archived == False).all()  # noqa: E712
    documents = db.query(Document).filter(Document.project_id == project.id, Document.is_deleted == False).all()  # noqa: E712
    invitations = db.query(ProjectInvitation).filter(ProjectInvitation.project_id == project.id).all()
    done_count = len([task for task in tasks if task.status == "DONE"])
    progress = round(done_count / len(tasks) * 100) if tasks else 0
    member_entry = next((item for item in members if item.user_id == current_user_id), None)
    updated_by = users.get(project.owner_id)
    return {
        "id": project.id,
        "name": project.name,
        "course_name": project.course_name,
        "description": project.description,
        "status": project.status,
        "category": project.category,
        "start_date": project.start_date,
        "due_date": project.due_date,
        "repo_url": project.repo_url,
        "advisor_name": project.advisor_name,
        "advisor_email": project.advisor_email,
        "tags": parse_json(project.tags_json, []),
        "member_count": len(members),
        "document_count": len(documents),
        "pending_invitation_count": len([inv for inv in invitations if inv.status == "pending"]),
        "progress": progress,
        "members": [user_brief(users[item.user_id]) for item in members[:5] if item.user_id in users],
        "my_role": member_entry.role if member_entry else "",
        "owner_id": project.owner_id,
        "owner_name": updated_by.display_name if updated_by else "",
        "is_owner": project.owner_id == current_user_id,
        "is_archived": project.status == "已结束",
        "updated_at": fmt_dt(project.updated_at),
        "updated_by": updated_by.display_name if updated_by else "",
    }


def serialize_member(member: ProjectMember, users: dict[int, User]):
    user = users[member.user_id]
    return {
        "id": member.id,
        "user_id": user.id,
        "name": user.display_name,
        "email": user.email,
        "avatar": user.avatar,
        "role": member.role,
        "title": user.title,
        "permission_level": member.permission_level,
        "workload": member.workload,
        "online_status": member.online_status,
        "joined_at": fmt_dt(member.joined_at),
    }


def serialize_invitation(invitation: ProjectInvitation, users: dict[int, User], projects: dict[int, Project]):
    inviter = users.get(invitation.inviter_id)
    invitee = users.get(invitation.invitee_id)
    project = projects.get(invitation.project_id)
    return {
        "id": invitation.id,
        "project_id": invitation.project_id,
        "project_name": project.name if project else "",
        "inviter": user_brief(inviter) if inviter else None,
        "invitee": user_brief(invitee) if invitee else None,
        "role": invitation.role,
        "message": invitation.message,
        "status": invitation.status,
        "created_at": fmt_dt(invitation.created_at),
        "responded_at": fmt_dt(invitation.responded_at),
    }


def serialize_task(task: Task, users: dict[int, User]):
    assignee = users.get(task.assignee_id) if task.assignee_id else None
    return {
        "id": task.id,
        "project_id": task.project_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "response_status": task.response_status,
        "priority": task.priority,
        "progress": task.progress,
        "assignee": user_brief(assignee) if assignee else None,
        "due_date": task.due_date,
        "start_date": task.start_date,
        "blocker_reason": task.blocker_reason,
        "related_requirement": task.related_requirement,
        "related_document": task.related_document,
        "related_commit": task.related_commit,
        "milestone_id": task.milestone_id,
        "created_by": task.created_by,
        "created_at": fmt_dt(task.created_at),
        "updated_at": fmt_dt(task.updated_at),
    }


def serialize_task_activity(activity: TaskActivity, users: dict[int, User]):
    actor = users.get(activity.actor_id)
    return {
        "id": activity.id,
        "task_id": activity.task_id,
        "activity_type": activity.activity_type,
        "content": activity.content,
        "from_value": activity.from_value,
        "to_value": activity.to_value,
        "created_at": fmt_dt(activity.created_at),
        "actor": user_brief(actor) if actor else None,
    }


def serialize_conversation(conversation: Conversation, db: Session, current_user_id: int):
    users = build_user_map(db)
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc())
        .limit(1)
        .all()
    )
    latest = messages[0] if messages else None
    unread = db.query(Message).filter(Message.conversation_id == conversation.id).count()
    return {
        "id": conversation.id,
        "project_id": conversation.project_id,
        "name": conversation.name,
        "conversation_type": conversation.conversation_type,
        "related_task_id": conversation.related_task_id,
        "is_pinned": conversation.is_pinned,
        "latest_message": serialize_message(latest, users) if latest else None,
        "unread_count": 0 if conversation.conversation_type == "system" and current_user_id != 1 else min(unread, 12),
    }


def serialize_message(message: Message | None, users: dict[int, User]):
    if not message:
        return None
    sender = users.get(message.sender_id)
    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "project_id": message.project_id,
        "sender": user_brief(sender) if sender else None,
        "message_type": message.message_type,
        "content": message.content,
        "code_language": message.code_language,
        "metadata": parse_json(message.metadata_json, {}),
        "status": message.status,
        "created_at": fmt_dt(message.created_at),
    }


def serialize_document(document: Document, users: dict[int, User]):
    author = users.get(document.author_id)
    updated_by = users.get(document.updated_by_id)
    return {
        "id": document.id,
        "project_id": document.project_id,
        "title": document.title,
        "content": document.content,
        "author": user_brief(author) if author else None,
        "updated_by": user_brief(updated_by) if updated_by else None,
        "version_count": document.version_count,
        "permission_status": document.permission_status,
        "tags": parse_json(document.tags_json, []),
        "related_task_id": document.related_task_id,
        "created_at": fmt_dt(document.created_at),
        "updated_at": fmt_dt(document.updated_at),
    }


def serialize_document_version(version: DocumentVersion, users: dict[int, User]):
    author = users.get(version.author_id)
    return {
        "id": version.id,
        "version_label": version.version_label,
        "summary": version.summary,
        "content": version.content,
        "added_words": version.added_words,
        "modified_words": version.modified_words,
        "created_at": fmt_dt(version.created_at),
        "author": user_brief(author) if author else None,
    }


def serialize_file(file_row: FileResource, users: dict[int, User]):
    uploader = users.get(file_row.uploader_id)
    return {
        "id": file_row.id,
        "project_id": file_row.project_id,
        "name": file_row.name,
        "file_type": file_row.file_type,
        "related_task": file_row.related_task,
        "uploader": user_brief(uploader) if uploader else None,
        "version_label": file_row.version_label,
        "review_status": file_row.review_status,
        "download_count": file_row.download_count,
        "category": file_row.category,
        "storage_path": file_row.storage_path,
        "size_label": file_row.size_label,
        "description": file_row.description,
        "comments": parse_json(file_row.comments_json, []),
        "created_at": fmt_dt(file_row.created_at),
        "updated_at": fmt_dt(file_row.updated_at),
    }


def serialize_notification(notification: Notification, users: dict[int, User], projects: dict[int, Project]):
    project = projects.get(notification.project_id) if notification.project_id else None
    return {
        "id": notification.id,
        "title": notification.title,
        "content": notification.content,
        "type": notification.type,
        "project_id": notification.project_id,
        "project_name": project.name if project else "",
        "ref_type": notification.ref_type,
        "ref_id": notification.ref_id,
        "is_read": notification.is_read,
        "created_at": fmt_dt(notification.created_at),
        "read_at": fmt_dt(notification.read_at),
        "icon": notification.type,
    }


def serialize_event(event: CollaborationEvent, users: dict[int, User]):
    actor = users.get(event.actor_id)
    return {
        "id": event.id,
        "event_type": event.event_type,
        "title": event.title,
        "content": event.content,
        "related_type": event.related_type,
        "related_id": event.related_id,
        "score_value": event.score_value,
        "created_at": fmt_dt(event.created_at),
        "actor": user_brief(actor) if actor else None,
    }


def serialize_contribution(score: ContributionScore, users: dict[int, User]):
    user = users.get(score.user_id)
    return {
        "id": score.id,
        "user": user_brief(user) if user else None,
        "total_score": score.total_score,
        "task_score": score.task_score,
        "document_score": score.document_score,
        "code_score": score.code_score,
        "response_score": score.response_score,
        "stability_score": score.stability_score,
        "completed_tasks": score.completed_tasks,
        "collaboration_events": score.collaboration_events,
        "updated_at": fmt_dt(score.updated_at),
    }


def serialize_evidence(evidence: ContributionEvidence, users: dict[int, User]):
    user = users.get(evidence.user_id)
    return {
        "id": evidence.id,
        "user": user_brief(user) if user else None,
        "evidence_type": evidence.evidence_type,
        "summary": evidence.summary,
        "score": evidence.score,
        "related_type": evidence.related_type,
        "related_id": evidence.related_id,
        "created_at": fmt_dt(evidence.created_at),
    }


def serialize_risk(risk: RiskAlert):
    return {
        "id": risk.id,
        "title": risk.title,
        "level": risk.level,
        "score": risk.score,
        "reason": risk.reason,
        "suggestion": risk.suggestion,
        "status": risk.status,
        "risk_type": risk.risk_type,
        "due_at": risk.due_at,
        "created_at": fmt_dt(risk.created_at),
    }


def serialize_commit(commit: GitCommit, users: dict[int, User]):
    user = users.get(commit.user_id)
    return {
        "id": commit.id,
        "author": user_brief(user) if user else None,
        "commit_hash": commit.commit_hash,
        "branch_name": commit.branch_name,
        "message": commit.message,
        "changed_files": parse_json(commit.changed_files_json, []),
        "added_lines": commit.added_lines,
        "deleted_lines": commit.deleted_lines,
        "risk_score": commit.risk_score,
        "quality_score": commit.quality_score,
        "related_task": commit.related_task,
        "created_at": fmt_dt(commit.created_at),
    }


def serialize_pull_request(pr: PullRequest, users: dict[int, User]):
    author = users.get(pr.author_id)
    reviewers = [user_brief(users[item]) for item in users if users[item].username in parse_json(pr.reviewers_json, [])]
    return {
        "id": pr.id,
        "title": pr.title,
        "branch_name": pr.branch_name,
        "author": user_brief(author) if author else None,
        "status": pr.status,
        "reviewers": reviewers,
        "updated_at": fmt_dt(pr.updated_at),
    }


def serialize_repository(repo: GitRepository):
    return {
        "id": repo.id,
        "name": repo.name,
        "url": repo.url,
        "default_branch": repo.default_branch,
        "sync_status": repo.sync_status,
        "webhook_status": repo.webhook_status,
        "last_synced_at": repo.last_synced_at,
        "ci_status": repo.ci_status,
        "total_commits": repo.total_commits,
    }


def build_dashboard_payload(project_id: int, db: Session):
    users = build_user_map(db)
    tasks = db.query(Task).filter(Task.project_id == project_id, Task.archived == False).all()  # noqa: E712
    documents = db.query(Document).filter(Document.project_id == project_id, Document.is_deleted == False).all()  # noqa: E712
    events = (
        db.query(CollaborationEvent)
        .filter(CollaborationEvent.project_id == project_id)
        .order_by(CollaborationEvent.created_at.desc())
        .all()
    )
    risks = db.query(RiskAlert).filter(RiskAlert.project_id == project_id).all()
    scores = (
        db.query(ContributionScore)
        .filter(ContributionScore.project_id == project_id)
        .order_by(ContributionScore.total_score.desc())
        .all()
    )
    invitations = db.query(ProjectInvitation).filter(ProjectInvitation.project_id == project_id, ProjectInvitation.status == "pending").all()
    done_count = len([task for task in tasks if task.status == "DONE"])
    activity_series = [
        {"date": "04-19", "value": 28},
        {"date": "04-22", "value": 45},
        {"date": "04-24", "value": 54},
        {"date": "04-26", "value": 46},
        {"date": "04-28", "value": 48},
        {"date": "04-30", "value": 53},
        {"date": "05-02", "value": 36},
        {"date": "05-04", "value": 47},
        {"date": "05-06", "value": 45},
        {"date": "05-08", "value": 56},
        {"date": "05-10", "value": 52},
        {"date": "05-12", "value": 68},
        {"date": "05-14", "value": 41},
        {"date": "05-16", "value": 55},
        {"date": "05-18", "value": 39},
    ]
    return {
        "stats": {
            "completion_rate": round(done_count / len(tasks) * 100) if tasks else 0,
            "completed_count": done_count,
            "task_total": len(tasks),
            "in_progress_count": len([task for task in tasks if task.status == "IN_PROGRESS"]),
            "delayed_count": len([task for task in tasks if task.status in {"BLOCKED", "REVIEW"}]),
            "member_count": db.query(ProjectMember).filter(ProjectMember.project_id == project_id).count(),
            "document_count": len(documents),
            "event_count": len(events),
            "pending_invitation_count": len(invitations),
            "todo_count": len([task for task in tasks if task.status != "DONE"]),
            "unread_count": db.query(Notification).filter(Notification.project_id == project_id, Notification.is_read == False).count(),  # noqa: E712
        },
        "activity_series": activity_series,
        "recent_events": [serialize_event(event, users) for event in events[:5]],
        "risk_alerts": [serialize_risk(item) for item in risks[:3]],
        "contribution_rank": [serialize_contribution(item, users) for item in scores[:5]],
        "health_radar": [
            {"name": "任务进度", "value": 80},
            {"name": "协作活跃度", "value": 75},
            {"name": "文档完整度", "value": 70},
            {"name": "代码健康度", "value": 85},
            {"name": "风险控制", "value": 65},
            {"name": "成员贡献度", "value": 78},
        ],
        "process_audit": [
            {"name": "任务变更", "count": 28},
            {"name": "文档版本变更", "count": 16},
            {"name": "代码提交", "count": 124},
            {"name": "成员加入/退出", "count": 2},
            {"name": "风险处理记录", "count": 3},
        ],
        "recent_task_activities": [
            serialize_task_activity(activity, users)
            for activity in db.query(TaskActivity).filter(TaskActivity.project_id == project_id).order_by(TaskActivity.created_at.desc()).limit(5).all()
        ],
    }


def build_graph_payload(project_id: int, db: Session):
    users = build_user_map(db)
    tasks = db.query(Task).filter(Task.project_id == project_id).limit(6).all()
    documents = db.query(Document).filter(Document.project_id == project_id).limit(5).all()
    commits = db.query(GitCommit).filter(GitCommit.project_id == project_id).limit(4).all()
    nodes = []
    edges = []
    for user in db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all():
        item = users[user.user_id]
        nodes.append({"id": f"user-{item.id}", "label": item.display_name, "type": "member", "avatar": item.avatar})
    for task in tasks:
        nodes.append({"id": f"task-{task.id}", "label": task.title, "type": "task"})
        if task.assignee_id:
            edges.append({"source": f"user-{task.assignee_id}", "target": f"task-{task.id}", "label": "负责"})
    for document in documents:
        nodes.append({"id": f"doc-{document.id}", "label": document.title, "type": "document"})
        edges.append({"source": f"user-{document.author_id}", "target": f"doc-{document.id}", "label": "编写"})
    for commit in commits:
        nodes.append({"id": f"commit-{commit.id}", "label": commit.commit_hash[:7], "type": "commit"})
        edges.append({"source": f"user-{commit.user_id}", "target": f"commit-{commit.id}", "label": "提交"})
    summary = {
        "code_commit": {"count": 128, "ratio": 36},
        "document": {"count": 24, "ratio": 22},
        "task": {"count": 26, "ratio": 20},
        "review": {"count": 18, "ratio": 12},
        "message": {"count": 156, "ratio": 10},
    }
    detail_commit = db.query(GitCommit).filter(GitCommit.project_id == project_id).first()
    return {
        "nodes": nodes,
        "edges": edges,
        "legend": [
            {"type": "task", "label": "任务"},
            {"type": "document", "label": "文档"},
            {"type": "message", "label": "消息"},
            {"type": "commit", "label": "代码提交"},
            {"type": "review", "label": "评审"},
            {"type": "member", "label": "成员"},
        ],
        "member_ranking": [serialize_contribution(item, users) for item in db.query(ContributionScore).filter(ContributionScore.project_id == project_id).order_by(ContributionScore.total_score.desc()).limit(6).all()],
        "evidence_summary": summary,
        "event_detail": {
            "event_type": "代码提交 (Commit)",
            "event_id": detail_commit.commit_hash if detail_commit else "",
            "author": users[detail_commit.user_id].display_name if detail_commit else "",
            "time": fmt_dt(detail_commit.created_at) if detail_commit else "",
            "related_task": detail_commit.related_task if detail_commit else "",
            "description": detail_commit.message if detail_commit else "",
            "impact_files": len(parse_json(detail_commit.changed_files_json, [])) if detail_commit else 0,
            "contribution_score": 8.5,
        },
        "timeline": [
            {"date": "04-19", "type": "task"},
            {"date": "04-24", "type": "document"},
            {"date": "04-29", "type": "message"},
            {"date": "05-04", "type": "commit"},
            {"date": "05-09", "type": "review"},
            {"date": "05-14", "type": "task"},
            {"date": "05-18", "type": "document"},
        ],
    }


def build_git_payload(project_id: int, db: Session):
    users = build_user_map(db)
    commits = db.query(GitCommit).filter(GitCommit.project_id == project_id).order_by(GitCommit.created_at.desc()).all()
    prs = db.query(PullRequest).filter(PullRequest.project_id == project_id).all()
    repo = db.query(GitRepository).filter(GitRepository.project_id == project_id).first()
    hotspots = [
        {"path": "src/views/TaskList.vue", "changes": 24, "lines": "+512 / -203", "participants": 4, "heat": 95},
        {"path": "src/api/task.ts", "changes": 18, "lines": "+342 / -121", "participants": 3, "heat": 78},
        {"path": "src/store/task.ts", "changes": 15, "lines": "+287 / -98", "participants": 3, "heat": 65},
        {"path": "src/components/Chart.vue", "changes": 12, "lines": "+213 / -76", "participants": 2, "heat": 52},
        {"path": "src/utils/permission.ts", "changes": 10, "lines": "+156 / -42", "participants": 2, "heat": 38},
    ]
    conflict_files = [
        {"path": "src/views/TaskList.vue", "members": ["张三", "李四", "王五"], "level": "高", "suggestion": "立即协调", "eta": "2h"},
        {"path": "src/api/task.ts", "members": ["张三", "李四", "赵六"], "level": "高", "suggestion": "先合并 develop", "eta": "4h"},
        {"path": "src/store/user.ts", "members": ["王五", "赵六"], "level": "中", "suggestion": "沟通后合并", "eta": "6h"},
        {"path": "src/components/Header.vue", "members": ["张三", "王五"], "level": "中", "suggestion": "拆分修改点", "eta": "8h"},
        {"path": "src/utils/permission.ts", "members": ["李四", "王五", "赵六"], "level": "低", "suggestion": "按分支顺序", "eta": "12h"},
    ]
    return {
        "overview": {
            "today_commits": 18,
            "active_branches": 7,
            "conflict_files": 12,
            "pending_prs": len([item for item in prs if item.status == "待审核"]),
        },
        "recent_commits": [serialize_commit(item, users) for item in commits],
        "branch_graph": [
            {"branch": "main", "time": "16:42", "author": "张三", "commit": "a1b2c3d"},
            {"branch": "develop", "time": "15:21", "author": "王五", "commit": "b2c3d4e"},
            {"branch": "feature/auth", "time": "14:03", "author": "赵六", "commit": "c3d4e5f"},
            {"branch": "feature/doc", "time": "11:57", "author": "孙七", "commit": "d4e5f6g"},
            {"branch": "feature/db", "time": "09:33", "author": "周八", "commit": "e5f6g7h"},
        ],
        "conflict_files": conflict_files,
        "hotspots": hotspots,
        "pull_requests": [serialize_pull_request(item, users) for item in prs],
        "repository": serialize_repository(repo) if repo else None,
    }


def build_reminder_payload(project_id: int, user_id: int, db: Session):
    users = build_user_map(db)
    projects = {item.id: item for item in db.query(Project).all()}
    invitations = db.query(ProjectInvitation).filter(ProjectInvitation.invitee_id == user_id, ProjectInvitation.status == "pending").all()
    notifications = db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()
    tasks = db.query(Task).filter(Task.project_id == project_id, Task.assignee_id == user_id).all()
    return {
        "stats": {
            "pending_invitations": len(invitations),
            "unread_notifications": len([item for item in notifications if not item.is_read]),
            "my_todos": len([item for item in tasks if item.status != "DONE"]),
            "upcoming_tasks": len([item for item in tasks if item.status in {"IN_PROGRESS", "REVIEW"}]),
        },
        "invitations": [serialize_invitation(item, users, projects) for item in invitations],
        "todo_tasks": [serialize_task(item, users) for item in tasks],
        "latest_notifications": [serialize_notification(item, users, projects) for item in notifications[:8]],
        "today_timeline": [
            {"time": "09:15", "title": "李四 完成了任务", "content": "数据库索引优化"},
            {"time": "10:02", "title": "王五 评论了文档", "content": "系统设计说明书 v1.1 第 2 页"},
            {"time": "10:45", "title": "赵六 提交了代码", "content": "feat: 添加用户登录接口"},
            {"time": "13:20", "title": "孙七 上传了文件", "content": "接口文档 v1.3.pdf"},
            {"time": "14:10", "title": "系统 触发风险提醒", "content": "用户模块接口开发延期风险"},
            {"time": "15:30", "title": "周八 邀请你加入", "content": "校园二手交易平台"},
        ],
    }
