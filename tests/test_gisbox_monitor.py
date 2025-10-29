import pytest
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
from watchdog.events import FileSystemEvent

# Importar las clases a probar
from gisbox_monitor import GISBoxMonitor, UploadHandler, logger

# Fixture para simular el entorno de trabajo
@pytest.fixture
def mock_monitor_env(mocker):
    # Mockear la carga de variables de entorno
    mocker.patch('gisbox_monitor.load_dotenv')
    mocker.patch.dict(os.environ, {
        "ARCGIS_URL": "https://test.arcgis.com",
        "ARCGIS_USERNAME": "test_user",
        "ARCGIS_PASSWORD": "test_password",
        "ARCGIS_PROFILE": "",
        "LOCAL_SYNC_DIR": "/tmp/gisbox_monitor_test"
    })
    # Asegurar que el directorio de prueba existe
    test_dir = Path("/tmp/gisbox_monitor_test")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Crear una subcarpeta
    (test_dir / "TestFolder").mkdir()
    
    yield
    # Limpiar después de la prueba
    if test_dir.exists():
        shutil.rmtree(test_dir)

# Fixture para mockear la conexión a GIS y el usuario
@pytest.fixture
def mock_gis_monitor(mocker):
    # Mockear la conexión a GIS
    mock_gis = MagicMock()
    mock_gis.properties.name = "Test Monitor Org"
    
    # Mockear el usuario
    mock_user = MagicMock()
    mock_user.username = "test_user"
    mock_gis.users.me = mock_user
    
    mocker.patch('gisbox_monitor.GIS', return_value=mock_gis)
    
    return mock_gis, mock_user

# --- Pruebas para UploadHandler ---

@pytest.fixture
def handler(mock_gis_monitor):
    gis, _ = mock_gis_monitor
    return UploadHandler(gis, "/tmp/gisbox_monitor_test")

def test_get_arcgis_folder_root(handler):
    src_path = "/tmp/gisbox_monitor_test/file.txt"
    assert handler._get_arcgis_folder(src_path) is None

def test_get_arcgis_folder_subfolder(handler):
    src_path = "/tmp/gisbox_monitor_test/TestFolder/file.txt"
    assert handler._get_arcgis_folder(src_path) == "TestFolder"

def test_upload_file_new(handler, mock_gis_monitor, mocker, mock_monitor_env):
    mock_gis, mock_user = mock_gis_monitor
    mock_gis.content.search.return_value = [] # No existe
    mock_gis.content.add.return_value = MagicMock(title="New File")
    
    file_path = Path("/tmp/gisbox_monitor_test/new_file.csv")
    file_path.touch()
    
    with patch.object(logger, 'info') as mock_info:
        handler._upload_file(str(file_path))
        
    mock_gis.content.search.assert_called_once()
    mock_gis.content.add.assert_called_once()
    mock_info.assert_any_call('  [SUBIENDO] Nuevo archivo: new_file.csv...')

def test_upload_file_update(handler, mock_gis_monitor, mocker, mock_monitor_env):
    mock_gis, mock_user = mock_gis_monitor
    mock_item = MagicMock(title="Existing File", update=MagicMock())
    mock_gis.content.search.return_value = [mock_item] # Existe
    
    file_path = Path("/tmp/gisbox_monitor_test/Existing File.csv")
    file_path.touch()
    
    with patch.object(logger, 'info') as mock_info:
        handler._upload_file(str(file_path))
        
    mock_gis.content.search.assert_called_once()
    mock_item.update.assert_called_once()
    mock_info.assert_any_call('  [ACTUALIZANDO] Existing File...')

def test_delete_item_exists(handler, mock_gis_monitor, mocker, mock_monitor_env):
    mock_gis, mock_user = mock_gis_monitor
    mock_item = MagicMock(title="FileToDelete", delete=MagicMock())
    mock_gis.content.search.return_value = [mock_item] # Existe
    
    file_path = Path("/tmp/gisbox_monitor_test/FileToDelete.csv")
    file_path.touch() # Crear el archivo para que is_file() sea True
    
    with patch.object(logger, 'info') as mock_info:
        handler._delete_item(str(file_path))
        
    mock_gis.content.search.assert_called_once()
    mock_item.delete.assert_called_once()
    mock_info.assert_any_call('  [ELIMINADO] FileToDelete de ArcGIS.')

def test_on_created_file(handler, mocker):
    mock_upload = mocker.patch.object(handler, '_upload_file')
    event = FileSystemEvent("/tmp/gisbox_monitor_test/created.txt")
    event.is_directory = False
    handler.on_created(event)
    mock_upload.assert_called_once_with("/tmp/gisbox_monitor_test/created.txt")

def test_on_deleted_file(handler, mocker):
    mock_delete = mocker.patch.object(handler, '_delete_item')
    event = FileSystemEvent("/tmp/gisbox_monitor_test/deleted.txt")
    event.is_directory = False
    handler.on_deleted(event)
    mock_delete.assert_called_once_with("/tmp/gisbox_monitor_test/deleted.txt")

def test_on_modified_file(handler, mocker):
    mock_upload = mocker.patch.object(handler, '_upload_file')
    event = FileSystemEvent("/tmp/gisbox_monitor_test/modified.txt")
    event.is_directory = False
    handler.on_modified(event)
    mock_upload.assert_called_once_with("/tmp/gisbox_monitor_test/modified.txt")

# --- Pruebas para GISBoxMonitor ---

def test_gisbox_monitor_initialization(mock_monitor_env, mock_gis_monitor):
    monitor = GISBoxMonitor()
    assert monitor.url == "https://test.arcgis.com"
    assert monitor.gis is mock_gis_monitor[0]

def test_gisbox_monitor_start_monitoring(mock_monitor_env, mock_gis_monitor, mocker):
    monitor = GISBoxMonitor()
    
    # Mockear el Observer y el sleep para evitar bucles infinitos en la prueba
    mock_observer = MagicMock()
    mocker.patch('gisbox_monitor.Observer', return_value=mock_observer)
    mocker.patch('gisbox_monitor.time.sleep', side_effect=KeyboardInterrupt)
    
    with patch.object(logger, 'info') as mock_info:
        # La KeyboardInterrupt detendrá el bucle
        monitor.start_monitoring()
        
    mock_observer.schedule.assert_called_once()
    mock_observer.start.assert_called_once()
    mock_observer.stop.assert_called_once()
    mock_observer.join.assert_called_once()
    mock_info.assert_any_call("GISBox Monitor iniciado. Presiona CTRL+C para detener.")
    mock_info.assert_any_call("GISBox Monitor detenido.")
