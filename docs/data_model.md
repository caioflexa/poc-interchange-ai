# Data Model - Interchange AI POC

## Entidades Principais

### Document (Relacional)
*   `id`: Nome do arquivo.
*   `brand`: Visa ou Mastercard.
*   `title`: Título amigável.
*   `doc_type`: tarifário ou normativo.
*   `file_path`: Caminho local.
*   `pages_count`: Total de páginas.

### InterchangeRule (Relacional)
*   `id`: Identificador único (ext_... para extraídas, syn_... para sintéticas).
*   `brand`: Bandeira.
*   `product_type`: credit, debit, prepaid.
*   `transaction_type`: purchase, installment, cash_withdrawal.
*   `channel`: card_present, ecommerce, etc.
*   `rate_percent`: Taxa percentual (ex: 1.5).
*   `fixed_fee`: Valor fixo (ex: 0.10).
*   `min_fee` / `max_fee`: Limites de taxa.
*   `confidence_score`: Nível de confiança da extração (0.0 a 1.0).

### Chunk (Vetorial)
*   `text`: Trecho do documento.
*   `metadata`: `document_id`, `page`.
*   `embedding`: Vetor denso (384 dimensões).
