from enum import Enum


class Brand(str, Enum):
    # Bandeiras de cartão suportadas
    VISA = "Visa"
    MASTERCARD = "Mastercard"
    UNKNOWN = "Unknown"


class ProductType(str, Enum):
    # Tipos de produto financeiro
    CREDIT = "credit"
    DEBIT = "debit"
    PREPAID = "prepaid"
    UNKNOWN = "unknown"


class TransactionType(str, Enum):
    # Tipos de transação de pagamento
    PURCHASE = "purchase"
    INSTALLMENT = "installment"
    CASH_WITHDRAWAL = "cash_withdrawal"
    REFUND = "refund"
    UNKNOWN = "unknown"


class Channel(str, Enum):
    # Canais onde a transação ocorre
    CARD_PRESENT = "card_present"
    CARD_NOT_PRESENT = "card_not_present"
    ECOMMERCE = "ecommerce"
    CONTACTLESS = "contactless"
    OTHER = "other"
    UNKNOWN = "unknown"


class ExtractionMethod(str, Enum):
    # Métodos utilizados para extrair a regra do documento
    REGEX = "regex"
    TABLE_PARSER = "table_parser"
    LLM = "llm"
    MANUAL_SEED = "manual_seed"
    MOCK = "mock"
