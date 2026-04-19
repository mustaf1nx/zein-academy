from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./zein.db")

# Исправляем URL для PostgreSQL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Connection pooling для ускорения
if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL с пулом соединений
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,               # 10 постоянных соединений
        max_overflow=20,            # +20 при пиковой нагрузке  
        pool_pre_ping=True,         # проверка соединений
        pool_recycle=3600,          # пересоздание через час
        connect_args={
            "connect_timeout": 10,   # таймаут подключения
            "application_name": "zein-academy",
            "sslmode": "prefer"      # SSL если доступен
        }
    )
else:
    # SQLite (для локальной разработки)
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
