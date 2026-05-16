from app.domain.schemas import InterchangeRule
from typing import List


class StructuredParser:
    # Classe para converter dados tabulares em objetos de regra
    @staticmethod
    def parse_csv_rules(df) -> List[InterchangeRule]:
        # Itera sobre um DataFrame para criar instâncias estruturadas de regras
        rules = []
        for _, row in df.iterrows():
            rules.append(
                InterchangeRule(
                    id=f"syn_{row['brand']}_{row['merchant_segment']}_{_}",
                    brand=row["brand"],
                    product_type=row["product_type"],
                    transaction_type=row["transaction_type"],
                    channel=row["channel"],
                    merchant_segment=row["merchant_segment"],
                    rate_percent=row["rate_percent"],
                    fixed_fee=row["fixed_fee"],
                    min_fee=row.get("min_fee"),
                    max_fee=row.get("max_fee"),
                    currency=row["currency"],
                    conditions=row.get("conditions"),
                    confidence_score=row.get("confidence_score", 1.0),
                    extraction_method="manual_seed",
                )
            )
        return rules
