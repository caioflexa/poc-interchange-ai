from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import VectorStore
from app.core.llm import LocalLLM
from app.core.config import settings
from app.retrieval.prompts import get_rag_prompt, get_expansion_prompt
from app.core.logging import logger
from sentence_transformers import CrossEncoder
import os


class RAGService:
    # Orquestrador de busca e geração aumentada por recuperação (RAG)
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
        llm: LocalLLM,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm = llm

        # Inicializa o Reranker (Cross-Encoder)
        model_path = os.path.join(settings.BASE_DIR, "models")
        logger.info(f"Loading Reranker: {settings.RERANKER_MODEL}")
        self.reranker = CrossEncoder(settings.RERANKER_MODEL, cache_folder=model_path)

    def query(self, question: str):
        total_prompt_tokens = 0
        total_completion_tokens = 0

        # 1. Expansão de Consulta: Gera variações da pergunta para capturar mais contexto
        logger.info(f"Expanding query for: {question}")
        expansion_prompt = get_expansion_prompt(settings.LLM_TEMPLATE, question)
        expansion_res = self.llm.generate_with_usage(expansion_prompt)
        expansion_output = expansion_res["text"]
        
        total_prompt_tokens += expansion_res["prompt_tokens"]
        total_completion_tokens += expansion_res["completion_tokens"]

        # Limpa e extrai as variações (cada linha vira uma query)
        variations = [
            v.strip("- ").strip() for v in expansion_output.split("\n") if v.strip()
        ]
        queries = [question] + variations[:3]  # Original + até 3 variações

        logger.info(f"Total queries to execute: {queries}")

        # 2. Busca Inicial (Recuperação Bruta)
        where_filter = None
        q_lower = question.lower()
        if "visa" in q_lower:
            where_filter = {"brand": "Visa"}
        elif "mastercard" in q_lower:
            where_filter = {"brand": "Mastercard"}

        raw_candidates = []
        seen_ids = set()

        for q in queries:
            query_embedding = self.embedding_service.encode([q])[0]
            # Busca um número maior de candidatos para o Reranker filtrar
            results = self.vector_store.search(
                query_embedding, n_results=15, where=where_filter
            )

            if results["documents"]:
                for i in range(len(results["documents"][0])):
                    doc_id = results["ids"][0][i]
                    if doc_id not in seen_ids:
                        seen_ids.add(doc_id)
                        raw_candidates.append(
                            {
                                "text": results["documents"][0][i],
                                "metadata": results["metadatas"][0][i],
                            }
                        )

        if not raw_candidates:
            return {
                "question": question,
                "answer": "Não encontrei essa informação nos documentos carregados.",
                "retrieved_chunks": [],
                "tokens": {
                    "prompt": total_prompt_tokens,
                    "completion": total_completion_tokens,
                    "total": total_prompt_tokens + total_completion_tokens
                }
            }

        # 3. Reranking: O Cross-Encoder reordena os candidatos por relevância real
        logger.info(f"Reranking {len(raw_candidates)} candidates...")
        sentence_pairs = [[question, c["text"]] for c in raw_candidates]
        scores = self.reranker.predict(sentence_pairs)

        # Adiciona o score aos candidatos e ordena
        for i, candidate in enumerate(raw_candidates):
            candidate["rerank_score"] = float(scores[i])

        # Ordena do maior score para o menor
        ranked_candidates = sorted(
            raw_candidates, key=lambda x: x["rerank_score"], reverse=True
        )

        # Seleciona o Top-5 final após o Reranking para o LLM
        final_results = ranked_candidates[:5]

        # 4. Geração da Resposta
        context_parts = []
        retrieved_chunks = []
        for res in final_results:
            metadata = res["metadata"]
            retrieved_chunks.append(res)
            context_parts.append(
                f"[Documento: {metadata['document_id']}, Página: {metadata['page']}, Score: {res['rerank_score']:.2f}]\n{res['text']}"
            )

        context_str = "\n---\n".join(context_parts)

        prompt = get_rag_prompt(settings.LLM_TEMPLATE, question, context_str)
        answer_res = self.llm.generate_with_usage(prompt)
        answer = answer_res["text"]

        total_prompt_tokens += answer_res["prompt_tokens"]
        total_completion_tokens += answer_res["completion_tokens"]

        return {
            "question": question,
            "answer": answer,
            "retrieved_chunks": retrieved_chunks,
            "tokens": {
                "prompt": total_prompt_tokens,
                "completion": total_completion_tokens,
                "total": total_prompt_tokens + total_completion_tokens
            }
        }
