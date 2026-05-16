import re


class TextCleaner:
    # Classe utilitária para normalização de texto
    @staticmethod
    def clean(text: str) -> str:
        # Remove espaços excessivos e limpa as bordas do texto
        if not text:
            return ""
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        return text
