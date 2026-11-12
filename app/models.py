from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)
    slug = Column(String(120), unique=True, nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    drive_file_id = Column(String(255), unique=True, index=True)
    title = Column(String(500), nullable=False)
    filename = Column(String(500))
    description = Column(Text, default="")
    mime_type = Column(String(255))
    file_ext = Column(String(50))
    size_bytes = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    tags = Column(Text, default="")
    author = Column(String(255), default="")
    subject = Column(String(255), default="")
    drive_modified_time = Column(String(64))
    drive_web_view_link = Column(String(1000))
    download_url = Column(String(1000))
    text_content = Column(Text, default="")
    text_status = Column(String(50), default="pending")  # pending/extracted/failed/none
    text_error = Column(Text, default="")
    is_public = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category = relationship("Category")

class Setting(Base):
    __tablename__ = "settings"
    key = Column(String(120), primary_key=True)
    value = Column(Text, default="")

class SyncLog(Base):
    __tablename__ = "sync_logs"
    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="running")
    added = Column(Integer, default=0)
    updated = Column(Integer, default=0)
    deleted = Column(Integer, default=0)
    errors = Column(Text, default="")
    message = Column(Text, default="")

class AdminSession(Base):
    __tablename__ = "admin_sessions"
    token = Column(String(255), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
