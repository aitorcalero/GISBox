import pytest
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

# Importar la clase a probar
# Se asume que python-dotenv está instalado para cargar el .env
from gisbox_sync import GISBoxSync, logger

# Fixture para simular el entorno de trabajo
@pytest.fixture
def mock_env(mocker):
    # Mockear la carga de variables de entorno
    mocker.patch('gisbox_sync.load_dotenv')
    mocker.patch.dict(os.environ, {
        "ARCGIS_URL": "https://test.arcgis.com",
        "ARCGIS_USERNAME": "test_user",
        "ARCGIS_PASSWORD": "test_password",
        "ARCGIS_PROFILE": "",
        "LOCAL_SYNC_DIR": "/tmp/gisbox_sync_test"
    })
    # Asegurar que el directorio de prueba existe
    test_dir = Path("/tmp/gisbox_sync_test")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True, exist_ok=True)
    yield
    # Limpiar después de la prueba
    if test_dir.exists():
        shutil.rmtree(test_dir)

# Fixture para mockear la conexión a GIS y el usuario
@pytest.fixture
def mock_gis_user(mocker):
    # Mockear la conexión a GIS
    mock_gis = MagicMock()
    mock_gis.properties.name = "Test Org"
    
    # Mockear el usuario
    mock_user = MagicMock()
    mock_user.username = "test_user"
    mock_user.folders = [{'title': 'Folder1', 'id': 'id1'}]
    mock_user.items.return_value = [] # Por defecto, sin items
    
    mock_gis.users.get.return_value = mock_user
    
    mocker.patch('gisbox_sync.GIS', return_value=mock_gis)
    mocker.patch('gisbox_sync.User', return_value=mock_user)
    
    return mock_gis, mock_user

# Test 1: Inicialización correcta
def test_gisbox_sync_initialization(mock_env, mock_gis_user):
    sync_tool = GISBoxSync()
    assert sync_tool.url == "https://test.arcgis.com"
    assert sync_tool.username == "test_user"
    assert sync_tool.local_sync_dir == "/tmp/gisbox_sync_test"
    assert sync_tool.gis is mock_gis_user[0]
    mock_gis_user[0].users.get.assert_called_with("test_user")

# Test 2: Error si LOCAL_SYNC_DIR no está configurado
def test_gisbox_sync_no_sync_dir(mocker):
    mocker.patch('gisbox_sync.load_dotenv')
    mocker.patch.dict(os.environ, {"LOCAL_SYNC_DIR": ""})
    with pytest.raises(ValueError, match="LOCAL_SYNC_DIR no está configurado"):
        GISBoxSync()

# Test 3: Preparación del directorio local
def test_prepare_local_directory(mock_env, mock_gis_user, mocker):
    sync_tool = GISBoxSync()
    # Crear un archivo dentro para probar la limpieza
    Path(sync_tool.local_sync_dir, "old_file.txt").touch()
    
    with patch.object(logger, 'warning') as mock_warning:
        sync_tool._prepare_local_directory()
        mock_warning.assert_called_once() # Debería advertir sobre la eliminación
        
    assert Path(sync_tool.local_sync_dir).exists()
    assert not Path(sync_tool.local_sync_dir, "old_file.txt").exists()

# Test 4: Descarga de un item con éxito
def test_download_items_success(mock_env, mock_gis_user, mocker):
    sync_tool = GISBoxSync()
    mock_user = mock_gis_user[1]
    
    # Mockear un item descargable
    mock_item = MagicMock()
    mock_item.type = 'PDF'
    mock_item.title = 'Test Document'
    
    # Simular que item.download() devuelve la ruta temporal del archivo
    temp_file_path = Path(sync_tool.local_sync_dir, "temp_download_file")
    temp_file_path.touch()
    mock_item.download.return_value = str(temp_file_path)
    
    mock_user.items.return_value = [mock_item]
    
    # Mockear os.rename para verificar el renombrado
    mocker.patch('os.rename')
    
    # Ejecutar la descarga
    count = sync_tool.download_items()
    
    assert count == 1
    mock_item.download.assert_called_once()
    
    # Verificar que se intentó renombrar al formato final
    expected_final_path = Path(sync_tool.local_sync_dir, "Test Document.pdf")
    os.rename.assert_called_with(temp_file_path, expected_final_path)

# Test 5: Descarga de un item con error
def test_download_items_failure(mock_env, mock_gis_user, mocker):
    sync_tool = GISBoxSync()
    mock_user = mock_gis_user[1]
    
    # Mockear un item que causa error
    mock_item = MagicMock()
    mock_item.type = 'PDF'
    mock_item.title = 'Failing Document'
    mock_item.download.side_effect = Exception("Download failed")
    
    mock_user.items.return_value = [mock_item]
    
    with patch.object(logger, 'error') as mock_error:
        count = sync_tool.download_items()
        
    assert count == 0
    mock_error.assert_called_once()
    assert "Download failed" in mock_error.call_args[0][0]

# Test 6: Sincronización completa (sync_down)
def test_sync_down_flow(mock_env, mock_gis_user, mocker):
    sync_tool = GISBoxSync()
    mock_user = mock_gis_user[1]
    
    # Mockear el método download_items para controlar el flujo
    mock_download = mocker.patch.object(GISBoxSync, 'download_items', side_effect=[2, 1]) # 2 items en root, 1 en Folder1
    
    # Mockear la preparación del directorio
    mock_prepare = mocker.patch.object(GISBoxSync, '_prepare_local_directory')
    
    # Ejecutar la sincronización
    total_count = sync_tool.sync_down()
    
    mock_prepare.assert_called_once()
    
    # Se llama una vez para la raíz (folder_name=None) y una vez por cada carpeta ('Folder1')
    mock_download.call_count == 2
    mock_download.assert_any_call(folder_name=None)
    mock_download.assert_any_call(folder_name='Folder1')
    
    assert total_count == 3
