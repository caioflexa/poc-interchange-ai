from sqlalchemy.orm import Session
from app.ingestion.document_loader import DocumentLoader
from app.preprocessing.chunker import Chunker
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import VectorStore
from app.persistence.repositories import DocumentRepository, RuleRepository
from app.persistence.models import DocumentModel, ChunkModel
from app.core.logging import logger
import os


class PipelineService:
    # Orquestrador do fluxo completo de ingestão e processamento
    def __init__(self, db: Session):
        self.db = db
        self.doc_repo = DocumentRepository(db)
        self.rule_repo = RuleRepository(db)
        self.chunker = Chunker()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def ingest_directory(self, raw_dir: str):
        # Varre um diretório e processa todos os arquivos encontrados
        logger.info(f"Ingesting documents from {raw_dir}")
        for root, _, files in os.walk(raw_dir):
            for file in files:
                file_path = os.path.join(root, file)
                self.ingest_file(file_path)

    def ingest_file(self, file_path: str):
        # Processa um arquivo individual: carrega, divide em chunks e vetoriza
        logger.info(f"Processing file: {file_path}")
        doc_id = os.path.basename(file_path)

        # Verifica se o documento já foi ingerido
        if self.doc_repo.get_by_id(doc_id):
            logger.info(f"Document {doc_id} already exists. Skipping.")
            return

        pages = DocumentLoader.load(file_path)
        if not pages:
            return

        doc_model = DocumentModel(
            id=doc_id,
            brand="Visa" if "visa" in doc_id.lower() else "Mastercard",
            title=doc_id,
            doc_type="tarifário",
            file_path=file_path,
            pages_count=len(pages),
        )
        self.doc_repo.save(doc_model)

        chunks = self.chunker.create_chunks(pages)
        brand = "Visa" if "visa" in doc_id.lower() else "Mastercard"

        for i, c in enumerate(chunks):
            c["document_id"] = doc_id
            c["brand"] = brand
            # Persiste o chunk no banco relacional
            chunk_model = ChunkModel(
                document_id=doc_id,
                page=c.get("page", 0),
                text=c["text"],
                chunk_index=i,
                content_type="text",
            )
            self.db.add(chunk_model)

        embeddings = self.embedding_service.encode([c["text"] for c in chunks])
        self.vector_store.add_chunks(chunks, embeddings)

        self.db.commit()
        logger.info(f"Ingested {len(chunks)} chunks from {doc_id}")
