import asyncio
import os
import time
import torch  # noqa: F401
import chromadb  # noqa: F401
import chromadb_rust_bindings  # noqa: F401
import chainlit as cl
from chainlit.input_widget import Select, Switch

# Otimização de memória PyTorch
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

from app.core.config import settings
from app.core.llm import LocalLLM
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import VectorStore
from app.retrieval.rag_service import RAGService
from app.core.logging import logger

# Recursos carregados globalmente para evitar recarga no "New chat"
_resources = {}


def clear_vram():
    """Libera memória da GPU de forma agressiva."""
    import gc

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()


def load_resources(model_name: str, use_gpu: bool):
    """Inicializa os componentes pesados da POC."""
    global _resources

    # Se já houver recursos, limpa antes de carregar novos (evita acúmulo de VRAM)
    if _resources:
        logger.info("Clearing existing resources before reload...")
        _resources = {}
        clear_vram()

    logger.info(f"Loading resources for {model_name} with use_gpu={use_gpu}")

    # Atualiza configurações dinamicamente com base no modelo selecionado
    settings.LLM_USE_GPU = use_gpu

    if "Qwen" in model_name:
        settings.LLM_MODEL_PATH = os.path.join(
            settings.BASE_DIR, "models", "qwen2.5-1.5b-instruct-q4_k_m.gguf"
        )
        settings.LLM_TEMPLATE = "qwen"
    elif "E4B" in model_name:
        settings.LLM_MODEL_PATH = os.path.join(
            settings.BASE_DIR, "models", "gemma-4-E4B-it-Q4_K_M.gguf"
        )
        settings.LLM_TEMPLATE = "gemma"
    elif "26B" in model_name:
        settings.LLM_MODEL_PATH = os.path.join(
            settings.BASE_DIR, "models", "gemma-4-26B-A4B-it-UD-Q4_K_M.gguf"
        )
        settings.LLM_TEMPLATE = "gemma"

    embedding_service = EmbeddingService()
    vector_store = VectorStore()

    llm = LocalLLM(use_gpu=use_gpu)
    rag_service = RAGService(embedding_service, vector_store, llm)

    return {"rag_service": rag_service, "llm": llm}


@cl.on_chat_start
async def on_chat_start():
    # Configurações iniciais na barra lateral
    chat_settings = await cl.ChatSettings(
        [
            Select(
                id="model",
                label="Modelo LLM",
                values=["Qwen 2.5 (1.5B)", "Gemma 4 (E4B)", "Gemma 4 (26B)"],
                initial_index=0,
            ),
            Switch(id="use_gpu", label="Usar GPU", initial=settings.LLM_USE_GPU),
        ]
    ).send()

    await setup_system(chat_settings)


async def setup_system(chat_settings):
    global _resources

    msg = cl.Message(content="🔄 Inicializando motor de IA e base vetorial...")
    await msg.send()

    try:
        # Carrega recursos em thread separada
        _resources = await asyncio.to_thread(
            load_resources, chat_settings["model"], chat_settings["use_gpu"]
        )

        msg.content = (
            "✅ Sistema pronto! Como posso ajudar com as taxas de intercâmbio hoje?"
        )
        await msg.update()
    except Exception as e:
        msg.content = f"❌ Erro ao carregar sistema: {str(e)}"
        await msg.update()


@cl.on_settings_update
async def on_settings_update(chat_settings):
    await setup_system(chat_settings)


@cl.on_message
async def main(message: cl.Message):
    rag_service = _resources.get("rag_service")

    if not rag_service:
        await cl.Message(content="⚠️ Sistema não inicializado corretamente.").send()
        return

    msg = cl.Message(content="")
    await msg.send()

    start_time = time.time()

    # Executa a consulta RAG
    result = await asyncio.to_thread(rag_service.query, message.content)

    elapsed_time = time.time() - start_time

    # Prepara o "Backstage" com evidências
    elements = []
    backstage_content = f"### Pergunta: {message.content}\n\n"
    backstage_content += "#### 📊 Estatísticas de Execução\n"
    backstage_content += f"**Tempo de resposta:** {elapsed_time:.2f}s\n"
    
    tokens = result.get("tokens", {})
    backstage_content += f"**Tokens (Prompt):** {tokens.get('prompt', 0)}\n"
    backstage_content += f"**Tokens (Resposta):** {tokens.get('completion', 0)}\n"
    backstage_content += f"**Tokens (Total):** {tokens.get('total', 0)}\n\n"
    
    backstage_content += "#### Análise de RAG\n"
    chunks = result.get("retrieved_chunks", [])
    if chunks:
        backstage_content += "#### 📚 Evidências Documentais Encontradas:\n"
        for i, chunk in enumerate(chunks):
            doc_id = chunk["metadata"].get("document_id", "N/A")
            page = chunk["metadata"].get("page", "?")
            backstage_content += (
                f"**[{i + 1}] {doc_id} (Pág. {page})**\n{chunk['text']}\n\n"
            )
    else:
        backstage_content += "⚠️ Nenhuma evidência encontrada no banco vetorial.\n"

    elements.append(
        cl.Text(name="🔙 BACKSTAGE", content=backstage_content, display="side")
    )

    msg.content = result.get("answer", "Não foi possível gerar uma resposta.")
    msg.elements = elements
    await msg.update()
