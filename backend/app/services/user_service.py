from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth.security import hash_password, verify_password
from app.models.models import User
from app.schemas.schemas import UserCreate, UserUpdate

def authenticate(db: Session, email: str, password: str):
    user = db.scalar(select(User).where(User.email == email.lower()))
    if user and user.enabled and verify_password(password, user.password_hash):
        return user
    return None

def list_users(db: Session): return db.scalars(select(User).order_by(User.email)).all()
def get_user(db: Session, user_id: UUID):
    user = db.get(User, user_id)
    if not user: raise HTTPException(404, "User not found")
    return user
def create_user(db: Session, data: UserCreate):
    if db.scalar(select(User).where(User.email == data.email.lower())): raise HTTPException(409, "Email already exists")
    user = User(name=data.name, email=data.email.lower(), password_hash=hash_password(data.password), role=data.role, enabled=data.enabled)
    db.add(user); db.commit(); db.refresh(user); return user
def update_user(db: Session, user_id: UUID, data: UserUpdate):
    user = get_user(db, user_id)
    values = data.model_dump(exclude_unset=True)
    if "password" in values: user.password_hash = hash_password(values.pop("password"))
    if "email" in values and values["email"]: values["email"] = values["email"].lower()
    for k,v in values.items(): setattr(user,k,v)
    db.commit(); db.refresh(user); return user
