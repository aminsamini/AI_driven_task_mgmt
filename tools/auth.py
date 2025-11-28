from passlib.context import CryptContext
from database import SessionLocal, User
import uuid
import re
import time

class RateLimitException(Exception):
    pass

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

login_attempts = {}
LOCKOUT_TIME = 600 # 10 minutes
MAX_ATTEMPTS = 5

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def is_valid_email(email):
    return re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email)

def is_strong_password(password):
    return len(password) >= 8 and any(c.isupper() for c in password) and any(c.islower() for c in password) and any(c.isdigit() for c in password)

def create_user(first_name, last_name, email, password, position=None, job_description=None):
    if not is_valid_email(email):
        raise ValueError("Invalid email format.")
    if not is_strong_password(password):
        raise ValueError("Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number.")

    with SessionLocal() as db:
        if db.query(User).filter(User.email == email).first():
            raise ValueError("Email already registered.")

        hashed_password = get_password_hash(password)
        db_user = User(
            id=str(uuid.uuid4()),
            first_name=first_name,
            last_name=last_name,
            email=email,
            hashed_password=hashed_password,
            position=position,
            job_description=job_description
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

def get_user_by_email(email):
    with SessionLocal() as db:
        return db.query(User).filter(User.email == email).first()

def authenticate_user(email, password):
    if email in login_attempts and time.time() - login_attempts[email]['time'] < LOCKOUT_TIME and login_attempts[email]['count'] >= MAX_ATTEMPTS:
        raise RateLimitException("Too many login attempts. Please try again later.")

    user = get_user_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        if email in login_attempts:
            login_attempts[email]['count'] += 1
            login_attempts[email]['time'] = time.time()
        else:
            login_attempts[email] = {'count': 1, 'time': time.time()}
        return None

    if email in login_attempts:
        del login_attempts[email]

    return user
