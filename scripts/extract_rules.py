import os
import sys

# Adiciona a raiz do projeto ao sys.path para permitir a importação do pacote 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.persistence.database import SessionLocal, init_db
from app.persistence.models import ChunkModel, InterchangeRuleModel
from app.extraction.rule_extractor import RuleExtractor
from app.persistence.repositories import RuleRepository
from app.core.logging import logger


def run_extraction():
    # Processa os chunks armazenados para extrair regras estruturadas via regex
    init_db()
    db = SessionLocal()
    extractor = RuleExtractor()
    repo = RuleRepository(db)

    chunks = db.query(ChunkModel).all()
    if not chunks:
        logger.warning("No chunks found in database. Run ingestion first.")
        return

    extracted_count = 0
    for chunk in chunks:
        # Tenta extrair regras de cada fragmento de texto
        rules = extractor.extract_from_text(chunk.text, chunk.document_id, chunk.page)
        for rule_schema in rules:
            existing = (
                db.query(InterchangeRuleModel)
                .filter(InterchangeRuleModel.id == rule_schema.id)
                .first()
            )
            if not existing:
                model = InterchangeRuleModel(
                    id=rule_schema.id,
                    brand=rule_schema.brand,
                    document_id=rule_schema.document_id,
                    source_page=rule_schema.source_page,
                    source_excerpt=rule_schema.source_excerpt,
                    product_type=rule_schema.product_type,
                    transaction_type=rule_schema.transaction_type,
                    channel=rule_schema.channel,
                    merchant_segment=rule_schema.merchant_segment,
                    rate_percent=rule_schema.rate_percent,
                    fixed_fee=rule_schema.fixed_fee,
                    currency=rule_schema.currency,
                    confidence_score=rule_schema.confidence_score,
                    extraction_method=rule_schema.extraction_method,
                )
                repo.save(model)
                extracted_count += 1

    logger.info(f"Extracted {extracted_count} rules from {len(chunks)} chunks")
    db.close()


if __name__ == "__main__":
    run_extraction()
