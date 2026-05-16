from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # Definição dinâmica dos caminhos base do projeto
    BASE_DIR: str = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    RAW_DATA_DIR: str = os.path.join(DATA_DIR, "raw")
    SYNTHETIC_DATA_DIR: str = os.path.join(DATA_DIR, "synthetic")

    # Configurações básicas da POC
    PROJECT_NAME: str = "Interchange AI POC"
    DATABASE_URL: str = f"sqlite:///{os.path.join(DATA_DIR, 'interchange.db')}"
    VECTOR_DB_PATH: str = os.path.join(DATA_DIR, "vector_store")
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"
    LOG_LEVEL: str = "INFO"

    # Configurações de LLM Local (Llama-cpp)
    LLM_MODEL_PATH: str = os.path.join(
        BASE_DIR, "models", "qwen2.5-1.5b-instruct-q4_k_m.gguf"
    )
    LLM_TEMPLATE: str = "qwen"  # gemma ou qwen
    LLM_N_CTX: int = 8192
    LLM_MAX_TOKENS: int = 2048
    LLM_TEMPERATURE: float = 0.1
    LLM_N_THREADS: int = 4
    LLM_USE_GPU: bool = False
    LLM_STOP_TOKENS: list[str] = ["<|im_end|>", "<|endoftext|>"]

    class Config:
        env_file = ".env"


settings = Settings()
