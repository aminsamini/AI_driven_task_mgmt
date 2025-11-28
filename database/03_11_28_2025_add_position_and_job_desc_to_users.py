from sqlalchemy import create_engine, text

DATABASE_URL = "sqlite:///task_management.db"

def upgrade():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        with connection.begin():
            try:
                connection.execute(text("ALTER TABLE users ADD COLUMN position VARCHAR"))
                print("✅ Added 'position' column to 'users' table.")
            except Exception as e:
                print(f"⚠️ Could not add 'position' column (might already exist): {e}")

            try:
                connection.execute(text("ALTER TABLE users ADD COLUMN job_description VARCHAR"))
                print("✅ Added 'job_description' column to 'users' table.")
            except Exception as e:
                print(f"⚠️ Could not add 'job_description' column (might already exist): {e}")

if __name__ == "__main__":
    upgrade()
