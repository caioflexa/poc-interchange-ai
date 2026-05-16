# Interchange AI POC

## Visão Geral
Esta Prova de Conceito (POC) demonstra uma arquitetura autônoma para extração e consulta de taxas de intercâmbio a partir de documentos públicos da Visa e Mastercard.

## Arquitetura
O projeto é focado em um motor de RAG (Retrieval-Augmented Generation) de alta precisão:
- **Ingestion**: Carregamento e processamento de PDFs/TXTs.
- **Persistence**: Armazenamento em banco relacional (SQLite) e vetorial (ChromaDB).
- **Retrieval**: Busca semântica avançada com Reranking e Expansão de Consulta.
- **Interface**: Chat interativo para consulta em linguagem natural.

## Requisitos de Sistema
O projeto oferece três perfis de execução, dependendo do hardware disponível:

1. **Perfil Econômico (Modelo 1.5B)**
   - **Modelo:** Qwen 2.5 (1.5B)
   - **Hardware:** CPU moderna (Intel i5/AMD Ryzen 5+) ou GPU básica (2GB-4GB VRAM).
   - **Memória RAM:** 8GB+.
   - **Uso:** Testes rápidos, desenvolvimento em laptops ou máquinas sem GPU dedicada.

2. **Perfil Equilibrado (Modelo E4B)**
   - **Modelo:** Gemma 4 (E4B)
   - **Hardware:** GPU NVIDIA (ex: RTX 3060/4060) com 8GB-12GB VRAM.
   - **Memória RAM:** 16GB+.
   - **Uso:** Uso geral com excelente equilíbrio entre velocidade e qualidade de raciocínio.

3. **Perfil Robusto (Modelo 26B)**
   - **Modelo:** Gemma 4 (26B)
   - **Hardware:** GPU NVIDIA RTX 3090 ou 4090 (mínimo 24GB VRAM recomendado).
   - **Memória RAM:** 32GB+.
   - **Uso:** Produção e extrações complexas onde a máxima precisão técnica é exigida.

**Requisitos Gerais de Software:**
- **Driver:** NVIDIA Driver v580+ com suporte a CUDA 12.4 (caso utilize GPU).
- **SO:** Linux (Ubuntu 22.04+ recomendado) ou Windows via WSL2.

## Funcionalidades de RAG Avançadas
Para garantir alta precisão em documentos técnicos financeiros, a POC utiliza:
- **Brand Metadata Filtering:** Identifica automaticamente se a pergunta refere-se a Visa ou Mastercard e filtra a base vetorial.
- **Query Expansion:** O LLM gera variações técnicas da pergunta (incluindo sinônimos e símbolos como "+" ou "%") para localizar dados exatos.
- **High-Precision Reranking (Cross-Encoder):** Utiliza o modelo `BAAI/bge-reranker-v2-m3` para re-analisar os candidatos e priorizar tabelas e taxas sobre textos jurídicos genéricos.
- **Gestão de VRAM:** Sistema otimizado para a RTX 4090, com limpeza agressiva de cache CUDA e offloading de modelos leves para CPU.

## Como Executar

### 1. Instalação
```bash
python3 -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
```

### 2. Configuração e Modelos
Configure o arquivo `.env`. É **importante** configurar:
- `LLM_USE_GPU`: `True` para ativar a aceleração por hardware (RTX 4090).

#### Download de Modelos
Execute o comando abaixo para baixar os Embeddings, Reranker e as 3 opções de LLM:
```bash
python scripts/download_models.py
```

### 3. Preparação dos Dados
> **Importante:** Se você já realizou uma ingestão anterior à implementação das funcionalidades de Reranking/Brand Filtering, limpe a pasta `data/vector_store/` e rode a ingestão novamente.

1.  **Documentos Reais (PDF/TXT):** Coloque os PDFs ou arquivos de texto das bandeiras nas pastas correspondentes:
    *   `data/raw/visa/`
    *   `data/raw/mastercard/`
2.  **Dados Sintéticos:** O arquivo `interchange_rules_sample.csv` deve estar em `data/synthetic/`.

### 4. Ingestão e Pipeline
```bash
# 1. Processa os documentos (vetorização e extração de chunks)
python scripts/ingest_documents.py

# 2. Carrega as regras base do CSV sintético
python scripts/load_synthetic_transactions.py

# 3. Executa a extração estruturada (converte chunks em regras no banco)
python scripts/extract_rules.py
```

### 5. Interface de Chat (Chainlit)
```bash
chainlit run chat_app.py --port 8080
```
*Monitore o painel **"🔙 BACKSTAGE"** na lateral do chat para auditar as fontes e os scores de relevância (Rerank Score).*

## Modelos de LLM Suportados

| Modelo | Template | Stop Tokens | Uso Recomendado |
| :--- | :--- | :--- | :--- |
| **Qwen2.5 (1.5B)** | `qwen` | `<|im_end|>`, `<|endoftext|>` | Máquinas com pouca RAM / CPU |
| **Gemma 4 (E4B)** | `gemma` | `<end_of_turn>`, `<start_of_turn>` | Equilíbrio entre performance e qualidade |
| **Gemma 4 (26B)** | `gemma` | `<end_of_turn>`, `<start_of_turn>` | Máquinas com GPU (VRAM > 16GB) |

## Diferenciais Técnicos
- **LLM Local:** Raciocínio real sem custos de API ou envio de dados para nuvem.
- **Auditabilidade:** Cada resposta cita obrigatoriamente a página, o documento fonte e o score de confiança.
- **Foco em Precisão:** Motor desenhado para vencer o "ruído" de documentos jurídicos longos.
