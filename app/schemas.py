from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = ""
    class Config:
        from_attributes = True

class DocumentOut(BaseModel):
    id: int
    title: str
    filename: Optional[str] = None
    description: Optional[str] = ""
    mime_type: Optional[str] = None
    file_ext: Optional[str] = None
    size_bytes: Optional[int] = 0
    category: Optional[CategoryOut] = None
    tags: Optional[str] = ""
    author: Optional[str] = ""
    subject: Optional[str] = ""
    drive_modified_time: Optional[str] = None
    text_status: str = "pending"
    is_public: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    text_preview: Optional[str] = None
    class Config:
        from_attributes = True

class DocumentDetail(DocumentOut):
    text_content: Optional[str] = None
    download_url_api: Optional[str] = None

class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[DocumentOut]

class HealthOut(BaseModel):
    status: str
    documents: int
    version: str = "1.0.0"
