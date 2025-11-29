from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .connection import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    position = Column(String)
    job_description = Column(String)

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    assign_by = Column(String)  # User ID
    assignee = Column(String)   # User ID
    importance = Column(String) # between 1-5 
    priority = Column(String)   # between 1-5
    deadline = Column(DateTime)
    suggestions = Column(String)
    status = Column(String, default="open")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
