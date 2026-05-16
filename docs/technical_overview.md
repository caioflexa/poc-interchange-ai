# Technical Overview - Interchange AI POC

## Pipeline de Dados
O pipeline foi projetado para ser modular e extensível:

1.  **Ingestão**: Suporta PDF, DOCX e TXT. Registra metadados do documento no SQLite.
2.  **Pré-processamento**: Limpa o texto e divide em chunks de tamanho fixo com sobreposição. Extrai tabelas usando `pdfplumber`.
3.  **Vetorização**: Gera embeddings para cada chunk usando o modelo `paraphrase-multilingual-MiniLM-L12-v2` da Sentence Transformers.
4.  **Armazenamento Vetorial**: Chunks e embeddings são salvos no ChromaDB para busca semântica rápida.
5.  **Extração de Regras**:
    *   **Híbrida**: Combina Regex para padrões simples e **LLM Local (GGUF)** para extração semântica complexa.
    *   O motor de extração converte trechos de manuais em objetos `InterchangeRule` validados por schema Pydantic.
    *   Classifica automaticamente atributos como bandeira, tipo de produto e canal via prompt engineering especializado.
6.  **Simulação**: Recebe uma transação e busca a regra mais específica na base. Aplica o cálculo e retorna o valor estimado do intercâmbio.
7.  **RAG (Retrieval-Augmented Generation)**:
    *   Permite consultas em linguagem natural.
    *   Recupera chunks contextuais do ChromaDB.
    *   O LLM redige a resposta fundamentada, citando as fontes (Auditabilidade).

## Escolhas Arquiteturais
*   **FastAPI**: Escolhido pela performance e facilidade de documentação (Swagger).
*   **Chainlit**: Interface gráfica reativa para demonstração do assistente de IA.
*   **Llama-cpp-python**: Backend de inferência para rodar LLMs localmente em hardware comum (CPU ou GPU).
*   **SQLite + ChromaDB**: Combinação ideal para POCs locais, separando dados relacionais de dados não estruturados/vetoriais.
*   **Pydantic**: Garante a integridade dos dados em todas as camadas.
*   **Clean Architecture**: Facilita a substituição de componentes (ex: trocar Regex por um LLM real no futuro).
