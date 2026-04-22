from pathlib import Path

from gisbox_common import GISBoxConfig, connect_to_arcgis, load_dotenv


def test_load_dotenv_simple(tmp_path, monkeypatch):
    env_file = tmp_path / '.env'
    env_file.write_text('A=1\n# comentario\nB="hola"\n', encoding='utf-8')

    monkeypatch.delenv('A', raising=False)
    monkeypatch.delenv('B', raising=False)

    load_dotenv(env_file)

    assert __import__('os').getenv('A') == '1'
    assert __import__('os').getenv('B') == 'hola'


def test_connect_to_arcgis_prefers_profile(mocker):
    cfg = GISBoxConfig(url='u', username='x', password='y', profile='perfil', local_sync_dir='/tmp')
    mocked_gis = mocker.patch('gisbox_common.GIS', return_value='gis_obj')

    result = connect_to_arcgis(cfg)

    assert result == 'gis_obj'
    mocked_gis.assert_called_once_with(profile='perfil')


def test_connect_to_arcgis_with_credentials(mocker):
    cfg = GISBoxConfig(url='u', username='x', password='y', profile='', local_sync_dir='/tmp')
    mocked_gis = mocker.patch('gisbox_common.GIS', return_value='gis_obj')

    result = connect_to_arcgis(cfg)

    assert result == 'gis_obj'
    mocked_gis.assert_called_once_with('u', 'x', 'y')


def test_connect_to_arcgis_anonymous(mocker):
    cfg = GISBoxConfig(url='u', username='', password='', profile='', local_sync_dir='/tmp')
    mocked_gis = mocker.patch('gisbox_common.GIS', return_value='gis_obj')

    result = connect_to_arcgis(cfg)

    assert result == 'gis_obj'
    mocked_gis.assert_called_once_with('u')
