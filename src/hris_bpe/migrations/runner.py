from __future__ import annotations

from collections.abc import Callable

from sqlalchemy import Column, MetaData, String, Table, inspect, select, text
from sqlalchemy.engine import Connection

from hris_bpe.database.base import Base
from hris_bpe.database.model_registry import access_control_models  # noqa: F401
from hris_bpe.database.model_registry import attendance_models  # noqa: F401
from hris_bpe.database.model_registry import auth_models  # noqa: F401
from hris_bpe.database.model_registry import client_contract_models  # noqa: F401
from hris_bpe.database.model_registry import master_hr_models  # noqa: F401
from hris_bpe.database.model_registry import organization_models  # noqa: F401
from hris_bpe.database.model_registry import product_control_models  # noqa: F401
from hris_bpe.database.model_registry import site_operations_models  # noqa: F401
from hris_bpe.database.model_registry import workforce_operations_models  # noqa: F401
from hris_bpe.database.session import engine


MIGRATION_LOCK_KEY = 2026041902

migration_metadata = MetaData()
schema_migrations = Table(
    "schema_migrations",
    migration_metadata,
    Column("revision", String(100), primary_key=True),
)


class MigrationStep:
    def __init__(self, revision: str, upgrade: Callable[[Connection], None]) -> None:
        self.revision = revision
        self.upgrade = upgrade


def _noop(_: Connection) -> None:
    return None


def _ensure_postgresql_migration_lock(connection: Connection) -> None:
    if connection.dialect.name != "postgresql":
        return
    connection.execute(
        text("SELECT pg_advisory_xact_lock(:lock_key)"),
        {"lock_key": MIGRATION_LOCK_KEY},
    )


def _column_names(connection: Connection, table_name: str) -> set[str]:
    return {column["name"] for column in inspect(connection).get_columns(table_name)}


def _ensure_column(connection: Connection, table_name: str, column_name: str, ddl: str) -> None:
    if column_name in _column_names(connection, table_name):
        return
    connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {ddl}"))


def _ensure_index(connection: Connection, ddl: str) -> None:
    connection.execute(text(ddl))


