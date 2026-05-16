import pandas as pd
import os
import sys

# Adiciona a raiz do projeto ao sys.path para permitir a importação do pacote 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.persistence.database import SessionLocal, init_db
from app.persistence.repositories import RuleRepository
from app.persistence.models import InterchangeRuleModel
from app.core.config import settings
from app.core.logging import logger


def load_synthetic_rules():
    # Carrega as regras de exemplo (CSV) para o banco relacional
    init_db()
    db = SessionLocal()
    repo = RuleRepository(db)

    csv_path = os.path.join(settings.SYNTHETIC_DATA_DIR, "interchange_rules_sample.csv")
    if not os.path.exists(csv_path):
        logger.error(f"Synthetic rules file not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        rule_id = f"syn_{row['brand']}_{row['merchant_segment']}_{_}"

        # Verifica se a regra já existe
        if (
            db.query(InterchangeRuleModel)
            .filter(InterchangeRuleModel.id == rule_id)
            .first()
        ):
            continue

        # Cria o modelo a partir de cada linha do arquivo CSV
        rule = InterchangeRuleModel(
            id=rule_id,
            brand=row["brand"],
            product_type=row["product_type"],
            transaction_type=row["transaction_type"],
            channel=row["channel"],
            merchant_segment=row["merchant_segment"],
            rate_percent=row["rate_percent"],
            fixed_fee=row["fixed_fee"],
            min_fee=row["min_fee"] if pd.notnull(row["min_fee"]) else None,
            max_fee=row["max_fee"] if pd.notnull(row["max_fee"]) else None,
            currency=row["currency"],
            conditions=row["conditions"],
            confidence_score=1.0,
            extraction_method="manual_seed",
        )
        repo.save(rule)

    logger.info(f"Loaded {len(df)} synthetic rules")
    db.close()


if __name__ == "__main__":
    load_synthetic_rules()
