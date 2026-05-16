from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime


Base = declarative_base()


class DocumentModel(Base):
    # Modelo para armazenamento de metadados de documentos
    __tablename__ = "documents"
    id = Column(String, primary_key=True)
    brand = Column(String)
    title = Column(String)
    doc_type = Column(String)
    file_path = Column(String)
    ingestion_date = Column(DateTime, default=datetime.now)
    version = Column(String)
    pages_count = Column(Integer)


class ChunkModel(Base):
    # Modelo para armazenamento de fragmentos de texto (chunks)
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, ForeignKey("documents.id"))
    page = Column(Integer)
    text = Column(Text)
    chunk_index = Column(Integer)
    content_type = Column(String)


class InterchangeRuleModel(Base):
    # Modelo para armazenamento de regras estruturadas extraídas
    __tablename__ = "interchange_rules"
    id = Column(String, primary_key=True)
    brand = Column(String)
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    source_page = Column(Integer, nullable=True)
    source_excerpt = Column(Text, nullable=True)
    product_type = Column(String)
    transaction_type = Column(String)
    channel = Column(String)
    merchant_segment = Column(String)
    mcc = Column(String, nullable=True)
    rate_percent = Column(Float)
    fixed_fee = Column(Float)
    min_fee = Column(Float, nullable=True)
    max_fee = Column(Float, nullable=True)
    currency = Column(String)
    conditions = Column(Text, nullable=True)
    effective_date = Column(String, nullable=True)
    confidence_score = Column(Float)
    extraction_method = Column(String)
    created_at = Column(DateTime, default=datetime.now)
