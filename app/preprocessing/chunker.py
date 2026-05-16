from typing import List, Dict


class Chunker:
    # Classe responsável por dividir o texto em pedaços menores (chunks)
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def create_chunks(self, pages: List[Dict]) -> List[Dict]:
        # Divide o texto das páginas respeitando o tamanho e sobreposição definidos
        chunks = []
        for page_data in pages:
            text = page_data["text"]
            page_num = page_data["page"]

            if not text:
                continue

            start = 0
            idx = 0
            while start < len(text):
                end = start + self.chunk_size
                chunk_text = text[start:end]
                chunks.append(
                    {"page": page_num, "text": chunk_text, "chunk_index": idx}
                )
                start += self.chunk_size - self.chunk_overlap
                idx += 1
        return chunks
