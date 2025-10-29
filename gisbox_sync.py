import os
import shutil
import logging
from pathlib import Path
from arcgis.gis import GIS, User
from dotenv import load_dotenv

# Configuración de Logging
# Configuración de Logging
logger = logging.getLogger('GISBoxSync')
logger.setLevel(logging.INFO)
# Configuración del handler (para que solo se configure una vez)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

class GISBoxSync:
    """
    Clase principal para la sincronización de archivos entre ArcGIS Online/Enterprise
    y un sistema de archivos local.
    """
    def __init__(self):
        # Cargar variables de entorno desde .env
        load_dotenv(Path(__file__).parent / ".env")
        
        self.url = os.getenv("ARCGIS_URL")
        self.username = os.getenv("ARCGIS_USERNAME")
        self.password = os.getenv("ARCGIS_PASSWORD")
        self.profile = os.getenv("ARCGIS_PROFILE")
        self.local_sync_dir = os.getenv("LOCAL_SYNC_DIR")
        
        if not self.local_sync_dir:
            raise ValueError("LOCAL_SYNC_DIR no está configurado en el archivo .env")

        self.gis = self._connect_to_arcgis()
        self.user = self.gis.users.get(self.username) if self.username else self.gis.users.me
        
        # Tipos de archivo a sincronizar (Se podría externalizar)
        self.file_types = ['CSV', 'Service Definition', 'KML', 'ZIP', 'Shapefile',
                           'Image Collection', 'PDF', 'Microsoft Excel']

    def _connect_to_arcgis(self):
        """
        Establece la conexión con la organización de ArcGIS.
        Prioriza la conexión por perfil si está disponible.
        """
        if self.profile:
            gis = GIS(profile=self.profile)
        elif self.username and self.password:
            gis = GIS(self.url, self.username, self.password)
        else:
            # Conexión anónima o con prompt de credenciales
            gis = GIS(self.url)
            
        logger.info(f'Conectado exitosamente a la organización: [{gis.properties.name}]')
        return gis

    def _prepare_local_directory(self):
        """
        Prepara el directorio local de sincronización, eliminando el contenido anterior
        para una sincronización limpia (en modo backup).
        """
        local_path = Path(self.local_sync_dir)
        if local_path.exists():
            logger.warning(f"Eliminando contenido anterior en: {self.local_sync_dir}")
            shutil.rmtree(local_path)
        
        local_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio de sincronización preparado: {self.local_sync_dir}")

    def download_items(self, folder_name=None):
        """
        Descarga los elementos de ArcGIS Online/Enterprise al directorio local.
        """
        items = self.user.items(folder=folder_name)
        download_count = 0
        
        if folder_name:
            local_folder_path = Path(self.local_sync_dir) / folder_name
            local_folder_path.mkdir(exist_ok=True)
            logger.info(f"Procesando carpeta de ArcGIS: {folder_name}")
        else:
            local_folder_path = Path(self.local_sync_dir)
            logger.info("Procesando carpeta raíz de ArcGIS")

        for item in items:
            if item.type in self.file_types:
                try:
                    # La API de ArcGIS descarga el archivo a un directorio temporal
                    temp_path = Path(item.download(local_folder_path))
                    
                    # Renombrar el archivo descargado al nombre original con extensión correcta
                    # La API a veces descarga sin extensión o con un nombre temporal
                    file_extension = item.type.lower().replace(' ', '_')
                    if item.type == 'Microsoft Excel':
                        file_extension = 'xlsx'
                    elif item.type == 'Service Definition':
                        file_extension = 'sd'
                    elif item.type == 'Image Collection':
                        file_extension = 'zip'
                    else:
                        # Intentar obtener la extensión del nombre del item si es posible
                        if '.' in item.title:
                            file_extension = item.title.rsplit('.', 1)[1]
                        elif item.type in ['CSV', 'KML', 'PDF', 'ZIP']:
                            file_extension = item.type.lower()
                        
                    final_name = f"{item.title}.{file_extension}"
                    final_path = local_folder_path / final_name
                    
                    # Mover y renombrar el archivo temporal al destino final
                    if temp_path.is_dir():
                        # Si es un zip/carpeta, el archivo descargado es un directorio con el contenido
                        # Necesitamos mover el contenido o comprimirlo si fuera necesario.
                        # Por simplicidad, en esta refactorización nos enfocaremos en archivos individuales.
                        # El código original solo renombra, lo que implica que el download() devuelve un path de archivo.
                        # Asumimos el comportamiento del código original: temp_path es el archivo descargado.
                        
                        # Si el path devuelto es un directorio (ej. para Shapefile), lo comprimimos en un zip
                        if temp_path.is_dir():
                            shutil.make_archive(final_path.stem, 'zip', temp_path)
                            shutil.rmtree(temp_path)
                            final_path = local_folder_path / f"{final_path.stem}.zip"
                            
                        else:
                            # Renombrar el archivo descargado
                            os.rename(temp_path, final_path)
                            
                    else:
                         os.rename(temp_path, final_path)
                         
                    logger.info(f"  [DESCARGADO] {item.title} ({item.type}) a {final_path.name}")
                    download_count += 1
                    
                except Exception as e:
                    logger.error(f"Error al descargar {item.title}: {e}")

        return download_count

    def sync_down(self):
        """
        Realiza la sincronización de descarga (backup) de toda la organización.
        """
        self._prepare_local_directory()
        
        # 1. Descargar elementos de la carpeta raíz
        root_count = self.download_items(folder_name=None)
        
        # 2. Descargar elementos de las subcarpetas
        folders = self.user.folders
        total_count = root_count
        
        for folder in folders:
            folder_name = folder['title']
            count = self.download_items(folder_name=folder_name)
            total_count += count
            
        logger.info(f"\nSincronización de descarga completada. Total de elementos descargados: {total_count}")
        
        return total_count

if __name__ == "__main__":
    try:
        # Se requiere instalar python-dotenv: pip install python-dotenv
        # Se requiere instalar arcgis: pip install arcgis
        
        # El usuario debe completar el archivo .env con sus credenciales
        sync_tool = GISBoxSync()
        sync_tool.sync_down()
        
    except ValueError as e:
        logger.error(f"Error de configuración: {e}. Por favor, complete el archivo .env.")
    except Exception as e:
        logger.error(f"Ocurrió un error durante la sincronización: {e}")
