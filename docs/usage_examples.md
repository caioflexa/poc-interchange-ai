# Usage Examples - Interchange AI POC

## 1. Simulação de Transação

**Request:**
`POST /simulation`
```json
{
  "brand": "Visa",
  "amount": 200.0,
  "product_type": "credit",
  "transaction_type": "purchase",
  "channel": "ecommerce",
  "merchant_segment": "retail"
}
```

**Response:**
```json
{
  "matched_rule_id": "syn_Visa_retail_1",
  "brand": "Visa",
  "rate_percent": 1.8,
  "fixed_fee": 0.0,
  "estimated_interchange_fee": 3.6,
  "currency": "BRL",
  "confidence_score": 1.0,
  "source_document": null,
  "source_page": null,
  "notes": "Calculado usando regra syn_Visa_retail_1. Condições: Online retail rate"
}
```

## 2. Consulta RAG

**Request:**
`POST /rag/query`
```json
{
  "question": "Qual a taxa para supermercado na Visa?"
}
```

**Response:**
```json
{
  "question": "Qual a taxa para supermercado na Visa?",
  "answer": "Com base nos documentos consultados, aqui estão os trechos mais relevantes...",
  "retrieved_chunks": [
    {
      "text": "Credit Purchase Supermarket: 1.2%",
      "metadata": {
        "document_id": "visa_rules_dummy.txt",
        "page": 1
      }
    }
  ]
}
```
