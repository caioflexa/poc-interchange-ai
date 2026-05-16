import re
from app.domain.schemas import InterchangeRule
from app.domain.enums import (
    Brand,
    ProductType,
    TransactionType,
    Channel,
    ExtractionMethod,
)
from app.core.logging import logger
from app.extraction.llm_extractor import LLMExtractor


class RuleExtractor:
    # Classe que extrai regras estruturadas a partir de texto bruto
    def __init__(self):
        self.llm_extractor = LLMExtractor()

    def extract_from_text(
        self, text: str, document_id: str, page: int
    ) -> list[InterchangeRule]:
        # Combina extração por regex (rápida) e por LLM (semântica)
        rules = []

        # 1. Extração por Regex (Legado/Heurística)
        rules.extend(self._extract_via_regex(text, document_id, page))

        # 2. Extração por LLM (Sempre ativo se o sistema estiver rodando)
        logger.info(f"Extracting rules via LLM for {document_id} page {page}")
        llm_rules = self.llm_extractor.extract_from_text(text, document_id, page)
        rules.extend(llm_rules)

        return rules

    def _extract_via_regex(
        self, text: str, document_id: str, page: int
    ) -> list[InterchangeRule]:
        rules = []
        rate_pattern = r"(\d+\.?\d*)\s*%"
        rates = re.findall(rate_pattern, text)
        if rates:
            for i, rate in enumerate(rates):
                product = (
                    ProductType.CREDIT
                    if "credit" in text.lower()
                    else ProductType.DEBIT
                )
                channel = (
                    Channel.ECOMMERCE
                    if "ecommerce" in text.lower() or "online" in text.lower()
                    else Channel.CARD_PRESENT
                )

                rules.append(
                    InterchangeRule(
                        id=f"reg_{document_id}_{page}_{i}",
                        brand=Brand.VISA
                        if "visa" in text.lower()
                        else Brand.MASTERCARD,
                        document_id=document_id,
                        source_page=page,
                        source_excerpt=text[:200],
                        product_type=product,
                        transaction_type=TransactionType.PURCHASE,
                        channel=channel,
                        rate_percent=float(rate),
                        fixed_fee=0.0,
                        confidence_score=0.6,
                        extraction_method=ExtractionMethod.REGEX,
                    )
                )
        return rules
