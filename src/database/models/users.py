"""
Models de users
"""

from datetime import datetime
import uuid
from typing import Literal
from src.database.base import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, DateTime, UUID, BOOLEAN, Integer

class Users(Base):

    __tablename__= "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    public_id: Mapped[uuid.UUID] = mapped_column(UUID, default=uuid.uuid4, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False, index=True, unique=True)
    cpf: Mapped[str] = mapped_column(String(12), unique=True, nullable=False, index=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[Literal["male", "female", "other"]] = mapped_column(String(15), nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    permission: Mapped[bool] = mapped_column(BOOLEAN, default=False)
    role: Mapped[Literal["admin", "user"]] = mapped_column(String(20), default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


