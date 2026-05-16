import json
from typing import List
from app.core.llm import LocalLLM
from app.core.config import settings
from app.domain.schemas import InterchangeRule
from app.domain.enums import (
    Brand,
    ProductType,
    TransactionType,
    Channel,
    ExtractionMethod,
)
from app.extraction.prompts import get_extraction_prompt
from app.core.logging import logger


class LLMExtractor:
    def __init__(self, llm: LocalLLM = None):
        self.llm = llm or LocalLLM()

    def _map_enum(self, value: str, enum_class, default):
        """Mapeia uma string para um valor de Enum de forma resiliente."""
        if not value:
            return default
        
        val_clean = str(value).lower().strip()
        for member in enum_class:
            if member.value.lower() == val_clean:
                return member
        return default

    def _sanitize_item(self, item: dict) -> dict:
        """Tenta corrigir e normalizar um item extraído pela IA antes da validação."""
        # Se a IA trocou canal por tipo de produto
        prod_val = str(item.get("product_type", "")).lower()
        chan_val = str(item.get("channel", "")).lower()
        
        # Correção de contaminação cruzada
        if "contactless" in prod_val or "aproximação" in prod_val:
            item["channel"] = "contactless"
            item["product_type"] = "unknown"
        elif "ecommerce" in prod_val or "online" in prod_val:
            item["channel"] = "ecommerce"
            item["product_type"] = "unknown"
            
        # Mapeamento de Brand
        brand_str = str(item.get("brand", "")).lower()
        if "master" in brand_str:
            item["brand"] = Brand.MASTERCARD
        elif "visa" in brand_str:
            item["brand"] = Brand.VISA
        else:
            item["brand"] = Brand.UNKNOWN

        # Mapeamento seguro de outros enums
        item["product_type"] = self._map_enum(item.get("product_type"), ProductType, ProductType.UNKNOWN)
        item["transaction_type"] = self._map_enum(item.get("transaction_type"), TransactionType, TransactionType.PURCHASE)
        item["channel"] = self._map_enum(item.get("channel"), Channel, Channel.OTHER)
        
        # Garantia de tipos numéricos
        try:
            item["rate_percent"] = float(str(item.get("rate_percent", "0")).replace("%", "").strip())
        except (ValueError, TypeError):
            item["rate_percent"] = 0.0
            
        try:
            item["fixed_fee"] = float(str(item.get("fixed_fee", "0")).replace("$", "").replace("BRL", "").strip())
        except (ValueError, TypeError):
            item["fixed_fee"] = 0.0
            
        return item

    def extract_from_text(
        self, text: str, document_id: str, page: int
    ) -> List[InterchangeRule]:
        prompt = get_extraction_prompt(settings.LLM_TEMPLATE, text)
        response_text = self.llm.generate(prompt)

        if not response_text or not response_text.strip():
            logger.warning(f"LLM returned empty response for {document_id} page {page}")
            return []

        try:
            # Tenta encontrar o JSON se houver lixo em volta
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1
            if json_start != -1 and json_end != -1:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
            else:
                # Tenta como objeto único e converte para lista
                try:
                    data = json.loads(response_text)
                    if isinstance(data, dict):
                        data = [data]
                except json.JSONDecodeError:
                    return []

            if not isinstance(data, list):
                return []

            rules = []
            for i, raw_item in enumerate(data):
                try:
                    # Aplica a sanitização robusta
                    item = self._sanitize_item(raw_item)
                    
                    rule = InterchangeRule(
                        id=f"llm_{document_id}_{page}_{i}",
                        brand=item["brand"],
                        document_id=document_id,
                        source_page=page,
                        source_excerpt=text[:500],
                        product_type=item["product_type"],
                        transaction_type=item["transaction_type"],
                        channel=item["channel"],
                        merchant_segment=item.get("merchant_segment", "General"),
                        rate_percent=item["rate_percent"],
                        fixed_fee=item["fixed_fee"],
                        currency=item.get("currency", "BRL"),
                        conditions=item.get("conditions"),
                        confidence_score=0.85,
                        extraction_method=ExtractionMethod.LLM,
                    )
                    rules.append(rule)
                except Exception as e:
                    logger.warning(f"Error validating rule item: {e}")

            return rules

        except Exception as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return []
