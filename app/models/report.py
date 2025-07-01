from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

Base = declarative_base()

# SQLAlchemy Models
class Report(Base):
    """SQLAlchemy model for reports"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    report_type = Column(String(100), default="custom")  # daily, weekly, monthly, custom
    recipients = Column(JSON)  # Store recipient information as JSON
    file_path = Column(String(500))  # Path to generated report file
    error_message = Column(Text)  # Store error details if generation fails
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Pydantic Models for API
class ReportBase(BaseModel):
    """Base report model"""
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None
    report_type: str = Field(default="custom", max_length=100)
    recipients: Optional[Dict[str, Any]] = None

class ReportCreate(ReportBase):
    """Model for creating reports"""
    pass

class ReportUpdate(BaseModel):
    """Model for updating reports"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)
    report_type: Optional[str] = Field(None, max_length=100)
    recipients: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    is_active: Optional[bool] = None

class ReportResponse(ReportBase):
    """Model for report responses"""
    id: int
    status: str
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

    class Config:
        from_attributes = True
