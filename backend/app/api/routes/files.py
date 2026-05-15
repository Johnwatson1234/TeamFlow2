from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import ensure_project_member, get_current_user
from app.core.config import UPLOAD_DIR
from app.db.session import get_db
from app.models.entities import FileResource, User
from app.services.presenters import build_user_map, serialize_file


router = APIRouter()


@router.get("/projects/{project_id}/files")
def list_files(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_member(project_id, current_user.id, db)
    users = build_user_map(db)
    rows = db.query(FileResource).filter(FileResource.project_id == project_id).order_by(FileResource.updated_at.desc()).all()
    return [serialize_file(item, users) for item in rows]


@router.post("/projects/{project_id}/files/upload")
async def upload_file(
    project_id: int,
    upload: UploadFile = File(...),
    category: str = Form("其他"),
    related_task: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_project_member(project_id, current_user.id, db)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target = UPLOAD_DIR / upload.filename
    content = await upload.read()
    target.write_bytes(content)
    row = FileResource(
        project_id=project_id,
        name=upload.filename,
        file_type=upload.content_type or "文件",
        related_task=related_task,
        uploader_id=current_user.id,
        version_label="v1.0",
        review_status="待评审",
        download_count=0,
        category=category,
        storage_path=str(target),
        size_label=f"{round(len(content) / 1024, 1)} KB",
        description="用户上传文件",
        comments_json="[]",
    )
    db.add(row)
    db.commit()
    return {"message": "上传成功"}


@router.delete("/files/{id}")
def delete_file(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(FileResource).filter(FileResource.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail="文件不存在")
    ensure_project_member(row.project_id, current_user.id, db)
    db.delete(row)
    db.commit()
    return {"message": "文件已删除"}
