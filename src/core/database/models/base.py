from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, DateTime

Base = declarative_base()

class TimestampMixin:
    """Mixin for adding timestamp fields to models"""
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 