def _apply_phase2_database_hardening(connection: Connection) -> None:
    audit_tables = [
        "companies",
        "branches",
        "departments",
        "positions",
        "users",
        "roles",
        "user_scope_access",
        "employees",
        "guard_profiles",
        "employee_contracts",
        "clients",
        "client_contracts",
        "client_sites",
        "site_posts",
        "company_subscriptions",
        "company_feature_modules",
        "employee_deployments",
        "shift_types",
        "work_schedules",
        "attendance_records",
        "attendance_exceptions",
    ]
    for table_name in audit_tables:
        _ensure_column(
            connection,
            table_name,
            "created_by",
            "created_by INTEGER",
        )
        _ensure_column(
            connection,
            table_name,
            "updated_by",
            "updated_by INTEGER",
        )
        _ensure_column(
            connection,
            table_name,
            "version_no",
            "version_no INTEGER NOT NULL DEFAULT 1",
        )

    index_statements = [
        "CREATE INDEX IF NOT EXISTS ix_companies_status_code ON companies (status, code)",
        "CREATE INDEX IF NOT EXISTS ix_branches_company_status ON branches (company_id, status)",
        "CREATE INDEX IF NOT EXISTS ix_departments_company_name ON departments (company_id, name)",
        "CREATE INDEX IF NOT EXISTS ix_positions_company_category ON positions (company_id, category)",
        "CREATE INDEX IF NOT EXISTS ix_roles_company_name ON roles (company_id, name)",
        "CREATE INDEX IF NOT EXISTS ix_user_scope_access_user_scope_type ON user_scope_access (user_id, scope_type)",
        "CREATE INDEX IF NOT EXISTS ix_employees_company_branch_status ON employees (company_id, branch_id, employee_status)",
        "CREATE INDEX IF NOT EXISTS ix_employees_branch_status ON employees (branch_id, employee_status)",
        "CREATE INDEX IF NOT EXISTS ix_employee_contracts_employee_status_dates ON employee_contracts (employee_id, status, start_date)",
        "CREATE INDEX IF NOT EXISTS ix_clients_company_status ON clients (company_id, status)",
        "CREATE INDEX IF NOT EXISTS ix_client_contracts_client_status_dates ON client_contracts (client_id, status, start_date)",
        "CREATE INDEX IF NOT EXISTS ix_client_sites_client_status ON client_sites (client_id, status)",
        "CREATE INDEX IF NOT EXISTS ix_site_posts_site_active ON site_posts (client_site_id, active_flag)",
        "CREATE INDEX IF NOT EXISTS ix_company_subscriptions_company_status ON company_subscriptions (company_id, subscription_status)",
        "CREATE INDEX IF NOT EXISTS ix_company_subscriptions_tier_status ON company_subscriptions (product_tier_id, subscription_status)",
        "CREATE INDEX IF NOT EXISTS ix_company_feature_modules_subscription_active ON company_feature_modules (company_subscription_id, active_flag)",
        "CREATE INDEX IF NOT EXISTS ix_company_feature_modules_module_active ON company_feature_modules (feature_module_id, active_flag)",
        "CREATE INDEX IF NOT EXISTS ix_employee_deployments_site_status_dates ON employee_deployments (client_site_id, deployment_status, start_date)",
        "CREATE INDEX IF NOT EXISTS ix_employee_deployments_employee_status ON employee_deployments (employee_id, deployment_status)",
        "CREATE INDEX IF NOT EXISTS ix_deployment_histories_deployment_action_date ON deployment_histories (employee_deployment_id, action_date)",
        "CREATE INDEX IF NOT EXISTS ix_shift_types_company_code ON shift_types (company_id, code)",
        "CREATE INDEX IF NOT EXISTS ix_work_schedules_deployment_date ON work_schedules (employee_deployment_id, scheduled_date)",
        "CREATE INDEX IF NOT EXISTS ix_work_schedules_site_date_status ON work_schedules (client_site_id, scheduled_date, schedule_status)",
        "CREATE INDEX IF NOT EXISTS ix_work_schedules_employee_date_status ON work_schedules (employee_id, scheduled_date, schedule_status)",
        "CREATE INDEX IF NOT EXISTS ix_attendance_records_employee_date ON attendance_records (employee_id, attendance_date)",
        "CREATE INDEX IF NOT EXISTS ix_attendance_records_site_date_status ON attendance_records (client_site_id, attendance_date, attendance_status)",
        "CREATE INDEX IF NOT EXISTS ix_attendance_exceptions_record_resolution ON attendance_exceptions (attendance_record_id, resolution_status)",
    ]
    for ddl in index_statements:
        _ensure_index(connection, ddl)


def _apply_phase3_auth_access_control(connection: Connection) -> None:
    Base.metadata.tables["auth_refresh_sessions"].create(connection, checkfirst=True)
    Base.metadata.tables["auth_token_revocations"].create(connection, checkfirst=True)
    Base.metadata.tables["access_control_audit_logs"].create(connection, checkfirst=True)


MIGRATIONS = [
    MigrationStep("0001_base_schema", _noop),
    MigrationStep("0002_phase1_foundation", _noop),
    MigrationStep("0003_phase15_completion", _noop),
    MigrationStep("0004_phase2_database_hardening", _apply_phase2_database_hardening),
    MigrationStep("0005_phase3_auth_access_control", _apply_phase3_auth_access_control),
]


def upgrade_database() -> None:
    with engine.begin() as connection:
        _ensure_postgresql_migration_lock(connection)
        schema_migrations.create(connection, checkfirst=True)
        Base.metadata.create_all(bind=connection)
        applied_revisions = set(
            connection.execute(select(schema_migrations.c.revision)).scalars()
        )
        for migration in MIGRATIONS:
            if migration.revision in applied_revisions:
                continue
            migration.upgrade(connection)
            connection.execute(
                schema_migrations.insert().values(revision=migration.revision)
            )
