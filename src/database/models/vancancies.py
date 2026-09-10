"""
modelo de vancancies
"""

from datetime import datetime
from src.database.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, DateTime, Text, ForeignKey
from typing import List

class Vancancies(Base):

    __tablename__="vancancies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    resumes: Mapped[List["Resumes"]] = relationship(back_populates="vancancie", cascade="all, delete-orphan")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


    
