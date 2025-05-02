from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from .schemas import StatusEnum  # o donde ubiques el Enum
from datetime import datetime, timezone
from app.dependencies import get_db, get_current_user

# Enumeración para el estado del ticket
class StatusEnum(str, PyEnum):
    open = "open"
    closed = "closed"
    in_progress = "in_progress"


# Ticket
class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    status = Column(String, default="open")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    
    user_id = Column(Integer, ForeignKey("users.id"))  # FK
    user = relationship("User", back_populates="tickets")



# models.py
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    tickets = relationship("Ticket", back_populates="user")
    role = Column(String, default="user")  # Ejemplo: 'admin', 'user', etc.

