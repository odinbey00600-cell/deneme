from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config_manager.settings import settings

engine = create_engine(settings.db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
