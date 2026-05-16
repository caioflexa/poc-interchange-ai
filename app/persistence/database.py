from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.persistence.models import Base
import os


# Criação do engine de conexão com SQLite
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    # Inicializa o banco de dados e cria as tabelas se não existirem
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db():
    # Generator para fornecer sessões do banco de dados para a API
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
