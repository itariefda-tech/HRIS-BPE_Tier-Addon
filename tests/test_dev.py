from __future__ import annotations

from pathlib import Path

from hris_bpe.config.settings import Settings
from hris_bpe.dev import build_server_kwargs, resolve_reload_dirs


def test_resolve_reload_dirs_points_to_src_root():
    reload_dirs = resolve_reload_dirs()
    expected_src_root = Path(__file__).resolve().parents[1] / "src"

    assert reload_dirs == [str(expected_src_root)]


def test_build_server_kwargs_enables_reload_for_dev_runner():
    settings = Settings(app_host="0.0.0.0", app_port=9001, app_debug=False)

    server_kwargs = build_server_kwargs(settings, enable_reload=True)

    assert server_kwargs["app"] == "hris_bpe.main:app"
    assert server_kwargs["host"] == "0.0.0.0"
    assert server_kwargs["port"] == 9001
    assert server_kwargs["log_level"] == "info"
    assert server_kwargs["reload"] is True
    assert server_kwargs["reload_dirs"] == [str(Path(__file__).resolve().parents[1] / "src")]


def test_build_server_kwargs_can_disable_reload():
    settings = Settings(app_host="127.0.0.1", app_port=8000, app_debug=True)

    server_kwargs = build_server_kwargs(settings, enable_reload=False)

    assert server_kwargs["host"] == "127.0.0.1"
    assert server_kwargs["port"] == 8000
    assert server_kwargs["log_level"] == "debug"
    assert "reload" not in server_kwargs
    assert "reload_dirs" not in server_kwargs
