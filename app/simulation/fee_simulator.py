from app.domain.schemas import Transaction, InterchangeRule, SimulationResult


class FeeSimulator:
    # Motor de cálculo de taxas de intercâmbio
    @staticmethod
    def simulate(transaction: Transaction, rule: InterchangeRule) -> SimulationResult:
        # Aplica o cálculo matemático considerando percentual, taxa fixa e limites
        base_fee = (transaction.amount * rule.rate_percent / 100) + rule.fixed_fee

        final_fee = base_fee
        if rule.min_fee is not None:
            final_fee = max(final_fee, rule.min_fee)
        if rule.max_fee is not None:
            final_fee = min(final_fee, rule.max_fee)

        return SimulationResult(
            matched_rule_id=rule.id,
            brand=transaction.brand,
            rate_percent=rule.rate_percent,
            fixed_fee=rule.fixed_fee,
            estimated_interchange_fee=round(final_fee, 4),
            currency=rule.currency,
            confidence_score=rule.confidence_score,
            source_document=rule.document_id,
            source_page=rule.source_page,
            notes=f"Calculado usando regra {rule.id}. Condições: {rule.conditions or 'Nenhuma'}",
        )
