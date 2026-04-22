import os
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from gisbox_common import connect_to_arcgis, get_logger, load_config

logger = get_logger('GISBoxMonitor')

class UploadHandler(FileSystemEventHandler):
    """
    Maneja los eventos del sistema de archivos (creación, modificación, eliminación)
    para sincronizar los cambios con ArcGIS Online/Enterprise.
    """
    def __init__(self, gis, local_sync_dir):
        self.gis = gis
        self.local_sync_dir = Path(local_sync_dir)
        self.user = self.gis.users.me
        logger.info(f"Monitorizando cambios en: {self.local_sync_dir}")

    def _get_arcgis_folder(self, src_path):
        """
        Determina la carpeta de ArcGIS Online/Enterprise a partir de la ruta local.
        """
        relative_path = Path(src_path).relative_to(self.local_sync_dir)
        if len(relative_path.parts) > 1:
            return relative_path.parts[0]
        return None # Carpeta raíz

    def _upload_file(self, src_path):
        """
        Sube o actualiza un archivo a ArcGIS Online/Enterprise.
        """
        file_path = Path(src_path)
        if file_path.is_file():
            folder_name = self._get_arcgis_folder(src_path)
            
            # Propiedades básicas del elemento
            item_properties = {
                'title': file_path.stem,
                'tags': 'gisbox, sync',
                'type': 'File' # Tipo genérico, la API lo inferirá
            }
            
            # Buscar si el elemento ya existe
            search_query = f'title:"{file_path.stem}" AND owner:{self.user.username}'
            if folder_name:
                search_query += f' AND folder:{folder_name}'
                
            existing_items = self.gis.content.search(query=search_query, max_items=1)
            
            if existing_items:
                # Actualizar elemento existente
                item = existing_items[0]
                logger.info(f"  [ACTUALIZANDO] {item.title}...")
                item.update(item_properties=item_properties, data=src_path)
                logger.info(f"  [ACTUALIZADO] {item.title} en ArcGIS.")
            else:
                # Añadir nuevo elemento
                logger.info(f"  [SUBIENDO] Nuevo archivo: {file_path.name}...")
                item = self.gis.content.add(item_properties=item_properties, data=src_path, folder=folder_name)
                logger.info(f"  [SUBIDO] {item.title} a ArcGIS.")

    def _delete_item(self, src_path):
        """
        Elimina un elemento de ArcGIS Online/Enterprise.
        """
        file_path = Path(src_path)
        if not file_path.is_file():
            # Solo manejamos archivos, no carpetas
            return
            
        folder_name = self._get_arcgis_folder(src_path)
        
        # Buscar el elemento a eliminar
        search_query = f'title:"{file_path.stem}" AND owner:{self.user.username}'
        if folder_name:
            search_query += f' AND folder:{folder_name}'
            
        existing_items = self.gis.content.search(query=search_query, max_items=1)
        
        if existing_items:
            item = existing_items[0]
            logger.info(f"  [ELIMINANDO] {item.title} de ArcGIS...")
            item.delete()
            logger.info(f"  [ELIMINADO] {item.title} de ArcGIS.")

    def on_created(self, event):
        if not event.is_directory:
            self._upload_file(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self._delete_item(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            # La modificación se maneja como una subida/actualización
            self._upload_file(event.src_path)

class GISBoxMonitor:
    """
    Monitoriza el directorio local en busca de cambios y los sincroniza
    con ArcGIS Online/Enterprise.
    """
    def __init__(self):
        # Cargar variables de entorno
        self.config = load_config(Path(__file__).parent)

        self.url = self.config.url
        self.username = self.config.username
        self.password = self.config.password
        self.profile = self.config.profile
        self.local_sync_dir = self.config.local_sync_dir

        self.gis = self._connect_to_arcgis()
        
    def _connect_to_arcgis(self):
        """
        Establece la conexión con la organización de ArcGIS.
        """
        gis = connect_to_arcgis(self.config)

        logger.info(f'Conectado exitosamente a la organización: [{gis.properties.name}]')
        return gis

    def start_monitoring(self):
        """
        Inicia el observador de archivos.
        """
        event_handler = UploadHandler(self.gis, self.local_sync_dir)
        observer = Observer()
        observer.schedule(event_handler, self.local_sync_dir, recursive=True)
        observer.start()
        
        logger.info("GISBox Monitor iniciado. Presiona CTRL+C para detener.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
        logger.info("GISBox Monitor detenido.")

if __name__ == "__main__":
    try:
        # Asegurarse de que el directorio de sincronización existe antes de empezar a monitorizar
        if not Path(os.getenv("LOCAL_SYNC_DIR")).exists():
            logger.warning("El directorio local no existe. Por favor, ejecute primero gisbox_sync.py para la sincronización inicial.")
        
        monitor = GISBoxMonitor()
        monitor.start_monitoring()
        
    except ValueError as e:
        logger.error(f"Error de configuración: {e}. Por favor, complete el archivo .env.")
    except Exception as e:
        logger.error(f"Ocurrió un error durante la monitorización: {e}")
