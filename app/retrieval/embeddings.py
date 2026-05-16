import os
from sentence_transformers import SentenceTransformer
from app.core.config import settings


class EmbeddingService:
    # Serviço para geração de vetores densos (embeddings) de texto
    def __init__(self):
        # Carrega o modelo de embeddings da pasta local ou cache
        # Forçamos o uso de CPU para economizar VRAM para o LLM e Reranker
        model_path = os.path.join(settings.BASE_DIR, "models")
        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL, cache_folder=model_path, device="cpu"
        )

    def encode(self, texts: list[str]):
        # Transforma uma lista de textos em uma matriz de embeddings
        return self.model.encode(texts)
