"""
model de resumes
"""

from datetime import datetime
from typing import Literal
from src.database.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, DateTime,  ForeignKey, LargeBinary, Text
from src.database.models.vancancies import Vancancies

class Resumes(Base):

    __tablename__="resumes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    vancancie_id: Mapped[int] = mapped_column(ForeignKey("vancancies.id"))
    pdf: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    status: Mapped[Literal["aproved", "recuse", "pending"]] = mapped_column(String(12), nullable=False)
    reason: Mapped[str] = mapped_column(Text, default="null")
    vancancie: Mapped[Vancancies] = relationship(back_populates="resume")
    created_at = Mapped[datetime] = mapped_column(DateTime, default=datetime.now)




