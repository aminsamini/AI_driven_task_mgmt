from sqlalchemy import create_engine, Column, String, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///task_management.db"

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class LongTermMemory(Base):
    __tablename__ = "long_term_memory"
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    important_memory = Column(JSON)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_long_term_memory(user_id: str):
    db = SessionLocal()
    memory = db.query(LongTermMemory).filter(LongTermMemory.user_id == user_id).first()
    db.close()
    if memory:
        return memory.important_memory
    return {}

def update_long_term_memory(user_id: str, memory_data: dict):
    db = SessionLocal()
    memory = db.query(LongTermMemory).filter(LongTermMemory.user_id == user_id).first()
    if memory:
        memory.important_memory = memory_data
    else:
        memory = LongTermMemory(user_id=user_id, important_memory=memory_data)
        db.add(memory)
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
