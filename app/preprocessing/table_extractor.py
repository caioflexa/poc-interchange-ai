import pdfplumber
from app.core.logging import logger


class TableExtractor:
    # Classe para extração de tabelas de arquivos PDF
    @staticmethod
    def extract_from_pdf(file_path: str):
        # Utiliza pdfplumber para identificar e extrair estruturas tabulares
        tables = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    for table in page_tables:
                        tables.append({"page": i + 1, "data": table})
        except Exception as e:
            logger.error(f"Error extracting tables from {file_path}: {e}")
        return tables
