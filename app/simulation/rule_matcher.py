from app.domain.schemas import Transaction, InterchangeRule
from typing import List, Optional


class RuleMatcher:
    # Lógica para encontrar a melhor regra para uma transação específica
    def __init__(self, rules: List[InterchangeRule]):
        self.rules = rules

    def find_best_match(self, transaction: Transaction) -> Optional[InterchangeRule]:
        # Filtra regras compatíveis com bandeira, produto e canal
        eligible_rules = [
            r
            for r in self.rules
            if r.brand == transaction.brand
            and (
                r.product_type == transaction.product_type
                or r.product_type == "unknown"
            )
            and (
                r.transaction_type == transaction.transaction_type
                or r.transaction_type == "unknown"
            )
            and (r.channel == transaction.channel or r.channel == "unknown")
        ]

        if not eligible_rules:
            return None

        # Retorna a regra com maior nível de confiança
        return max(eligible_rules, key=lambda x: x.confidence_score)
