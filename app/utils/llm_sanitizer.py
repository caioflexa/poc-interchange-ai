import re


class LLMSanitizer:
    """
    Utilitário para higienizar o texto gerado por Large Language Models (LLMs).
    Remove tokens internos de controle que podem vazar em alguns GGUFs.
    """

    def sanitize(self, text: str) -> str:
        text = text.strip()

        # Remove padrões de pensamento/canal
        text = re.sub(
            r"(?is)<\|?channel\|?>\s*"
            r"(thought|analysis|tool|tool_use|commentary|final|assistant|model)?\s*"
            r"<\|?channel\|?>",
            "",
            text,
        )

        # Remove tags soltas remanescentes.
        text = re.sub(
            r"(?is)</?start_of_turn>|</?end_of_turn>|<\|?channel\|?>", "", text
        )

        # Remove rótulos residuais no início
        text = re.sub(
            r"(?is)^\s*(thought|analysis|tool|tool_use|commentary|final|assistant|model)\s*[:\-]?\s*",
            "",
            text,
        )

        return text.strip()
