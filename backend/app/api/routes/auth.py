from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.entities import User


router = APIRouter()


class RegisterPayload(BaseModel):
    username: str
    password: str
    display_name: str
    email: EmailStr


class LoginPayload(BaseModel):
    username: str
    password: str


class UpdateProfilePayload(BaseModel):
    display_name: str
    phone: str = ""
    bio: str = ""


class UpdatePasswordPayload(BaseModel):
    current_password: str
    new_password: str


@router.post("/register")
def register(payload: RegisterPayload, db: Session = Depends(get_db)):
    exists = db.query(User).filter((User.username == payload.username) | (User.email == payload.email)).first()
    if exists:
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
    user = User(
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        display_name=payload.display_name,
        email=payload.email,
        avatar=f"https://api.dicebear.com/7.x/adventurer/svg?seed={payload.username}",
        title="成员",
        system_role="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return {"token": token, "user": serialize_user(user)}


@router.post("/login")
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="账号或密码错误")
    token = create_access_token(user.id)
    return {"token": token, "user": serialize_user(user)}


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return serialize_user(current_user)


@router.put("/me")
def update_me(payload: UpdateProfilePayload, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.display_name = payload.display_name
    current_user.phone = payload.phone
    current_user.bio = payload.bio
    db.commit()
    db.refresh(current_user)
    return serialize_user(current_user)


@router.put("/me/password")
def update_password(payload: UpdatePasswordPayload, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="当前密码错误")
    current_user.password_hash = get_password_hash(payload.new_password)
    db.commit()
    return {"message": "密码更新成功"}


@router.get("/users/search")
def search_users(keyword: str = "", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(User)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            (User.username.like(like)) | (User.display_name.like(like)) | (User.email.like(like))
        )
    users = query.limit(20).all()
    return [serialize_user(user) for user in users if user.id != current_user.id]


def serialize_user(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "email": user.email,
        "phone": user.phone,
        "avatar": user.avatar,
        "system_role": user.system_role,
        "status": user.status,
        "title": user.title,
        "bio": user.bio,
    }
