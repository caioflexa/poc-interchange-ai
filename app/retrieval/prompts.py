_RAG_SYSTEM_PROMPT = """
Você é um assistente especializado em regras de taxas de intercâmbio da Visa e Mastercard.
Seu objetivo é responder perguntas de usuários com base nos trechos de documentos (CONTEXTO) fornecidos.

Regras de resposta:
1. Use APENAS as informações presentes no CONTEXTO.
2. Se a resposta não estiver no contexto, diga: "Não encontrei essa informação nos documentos carregados."
3. Cite sempre a página e o documento de origem ao fornecer uma informação.
4. Seja direto, técnico e preciso.
5. Responda em Português do Brasil.
"""


def get_rag_prompt(template: str, question: str, context: str) -> str:
    user_content = (
        f"CONTEXTO DOS DOCUMENTOS:\n{context}\n\nPERGUNTA DO USUÁRIO:\n{question}"
    )

    if template == "gemma":
        return (
            f"<start_of_turn>user\n{_RAG_SYSTEM_PROMPT}\n\n{user_content}<end_of_turn>\n"
            f"<start_of_turn>model\n"
        )

    return (
        f"<|im_start|>system\n{_RAG_SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{user_content}<|im_end|>\n<|im_start|>assistant\n"
    )


_EXPANSION_SYSTEM_PROMPT = """
Você é um especialista em busca de documentos financeiros.
Sua tarefa é gerar 3 variações técnicas e curtas da pergunta do usuário para melhorar a busca em um banco de dados.
Gere variações que foquem em termos técnicos, sinônimos e símbolos (como %, +, BRL).

Exemplo:
Entrada: "Qual o valor fixo da Mastercard?"
Saída:
- taxa fixa mastercard interchange
- mastercard fixed fee +
- valores fixos intercâmbio mastercard

Responda APENAS com as variações, uma por linha, sem numeração ou explicações.
"""


def get_expansion_prompt(template: str, question: str) -> str:
    if template == "gemma":
        return f"<start_of_turn>user\n{_EXPANSION_SYSTEM_PROMPT}\n\nPergunta: {question}<end_of_turn>\n<start_of_turn>model\n"

    return (
        f"<|im_start|>system\n{_EXPANSION_SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\nPergunta: {question}<|im_end|>\n<|im_start|>assistant\n"
    )
