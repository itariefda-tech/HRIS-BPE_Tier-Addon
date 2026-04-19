from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import uvicorn

from hris_bpe.config.settings import Settings, get_settings
from hris_bpe.database.session import session_scope
from hris_bpe.migrations.runner import upgrade_database
from hris_bpe.seeds.seed import seed_reference_data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="HRIS-BPE development server with auto bootstrap and auto reload."
    )
    parser.add_argument("--host", help="Override APP_HOST.")
    parser.add_argument("--port", type=int, help="Override APP_PORT.")
    parser.add_argument(
        "--skip-bootstrap",
        action="store_true",
        help="Skip migration + seed bootstrap before starting the dev server.",
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable code auto reload.",
    )
    return parser


def resolve_reload_dirs() -> list[str]:
    package_root = Path(__file__).resolve().parent
    source_root = package_root.parent
    return [str(source_root)]


def bootstrap_database() -> None:
    upgrade_database()
    with session_scope() as session:
        seed_reference_data(session)


def build_server_kwargs(
    settings: Settings,
    *,
    host: str | None = None,
    port: int | None = None,
    enable_reload: bool = True,
) -> dict[str, Any]:
    server_kwargs: dict[str, Any] = {
        "app": "hris_bpe.main:app",
        "host": host or settings.app_host,
        "port": port or settings.app_port,
        "log_level": "debug" if settings.app_debug else "info",
    }
    if enable_reload:
        server_kwargs["reload"] = True
        server_kwargs["reload_dirs"] = resolve_reload_dirs()
    return server_kwargs


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    settings = get_settings()

    if not args.skip_bootstrap:
        bootstrap_database()

    server_kwargs = build_server_kwargs(
        settings,
        host=args.host,
        port=args.port,
        enable_reload=not args.no_reload,
    )
    uvicorn.run(**server_kwargs)


if __name__ == "__main__":
    main()
