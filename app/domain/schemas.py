from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.domain.enums import (
    Brand,
    ProductType,
    TransactionType,
    Channel,
    ExtractionMethod,
)


class InterchangeRule(BaseModel):
    # Entidade estruturada que representa uma regra de intercâmbio
    id: Optional[str] = None
    brand: Brand
    document_id: Optional[str] = None
    source_page: Optional[int] = None
    source_excerpt: Optional[str] = None
    product_type: ProductType = ProductType.UNKNOWN
    transaction_type: TransactionType = TransactionType.UNKNOWN
    channel: Channel = Channel.UNKNOWN
    merchant_segment: Optional[str] = "General"
    mcc: Optional[str] = None
    rate_percent: float = 0.0
    fixed_fee: float = 0.0
    min_fee: Optional[float] = None
    max_fee: Optional[float] = None
    currency: str = "BRL"
    conditions: Optional[str] = None
    effective_date: Optional[str] = None
    confidence_score: float = 1.0
    extraction_method: ExtractionMethod = ExtractionMethod.MOCK
    created_at: datetime = Field(default_factory=datetime.now)


class Transaction(BaseModel):
    # Dados de entrada para uma simulação de intercâmbio
    transaction_id: Optional[str] = None
    brand: Brand
    amount: float
    product_type: ProductType
    transaction_type: TransactionType
    channel: Channel
    merchant_segment: str = "General"
    installments: int = 1
    contactless: bool = False
    prepaid: bool = False


class SimulationResult(BaseModel):
    # Resultado detalhado do cálculo de intercâmbio
    matched_rule_id: Optional[str]
    brand: Brand
    rate_percent: float
    fixed_fee: float
    estimated_interchange_fee: float
    currency: str
    confidence_score: float
    source_document: Optional[str]
    source_page: Optional[int]
    notes: str
