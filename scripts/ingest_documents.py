import os
import sys

# Adiciona a raiz do projeto ao sys.path para permitir a importação do pacote 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.persistence.database import SessionLocal, init_db
from app.services.pipeline_service import PipelineService
from app.core.config import settings
from app.core.logging import logger


def run_ingestion():
    # Inicializa o banco e executa o serviço de ingestão para o diretório raw
    init_db()
    db = SessionLocal()
    service = PipelineService(db)

    service.ingest_directory(settings.RAW_DATA_DIR)

    db.close()
    logger.info("Ingestion complete")


if __name__ == "__main__":
    run_ingestion()
