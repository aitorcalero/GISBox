from unittest.mock import patch

import pytest

import gisbox_cli


def test_parser_accepts_commands():
    parser = gisbox_cli.build_parser()

    for cmd in ('check-config', 'sync-down', 'monitor'):
        args = parser.parse_args([cmd])
        assert args.command == cmd


def test_main_dispatch_check_config():
    with patch('gisbox_cli._check_config', return_value=0) as mocked:
        result = gisbox_cli.main(['check-config'])
    assert result == 0
    mocked.assert_called_once()


def test_main_dispatch_sync_down():
    with patch('gisbox_cli._sync_down', return_value=0) as mocked:
        result = gisbox_cli.main(['sync-down'])
    assert result == 0
    mocked.assert_called_once()


def test_main_dispatch_monitor():
    with patch('gisbox_cli._monitor', return_value=0) as mocked:
        result = gisbox_cli.main(['monitor'])
    assert result == 0
    mocked.assert_called_once()


def test_main_requires_command():
    with pytest.raises(SystemExit):
        gisbox_cli.main([])
