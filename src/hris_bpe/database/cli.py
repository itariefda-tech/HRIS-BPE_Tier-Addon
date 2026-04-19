from __future__ import annotations

import argparse

from hris_bpe.database.session import session_scope
from hris_bpe.migrations.runner import upgrade_database
from hris_bpe.seeds.seed import seed_reference_data


def main() -> None:
    parser = argparse.ArgumentParser(description="HRIS-BPE database utility")
    parser.add_argument("command", choices=["upgrade", "seed", "bootstrap"])
    args = parser.parse_args()

    if args.command in {"upgrade", "bootstrap"}:
        upgrade_database()
    if args.command in {"seed", "bootstrap"}:
        with session_scope() as session:
            seed_reference_data(session)


if __name__ == "__main__":
    main()
