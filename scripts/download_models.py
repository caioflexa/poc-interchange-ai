import os
import sys
from huggingface_hub import hf_hub_download
from sentence_transformers import SentenceTransformer, CrossEncoder

# Adiciona a raiz do projeto ao sys.path para permitir a importação do pacote 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.config import settings


def download_embedding_model():
    """Faz o download do modelo de embedding definido nas configurações."""
    model_name = settings.EMBEDDING_MODEL
    print(f"\n--- Baixando modelo de embedding: {model_name} ---")

    # Define e cria o caminho local para salvar o modelo
    model_path = os.path.join(settings.BASE_DIR, "models")
    os.makedirs(model_path, exist_ok=True)

    # Inicializa o modelo forçando o salvamento na pasta local do projeto
    SentenceTransformer(model_name, cache_folder=model_path)
    print("Modelo de embedding salvo em models/")


def download_reranker_model():
    """Faz o download do modelo de reranker definido nas configurações."""
    model_name = settings.RERANKER_MODEL
    print(f"\n--- Baixando modelo de Reranker: {model_name} ---")

    model_path = os.path.join(settings.BASE_DIR, "models")
    os.makedirs(model_path, exist_ok=True)

    # CrossEncoder baixa o modelo se não encontrar no cache
    CrossEncoder(model_name, cache_folder=model_path)
    print("Modelo de reranker salvo em models/")


def download_llm_models():
    """Faz o download dos modelos de LLM suportados (formato GGUF) conforme llm_config_prompt.md."""
    models = [
        {
            "repo_id": "Qwen/Qwen2.5-1.5B-Instruct-GGUF",
            "filename": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
            "description": "Qwen 2.5 1.5B",
        },
        {
            "repo_id": "unsloth/gemma-4-E4B-it-GGUF",
            "filename": "gemma-4-E4B-it-Q4_K_M.gguf",
            "description": "Gemma 4 E4B",
        },
        {
            "repo_id": "unsloth/gemma-4-26B-A4B-it-GGUF",
            "filename": "gemma-4-26B-A4B-it-UD-Q4_K_M.gguf",
            "description": "Gemma 4 26B",
        },
    ]

    print("\n--- Baixando modelos de LLM (GGUF) ---")
    models_dir = os.path.join(settings.BASE_DIR, "models")
    os.makedirs(models_dir, exist_ok=True)

    for m in models:
        print(f"Baixando {m['description']}...")
        try:
            hf_hub_download(
                repo_id=m["repo_id"],
                filename=m["filename"],
                local_dir=models_dir,
                token=os.environ.get("HF_TOKEN"),
            )
            print(f"Sucesso: {m['filename']} salvo em models/")
        except Exception as e:
            print(
                f"Aviso: Não foi possível baixar {m['filename']}. Verifique se o repo existe. Erro: {e}"
            )


if __name__ == "__main__":
    download_embedding_model()
    download_reranker_model()
    download_llm_models()
    print("\nProcesso de download concluído!")
