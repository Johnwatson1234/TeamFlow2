from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import ensure_project_member, get_current_user
from app.core.realtime import manager
from app.db.session import get_db
from app.models.entities import Conversation, Message, Notification, ProjectMember, TaskActivity, User
from app.services.presenters import build_user_map, serialize_conversation, serialize_message, serialize_task
from app.utils.serializers import dump_json


router = APIRouter()


class ConversationPayload(BaseModel):
    name: str
    conversation_type: str = "project_group"
    related_task_id: int | None = None
    is_pinned: bool = False


class MessagePayload(BaseModel):
    content: str
    message_type: str = "text"
    code_language: str = ""
    metadata: dict = {}


@router.get("/projects/{project_id}/conversations")
def list_conversations(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_member(project_id, current_user.id, db)
    rows = db.query(Conversation).filter(Conversation.project_id == project_id).order_by(Conversation.is_pinned.desc(), Conversation.created_at.asc()).all()
    return [serialize_conversation(item, db, current_user.id) for item in rows]


@router.post("/projects/{project_id}/conversations")
def create_conversation(project_id: int, payload: ConversationPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_member(project_id, current_user.id, db)
    row = Conversation(
        project_id=project_id,
        name=payload.name,
        conversation_type=payload.conversation_type,
        related_task_id=payload.related_task_id,
        is_pinned=payload.is_pinned,
        created_by=current_user.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize_conversation(row, db, current_user.id)


@router.get("/conversations/{conversation_id}/messages")
def list_messages(conversation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    ensure_project_member(conversation.project_id, current_user.id, db)
    users = build_user_map(db)
    rows = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()
    task = None
    if conversation.related_task_id:
        from app.models.entities import Task

        task = db.query(Task).filter(Task.id == conversation.related_task_id).first()
    return {
        "conversation": serialize_conversation(conversation, db, current_user.id),
        "task_context": serialize_task(task, users) if task else None,
        "messages": [serialize_message(item, users) for item in rows],
    }


@router.post("/conversations/{conversation_id}/messages")
async def create_message(conversation_id: int, payload: MessagePayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    ensure_project_member(conversation.project_id, current_user.id, db)
    row = Message(
        project_id=conversation.project_id,
        conversation_id=conversation.id,
        sender_id=current_user.id,
        message_type=payload.message_type,
        content=payload.content,
        code_language=payload.code_language,
        metadata_json=dump_json(payload.metadata),
    )
    db.add(row)
    if conversation.related_task_id:
        db.add(
            TaskActivity(
                task_id=conversation.related_task_id,
                project_id=conversation.project_id,
                actor_id=current_user.id,
                activity_type="commented",
                content=f"{current_user.display_name} 发表了任务讨论",
            )
        )
    member_ids = [item.user_id for item in db.query(ProjectMember).filter(ProjectMember.project_id == conversation.project_id).all() if item.user_id != current_user.id]
    for user_id in member_ids:
        db.add(
            Notification(
                user_id=user_id,
                project_id=conversation.project_id,
                type="message",
                title=f"{current_user.display_name} 发送了新消息",
                content=payload.content[:80],
                ref_type="conversation",
                ref_id=conversation.id,
            )
        )
    db.commit()
    db.refresh(row)
    users = build_user_map(db)
    data = serialize_message(row, users)
    await manager.broadcast(conversation.project_id, {"type": "message:new", "payload": data})
    return data


@router.post("/conversations/{conversation_id}/read")
def mark_read(conversation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    ensure_project_member(conversation.project_id, current_user.id, db)
    return {"message": "已标记已读"}


@router.get("/projects/{project_id}/messages")
def project_messages(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_member(project_id, current_user.id, db)
    group = db.query(Conversation).filter(Conversation.project_id == project_id, Conversation.conversation_type == "project_group").first()
    if not group:
        raise HTTPException(status_code=404, detail="项目群聊不存在")
    return list_messages(group.id, db, current_user)


@router.post("/projects/{project_id}/messages")
async def send_project_message(project_id: int, payload: MessagePayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_member(project_id, current_user.id, db)
    group = db.query(Conversation).filter(Conversation.project_id == project_id, Conversation.conversation_type == "project_group").first()
    if not group:
        group = Conversation(project_id=project_id, conversation_type="project_group", name="项目群聊", created_by=current_user.id, is_pinned=True)
        db.add(group)
        db.commit()
        db.refresh(group)
    return await create_message(group.id, payload, db, current_user)


@router.delete("/messages/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(Message).filter(Message.id == message_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="消息不存在")
    ensure_project_member(row.project_id, current_user.id, db)
    db.delete(row)
    db.commit()
    return {"message": "消息已删除"}
