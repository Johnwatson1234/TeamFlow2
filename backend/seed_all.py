import sys
import os
import random
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.entities import (
    User, Project, ProjectMember, Milestone, Task, TaskActivity,
    GitRepository, GitCommit, PullRequest,
    Conversation, ConversationMember, Message,
    Document, FileResource, CollaborationEvent, ContributionScore, RiskAlert
)

db = SessionLocal()

def seed_data():
    users = db.query(User).all()
    projects = db.query(Project).all()
    
    if not users or not projects:
        print("No users or projects found. Run standard seed first.")
        return

    print(f"Found {len(users)} users and {len(projects)} projects. Starting to generate rich mock data...")

    # Data lists for random selection
    task_titles = [
        "完成系统架构设计与技术选型",
        "开发用户登录注册模块",
        "集成基于 JWT 的权限验证",
        "设计并实现数据库表结构",
        "构建前端全局状态管理(Vuex/Pinia)",
        "实现主控制台页面布局",
        "完成项目管理模块 CRUD 接口",
        "集成实时 WebSocket 消息推送",
        "优化前端长列表渲染性能",
        "编写后端单元测试覆盖核心逻辑",
        "撰写用户使用手册文档",
        "修复文件上传模块的进度条 BUG",
        "对接智谱大模型 API 完成自动摘要",
        "部署生产环境并配置 CI/CD 流水线"
    ]
    
    commit_msgs = [
        "feat: add user authentication",
        "fix: resolve null pointer exception in task service",
        "docs: update README with setup instructions",
        "refactor: extract common layout components",
        "perf: optimize database queries for dashboard",
        "test: add unit tests for project creation",
        "style: format code with black and isort",
        "chore: update dependencies",
        "feat: implement real-time chat via websockets",
        "fix: correct the calculation of contribution scores"
    ]
    
    doc_titles = [
        "项目需求规格说明书 v1.0",
        "系统架构设计文档",
        "数据库表结构字典",
        "API 接口交互定义",
        "前端组件库使用规范",
        "第三周开发周报汇总",
        "测试用例与验收标准"
    ]
    
    file_names = [
        "ui_design_v2.sketch",
        "api_docs.pdf",
        "deployment_script.sh",
        "meeting_notes_0612.docx",
        "logo_assets.zip"
    ]

    for project in projects:
        members = db.query(ProjectMember).filter(ProjectMember.project_id == project.id).all()
        if not members:
            continue
        member_users = [m.user_id for m in members]
        
        # 1. Generate Milestones
        existing_milestones = db.query(Milestone).filter(Milestone.project_id == project.id).all()
        if len(existing_milestones) < 6:
            ms_names = ["需求分析与原型", "架构设计与技术选型", "核心模块开发", "非核心模块与集成", "系统测试与修复", "部署上线与验收"]
            for i, name in enumerate(ms_names):
                ms = Milestone(
                    project_id=project.id,
                    name=name,
                    due_date=(datetime.now() + timedelta(days=(i+1)*10)).strftime("%Y-%m-%d"),
                    status="已完成" if i < 2 else "进行中" if i == 2 else "待开始",
                    order_index=i
                )
                db.add(ms)
            db.commit()
        
        milestones = db.query(Milestone).filter(Milestone.project_id == project.id).all()

        # 2. Generate Tasks
        existing_tasks = db.query(Task).filter(Task.project_id == project.id).all()
        if len(existing_tasks) < 15:
            for _ in range(10):
                ms = random.choice(milestones) if milestones else None
                assignee_id = random.choice(member_users)
                status = random.choice(["TODO", "IN_PROGRESS", "DONE"])
                progress = 100 if status == "DONE" else random.randint(10, 80) if status == "IN_PROGRESS" else 0
                t = Task(
                    project_id=project.id,
                    milestone_id=ms.id if ms else None,
                    title=random.choice(task_titles) + f" #{random.randint(100, 999)}",
                    description="请按照项目规范完成该任务，并及时提交代码进行 Code Review。",
                    status=status,
                    priority=random.choice(["低", "中", "高"]),
                    progress=progress,
                    assignee_id=assignee_id,
                    created_by=random.choice(member_users),
                    due_date=(datetime.now() + timedelta(days=random.randint(-5, 15))).strftime("%Y-%m-%d")
                )
                db.add(t)
            db.commit()
            
        tasks = db.query(Task).filter(Task.project_id == project.id).all()
        
        # 3. Generate Task Activities
        for t in tasks:
            acts = db.query(TaskActivity).filter(TaskActivity.task_id == t.id).all()
            if len(acts) < 2:
                for _ in range(random.randint(1, 3)):
                    db.add(TaskActivity(
                        task_id=t.id,
                        project_id=project.id,
                        actor_id=random.choice(member_users),
                        activity_type=random.choice(["status_change", "commented", "progress_update"]),
                        content=random.choice(["将任务状态更新为进行中", "提交了初步的代码，等待 Review", "遇到一些依赖问题，正在解决", "已完成并关联了相关 PR"]),
                    ))
        db.commit()

        # 4. Generate Git Data
        repo = db.query(GitRepository).filter(GitRepository.project_id == project.id).first()
        if not repo:
            repo = GitRepository(project_id=project.id, name=f"{project.name}-repo", url=f"https://github.com/team/{project.name}.git", total_commits=120)
            db.add(repo)
            db.commit()
            
        existing_commits = db.query(GitCommit).filter(GitCommit.project_id == project.id).all()
        if len(existing_commits) < 20:
            for _ in range(15):
                db.add(GitCommit(
                    project_id=project.id,
                    user_id=random.choice(member_users),
                    commit_hash=f"{random.randint(1000000, 9999999)}abcdef",
                    branch_name=random.choice(["main", "dev", "feature/login", "bugfix/ui"]),
                    message=random.choice(commit_msgs),
                    added_lines=random.randint(10, 300),
                    deleted_lines=random.randint(0, 100),
                    risk_score=random.uniform(0.1, 5.0),
                    quality_score=random.uniform(70.0, 99.0)
                ))
            db.commit()

        # 5. Generate Documents & Files
        existing_docs = db.query(Document).filter(Document.project_id == project.id).all()
        if len(existing_docs) < 5:
            for title in doc_titles:
                db.add(Document(
                    project_id=project.id,
                    title=title,
                    content="本文档记录了项目的核心架构设计思路以及技术栈选择...",
                    author_id=random.choice(member_users),
                    updated_by_id=random.choice(member_users)
                ))
            db.commit()
            
        existing_files = db.query(FileResource).filter(FileResource.project_id == project.id).all()
        if len(existing_files) < 5:
            for fn in file_names:
                db.add(FileResource(
                    project_id=project.id,
                    name=fn,
                    uploader_id=random.choice(member_users),
                    category="开发资料",
                    size_label=f"{random.randint(10, 500)} KB"
                ))
            db.commit()

        # 6. Generate Risk Alerts
        existing_risks = db.query(RiskAlert).filter(RiskAlert.project_id == project.id).all()
        if len(existing_risks) < 3:
            db.add(RiskAlert(
                project_id=project.id,
                title="项目进度存在延期风险",
                level="高",
                score=85.5,
                reason="核心模块开发里程碑已延期 2 天，且有 3 个阻塞任务未解决。",
                suggestion="建议召开站会讨论阻塞点，必要时重新评估需求优先级。",
                risk_type="进度",
                status="open"
            ))
            db.add(RiskAlert(
                project_id=project.id,
                title="代码冲突频繁",
                level="中",
                score=60.0,
                reason="近期多个 feature 分支同时修改了 utils.py 和 database.py。",
                suggestion="建议规范代码提交流程，增加模块负责人的 Review。",
                risk_type="代码",
                status="open"
            ))
            db.commit()

        # 7. Generate Conversations & Messages
        convs = db.query(Conversation).filter(Conversation.project_id == project.id).all()
        if not convs:
            conv = Conversation(project_id=project.id, name="项目大群", conversation_type="project_group", created_by=project.owner_id)
            db.add(conv)
            db.commit()
            convs = [conv]
            
        for conv in convs:
            existing_msgs = db.query(Message).filter(Message.conversation_id == conv.id).all()
            if len(existing_msgs) < 10:
                for _ in range(8):
                    db.add(Message(
                        project_id=project.id,
                        conversation_id=conv.id,
                        sender_id=random.choice(member_users),
                        content=random.choice([
                            "大家这周的进度怎么样？",
                            "遇到一个棘手的问题，有人帮忙看看这个 API 的返回格式吗？",
                            "已经提交了 PR，麻烦 @一下进行 Review",
                            "明天下午三点开个短会同步一下进度",
                            "UI 稿已经更新了，大家看下 Figma 链接"
                        ])
                    ))
        db.commit()

        # 8. Collaboration Events & Scores
        events = db.query(CollaborationEvent).filter(CollaborationEvent.project_id == project.id).all()
        if len(events) < 10:
            for _ in range(10):
                db.add(CollaborationEvent(
                    project_id=project.id,
                    actor_id=random.choice(member_users),
                    event_type=random.choice(["code_review", "document_update", "task_completed"]),
                    title=f"完成了一次协作: {random.choice(['修复 Bug', '更新文档', '审核代码'])}",
                    score_value=random.randint(5, 20)
                ))
            db.commit()

        for u in member_users:
            score = db.query(ContributionScore).filter(ContributionScore.project_id == project.id, ContributionScore.user_id == u).first()
            if not score:
                score = ContributionScore(
                    project_id=project.id,
                    user_id=u,
                    total_score=random.uniform(300, 900),
                    task_score=random.uniform(100, 300),
                    document_score=random.uniform(50, 150),
                    code_score=random.uniform(100, 400),
                    response_score=random.uniform(20, 100),
                    stability_score=random.uniform(50, 99),
                    completed_tasks=random.randint(2, 20),
                    collaboration_events=random.randint(10, 50)
                )
                db.add(score)
        db.commit()

    print("Data population completed successfully!")

if __name__ == "__main__":
    try:
        seed_data()
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()
