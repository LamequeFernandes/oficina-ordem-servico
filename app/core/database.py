from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


DATABASE_URL = f'mysql+pymysql://{settings.USER_DB}:{settings.PASSWORD_DB}@{settings.HOST_DB}:{settings.PORT_DB}/{settings.DATABASE}'
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
