import chromadb
from app.core.config import settings
import os


class VectorStore:
    # Gerencia o banco de dados vetorial para busca semântica
    def __init__(self):
        # Inicializa o cliente ChromaDB persistente com mecanismo de retry para os bindings Rust
        from app.core.logging import logger
        import time

        logger.info(f"Initializing VectorStore at {settings.VECTOR_DB_PATH}")
        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)

        max_retries = 3
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                self.client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
                # Força a inicialização dos bindings acessando um método simples
                self.client.heartbeat()
                logger.info("ChromaDB PersistentClient created and heartbeat verified")

                self.collection = self.client.get_or_create_collection(
                    "document_chunks"
                )
                logger.info("ChromaDB collection 'document_chunks' ready")
                return  # Sucesso
            except (AttributeError, Exception) as e:
                if "bindings" in str(e) or isinstance(e, AttributeError):
                    logger.warning(
                        f"ChromaDB bindings not ready (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                    if attempt == max_retries - 1:
                        logger.error(
                            "Failed to initialize ChromaDB after multiple attempts."
                        )
                        raise e
                else:
                    logger.error(f"Failed to initialize VectorStore: {str(e)}")
                    raise e

    def add_chunks(self, chunks: list[dict], embeddings: list):
        # Adiciona fragmentos de texto e seus respectivos vetores à coleção
        ids = [f"{c['document_id']}_{c['page']}_{c['chunk_index']}" for c in chunks]
        metadatas = [
            {
                "document_id": c["document_id"],
                "page": c["page"],
                "brand": c.get("brand", "Unknown"),
            }
            for c in chunks
        ]
        documents = [c["text"] for c in chunks]

        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist()
            if hasattr(embeddings, "tolist")
            else embeddings,
            metadatas=metadatas,
            documents=documents,
        )

    def search(self, query_embedding: list, n_results: int = 15, where: dict = None):
        # Realiza uma busca por similaridade de cosseno na base vetorial
        query_params = {
            "query_embeddings": query_embedding.tolist()
            if hasattr(query_embedding, "tolist")
            else [query_embedding],
            "n_results": n_results,
        }

        if where:
            query_params["where"] = where

        results = self.collection.query(**query_params)
        return results
