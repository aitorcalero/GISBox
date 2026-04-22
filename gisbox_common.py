import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'


@dataclass(frozen=True)
class GISBoxConfig:
    url: str | None
    username: str | None
    password: str | None
    profile: str | None
    local_sync_dir: str


def load_config(base_dir: Path) -> GISBoxConfig:
    """Carga y valida configuración desde .env y variables de entorno."""
    load_dotenv(base_dir / '.env')

    local_sync_dir = os.getenv('LOCAL_SYNC_DIR')
    if not local_sync_dir:
        raise ValueError('LOCAL_SYNC_DIR no está configurado en el archivo .env')

    return GISBoxConfig(
        url=os.getenv('ARCGIS_URL'),
        username=os.getenv('ARCGIS_USERNAME'),
        password=os.getenv('ARCGIS_PASSWORD'),
        profile=os.getenv('ARCGIS_PROFILE'),
        local_sync_dir=local_sync_dir,
    )


def get_logger(name: str) -> logging.Logger:
    """Devuelve un logger con configuración homogénea para todo GISBox."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT))
        logger.addHandler(handler)

    return logger
