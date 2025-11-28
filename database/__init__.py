from .connection import engine, SessionLocal, Base
from .models import User, Task

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized (tables created if not exist).")
