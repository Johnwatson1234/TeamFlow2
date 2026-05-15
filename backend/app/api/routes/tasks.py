from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import ensure_project_member, get_current_user
from app.db.session import get_db
from app.models.entities import CollaborationEvent, Conversation, Message, Milestone, Notification, Task, TaskActivity, User
from app.services.presenters import build_user_map, serialize_conversation, serialize_task, serialize_task_activity


router = APIRouter()


class TaskPayload(BaseModel):
    title: str
    description: str = ""
    status: str = "TODO"
    priority: str = "中"
    progress: int = 0
    assignee_id: int | None = None
    due_date: str = ""
    start_date: str = ""
    blocker_reason: str = ""
    related_requirement: str = ""
    related_document: str = ""
    related_commit: str = ""
    milestone_id: int | None = None


class MilestonePayload(BaseModel):
    name: str
    due_date: str
    status: str = "待开始"


class TaskActionPayload(BaseModel):
    content: str = ""
    progress: int | None = None
    assignee_id: int | None = None
    status: str | None = None
    blocker_reason: str = ""


@router.get("/projects/{project_id}/tasks")
def list_tasks(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_member(project_id, current_user.id, db)
    users = build_user_map(db)
    rows = db.query(Task).filter(Task.project_id == project_id, Task.archived == False).order_by(Task.created_at.desc()).all()  # noqa: E712
    return [serialize_task(item, users) for item in rows]


@router.get("/me/tasks")
def my_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = build_user_map(db)
    rows = db.query(Task).filter(Task.assignee_id == current_user.id, Task.archived == False).all()  # noqa: E712
    return [serialize_task(item, users) for item in rows]


@router.post("/projects/{project_id}/tasks")
def create_task(project_id: int, payload: TaskPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_member(project_id, current_user.id, db)
    task = Task(
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        response_status="待接收" if payload.assignee_id else "未分配",
        priority=payload.priority,
        progress=payload.progress,
        assignee_id=payload.assignee_id,
        due_date=payload.due_date,
        start_date=payload.start_date,
        blocker_reason=payload.blocker_reason,
        related_requirement=payload.related_requirement,
        related_document=payload.related_document,
        related_commit=payload.related_commit,
        milestone_id=payload.milestone_id,
        created_by=current_user.id,
    )
    db.add(task)
    db.flush()
    conversation = Conversation(
        project_id=project_id,
        conversation_type="task",
        related_task_id=task.id,
        name=f"任务 #{task.id} {task.title}",
        created_by=current_user.id,
    )
    db.add(conversation)
    db.add(
        TaskActivity(
            task_id=task.id,
            project_id=project_id,
            actor_id=current_user.id,
            activity_type="created",
            content=f"{current_user.display_name} 创建了任务 {task.title}",
        )
    )
    db.add(
        CollaborationEvent(
            project_id=project_id,
            actor_id=current_user.id,
            event_type="task",
            title=f"{current_user.display_name} 创建了任务",
            content=task.title,
            related_type="task",
            related_id=task.id,
            score_value=4.0,
        )
    )
    if payload.assignee_id:
        db.add(
            Notification(
                user_id=payload.assignee_id,
                project_id=project_id,
                type="task_assigned",
                title="你有新的任务分配",
                content=task.title,
                ref_type="task",
                ref_id=task.id,
            )
        )
    db.commit()
    db.refresh(task)
    return serialize_task(task, build_user_map(db))


@router.get("/tasks/{task_id}")
def task_detail(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    ensure_project_member(task.project_id, current_user.id, db)
    return serialize_task(task, build_user_map(db))


@router.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    ensure_project_member(task.project_id, current_user.id, db)
    for field in ["title", "description", "status", "priority", "progress", "assignee_id", "due_date", "start_date", "blocker_reason", "related_requirement", "related_document", "related_commit", "milestone_id"]:
        setattr(task, field, getattr(payload, field))
    db.add(
        TaskActivity(
            task_id=task.id,
            project_id=task.project_id,
            actor_id=current_user.id,
            activity_type="updated",
            content=f"{current_user.display_name} 更新了任务信息",
        )
    )
    db.commit()
    return serialize_task(task, build_user_map(db))


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    ensure_project_member(task.project_id, current_user.id, db)
    task.archived = True
    db.commit()
    return {"message": "任务已归档"}


@router.post("/tasks/{task_id}/assign")
def assign_task(task_id: int, payload: TaskActionPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    ensure_project_member(task.project_id, current_user.id, db)
    task.assignee_id = payload.assignee_id
    task.response_status = "待接收"
    db.add(
        TaskActivity(
            task_id=task.id,
            project_id=task.project_id,
            actor_id=current_user.id,
            activity_type="assigned",
            content=f"{current_user.display_name} 分配了任务",
        )
    )
    if payload.assignee_id:
        db.add(
            Notification(
                user_id=payload.assignee_id,
                project_id=task.project_id,
                type="task_assigned",
                title="你收到新的任务分配",
                content=task.title,
                ref_type="task",
                ref_id=task.id,
            )
        )
    db.commit()
    return {"message": "任务已分配"}


@router.post("/tasks/{task_id}/accept")
def accept_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    ensure_project_member(task.project_id, current_user.id, db)
    task.response_status = "处理中"
    task.status = "IN_PROGRESS"
    db.add(TaskActivity(task_id=task.id, project_id=task.project_id, actor_id=current_user.id, activity_type="accepted", content=f"{current_user.display_name} 接收并开始处理任务"))
    db.commit()
    return {"message": "已接收任务"}


@router.post("/tasks/{task_id}/start")
def start_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return accept_task(task_id, db, current_user)


@router.post("/tasks/{task_id}/block")
def block_task(task_id: int, payload: TaskActionPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    ensure_project_member(task.project_id, current_user.id, db)
    task.status = "BLOCKED"
    task.response_status = "阻塞中"
    task.blocker_reason = payload.blocker_reason or payload.content
    db.add(TaskActivity(task_id=task.id, project_id=task.project_id, actor_id=current_user.id, activity_type="blocked", content=f"{current_user.display_name} 标记任务阻塞：{task.blocker_reason}"))
    db.commit()
    return {"message": "已标记阻塞"}


@router.post("/tasks/{task_id}/complete")
def complete_task(task_id: int, payload: TaskActionPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    ensure_project_member(task.project_id, current_user.id, db)
    task.status = "DONE"
    task.response_status = "已完成"
    task.progress = 100
    db.add(TaskActivity(task_id=task.id, project_id=task.project_id, actor_id=current_user.id, activity_type="completed", content=f"{current_user.display_name} 完成了任务"))
    db.commit()
    return {"message": "任务已完成"}


@router.get("/tasks/{task_id}/activities")
def list_activities(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    ensure_project_member(task.project_id, current_user.id, db)
    users = build_user_map(db)
    rows = db.query(TaskActivity).filter(TaskActivity.task_id == task_id).order_by(TaskActivity.created_at.desc()).all()
    return [serialize_task_activity(item, users) for item in rows]


@router.get("/tasks/{task_id}/conversation")
def get_task_conversation(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    ensure_project_member(task.project_id, current_user.id, db)
    conversation = db.query(Conversation).filter(Conversation.related_task_id == task_id).first()
    if not conversation:
        conversation = Conversation(
            project_id=task.project_id,
            conversation_type="task",
            related_task_id=task.id,
            name=f"任务 #{task.id} {task.title}",
            created_by=current_user.id,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    return serialize_conversation(conversation, db, current_user.id)


@router.get("/projects/{project_id}/milestones")
def list_milestones(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_member(project_id, current_user.id, db)
    rows = db.query(Milestone).filter(Milestone.project_id == project_id).order_by(Milestone.order_index.asc()).all()
    return [{"id": item.id, "name": item.name, "due_date": item.due_date, "status": item.status, "order_index": item.order_index} for item in rows]


@router.post("/projects/{project_id}/milestones")
def create_milestone(project_id: int, payload: MilestonePayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_member(project_id, current_user.id, db)
    order_index = db.query(Milestone).filter(Milestone.project_id == project_id).count()
    row = Milestone(project_id=project_id, name=payload.name, due_date=payload.due_date, status=payload.status, order_index=order_index)
    db.add(row)
    db.commit()
    return {"message": "里程碑已创建"}
