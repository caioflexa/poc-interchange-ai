from app.simulation.fee_simulator import FeeSimulator
from app.domain.schemas import Transaction, InterchangeRule
from app.domain.enums import Brand, ProductType, TransactionType, Channel


def test_fee_calculation():
    # Testa se o cálculo da taxa de intercâmbio está correto
    transaction = Transaction(
        brand=Brand.VISA,
        amount=100.0,
        product_type=ProductType.CREDIT,
        transaction_type=TransactionType.PURCHASE,
        channel=Channel.CARD_PRESENT,
    )
    rule = InterchangeRule(
        brand=Brand.VISA, rate_percent=1.5, fixed_fee=0.10, currency="BRL"
    )
    result = FeeSimulator.simulate(transaction, rule)

    # Verifica se o resultado (1.5% de 100 + 0.10) é igual a 1.6
    assert result.estimated_interchange_fee == 1.6
