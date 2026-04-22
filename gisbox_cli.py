import argparse
from pathlib import Path

from gisbox_common import get_logger, load_config
from gisbox_monitor import GISBoxMonitor
from gisbox_sync import GISBoxSync

logger = get_logger('GISBoxCLI')


def _check_config() -> int:
    config = load_config(Path(__file__).parent)
    logger.info('Configuración válida.')
    logger.info(f'  URL: {config.url}')
    logger.info(f'  Usuario: {config.username or "(perfil/anónimo)"}')
    logger.info(f'  Directorio local: {config.local_sync_dir}')
    return 0


def _sync_down() -> int:
    sync_tool = GISBoxSync()
    total = sync_tool.sync_down()
    logger.info(f'Sincronización finalizada. Elementos descargados: {total}')
    return 0


def _monitor() -> int:
    monitor = GISBoxMonitor()
    monitor.start_monitoring()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='gisbox',
        description='CLI MVP para sincronización ArcGIS ↔ directorio local',
    )

    subparsers = parser.add_subparsers(dest='command', required=True)
    subparsers.add_parser('check-config', help='Valida configuración de entorno (.env).')
    subparsers.add_parser('sync-down', help='Ejecuta sincronización de descarga desde ArcGIS.')
    subparsers.add_parser('monitor', help='Inicia monitorización y subida automática de cambios.')

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == 'check-config':
        return _check_config()
    if args.command == 'sync-down':
        return _sync_down()
    if args.command == 'monitor':
        return _monitor()

    parser.print_help()
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
