from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

Base = declarative_base()

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    data = Column(JSON)  # Store processed data as JSON
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    sent_at = Column(DateTime, nullable=True)
    recipients = Column(JSON)  # Email addresses and notification targets
    report_type = Column(String(100))  # daily, weekly, monthly, custom
    is_active = Column(Boolean, default=True)

class AgworldData(Base):
    __tablename__ = "agworld_data"
    
    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String(100), nullable=False)  # field, crop, activity, etc.
    external_id = Column(String(255))  # Agworld entity ID
    raw_data = Column(JSON)
    processed_data = Column(JSON)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    sync_status = Column(String(50), default="synced")

# Pydantic schemas for API
class ReportBase(BaseModel):
    title: str
    content: Optional[str] = None
    report_type: str = "custom"
    recipients: Optional[Dict[str, Any]] = None

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    recipients: Optional[Dict[str, Any]] = None

class ReportResponse(ReportBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True
