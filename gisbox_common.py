import logging
import os
from dataclasses import dataclass
from pathlib import Path

from arcgis.gis import GIS

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'


@dataclass(frozen=True)
class GISBoxConfig:
    url: str | None
    username: str | None
    password: str | None
    profile: str | None
    local_sync_dir: str


def load_dotenv(dotenv_path: Path) -> None:
    """Carga un archivo .env sencillo en os.environ sin sobrescribir variables existentes."""
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue

        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


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


def connect_to_arcgis(config: GISBoxConfig) -> GIS:
    """Establece conexión a ArcGIS priorizando perfil sobre credenciales directas."""
    if config.profile:
        return GIS(profile=config.profile)
    if config.username and config.password:
        return GIS(config.url, config.username, config.password)
    return GIS(config.url)


def get_logger(name: str) -> logging.Logger:
    """Devuelve un logger con configuración homogénea para todo GISBox."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT))
        logger.addHandler(handler)

    return logger
