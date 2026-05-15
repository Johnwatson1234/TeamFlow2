from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import ensure_project_member, get_current_user
from app.db.session import get_db
from app.models.entities import CollaborationEvent, Document, DocumentVersion, User
from app.services.presenters import build_user_map, serialize_document, serialize_document_version


router = APIRouter()


class DocumentPayload(BaseModel):
    title: str
    content: str = ""
    related_task_id: int | None = None
    permission_status: str = "团队可编辑"
    tags: list[str] = []


class VersionPayload(BaseModel):
    summary: str
    content: str


@router.get("/projects/{project_id}/documents")
def list_documents(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_member(project_id, current_user.id, db)
    users = build_user_map(db)
    rows = db.query(Document).filter(Document.project_id == project_id, Document.is_deleted == False).order_by(Document.updated_at.desc()).all()  # noqa: E712
    return [serialize_document(item, users) for item in rows]


@router.post("/projects/{project_id}/documents")
def create_document(project_id: int, payload: DocumentPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_member(project_id, current_user.id, db)
    from app.utils.serializers import dump_json

    row = Document(
        project_id=project_id,
        title=payload.title,
        content=payload.content,
        author_id=current_user.id,
        updated_by_id=current_user.id,
        related_task_id=payload.related_task_id,
        permission_status=payload.permission_status,
        tags_json=dump_json(payload.tags),
        version_count=1,
    )
    db.add(row)
    db.flush()
    db.add(
        DocumentVersion(
            document_id=row.id,
            version_label="v1.0",
            summary="创建文档",
            content=payload.content,
            author_id=current_user.id,
            added_words=len(payload.content),
            modified_words=0,
        )
    )
    db.add(
        CollaborationEvent(
            project_id=project_id,
            actor_id=current_user.id,
            event_type="document",
            title=f"{current_user.display_name} 创建了文档",
            content=payload.title,
            related_type="document",
            related_id=row.id,
            score_value=3.0,
        )
    )
    db.commit()
    db.refresh(row)
    return serialize_document(row, build_user_map(db))


@router.get("/documents/{id}")
def get_document(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(Document).filter(Document.id == id, Document.is_deleted == False).first()  # noqa: E712
    if not row:
        raise HTTPException(status_code=404, detail="文档不存在")
    ensure_project_member(row.project_id, current_user.id, db)
    return serialize_document(row, build_user_map(db))


@router.put("/documents/{id}")
def update_document(id: int, payload: DocumentPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.utils.serializers import dump_json

    row = db.query(Document).filter(Document.id == id, Document.is_deleted == False).first()  # noqa: E712
    if not row:
        raise HTTPException(status_code=404, detail="文档不存在")
    ensure_project_member(row.project_id, current_user.id, db)
    row.title = payload.title
    row.content = payload.content
    row.updated_by_id = current_user.id
    row.related_task_id = payload.related_task_id
    row.permission_status = payload.permission_status
    row.tags_json = dump_json(payload.tags)
    db.commit()
    return serialize_document(row, build_user_map(db))


@router.delete("/documents/{id}")
def delete_document(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(Document).filter(Document.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail="文档不存在")
    ensure_project_member(row.project_id, current_user.id, db)
    row.is_deleted = True
    db.commit()
    return {"message": "文档已删除"}


@router.get("/documents/{id}/versions")
def list_versions(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(Document).filter(Document.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail="文档不存在")
    ensure_project_member(row.project_id, current_user.id, db)
    users = build_user_map(db)
    versions = db.query(DocumentVersion).filter(DocumentVersion.document_id == id).order_by(DocumentVersion.created_at.desc()).all()
    return [serialize_document_version(item, users) for item in versions]


@router.post("/documents/{id}/versions")
def create_version(id: int, payload: VersionPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(Document).filter(Document.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail="文档不存在")
    ensure_project_member(row.project_id, current_user.id, db)
    row.version_count += 1
    row.content = payload.content
    row.updated_by_id = current_user.id
    version = DocumentVersion(
        document_id=id,
        version_label=f"v1.{row.version_count - 1}",
        summary=payload.summary,
        content=payload.content,
        author_id=current_user.id,
        added_words=max(len(payload.content) - len(row.content), 0),
        modified_words=min(len(payload.content), len(row.content)),
    )
    db.add(version)
    db.commit()
    return {"message": "版本已保存"}
