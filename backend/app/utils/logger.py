import logging
import sys
from ..config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(settings.PROJECT_NAME)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
