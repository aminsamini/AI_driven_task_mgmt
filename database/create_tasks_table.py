from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

DATABASE_URL = "sqlite:///task_management.db"

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    assign_by = Column(String)  # User ID
    assignee = Column(String)   # User ID
    importance = Column(String)
    priority = Column(String)
    deadline = Column(DateTime)
    suggestions = Column(String)
    status = Column(String, default="open")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine(DATABASE_URL)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Tasks table created successfully.")

if __name__ == "__main__":
    init_db()
