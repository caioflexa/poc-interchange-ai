import os
from pypdf import PdfReader
from docx import Document
from app.core.logging import logger


class DocumentLoader:
    # Classe responsável por carregar diferentes formatos de arquivos
    @staticmethod
    def load(file_path: str):
        # Direciona o carregamento com base na extensão do arquivo
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return DocumentLoader._load_pdf(file_path)
        elif ext == ".docx":
            return DocumentLoader._load_docx(file_path)
        elif ext == ".txt":
            return DocumentLoader._load_txt(file_path)
        else:
            logger.warning(f"Unsupported file extension: {ext}")
            return []

    @staticmethod
    def _load_pdf(file_path: str):
        # Extrai texto de PDFs página por página
        pages = []
        try:
            reader = PdfReader(file_path)
            for i, page in enumerate(reader.pages):
                pages.append({"page": i + 1, "text": page.extract_text()})
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {e}")
        return pages

    @staticmethod
    def _load_docx(file_path: str):
        # Extrai texto de arquivos Word (.docx)
        try:
            doc = Document(file_path)
            full_text = [para.text for para in doc.paragraphs]
            return [{"page": 1, "text": "\n".join(full_text)}]
        except Exception as e:
            logger.error(f"Error loading DOCX {file_path}: {e}")
            return []

    @staticmethod
    def _load_txt(file_path: str):
        # Extrai texto de arquivos de texto simples (.txt)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return [{"page": 1, "text": f.read()}]
        except Exception as e:
            logger.error(f"Error loading TXT {file_path}: {e}")
            return []
