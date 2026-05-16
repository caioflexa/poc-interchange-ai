import logging
import sys
from app.core.config import settings


def setup_logging():
    # Configuração centralizada de logs para o console
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger("interchange-ai")


logger = setup_logging()
