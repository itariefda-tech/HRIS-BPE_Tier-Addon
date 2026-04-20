from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import inspect, select


TEST_DB_PATH = Path(".data/test_phase2_schema.db")
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-characters"
os.environ["APP_DEBUG"] = "false"
os.environ["AUTO_MIGRATE_ON_STARTUP"] = "false"

from hris_bpe.database.base import Base
from hris_bpe.database.session import engine, session_scope
from hris_bpe.domains.organization.models import Company
from hris_bpe.domains.workforce_operations.models import WorkSchedule
from hris_bpe.migrations.runner import schema_migrations, upgrade_database
from hris_bpe.seeds.seed import seed_reference_data


def test_phase2_migration_adds_audit_columns_indexes_and_revision_history():
    Base.metadata.drop_all(bind=engine)
    upgrade_database()

    inspector = inspect(engine)

    work_schedule_columns = {column["name"] for column in inspector.get_columns("work_schedules")}
    employee_columns = {column["name"] for column in inspector.get_columns("employees")}
    lifecycle_columns = {
        column["name"] for column in inspector.get_columns("employee_lifecycle_events")
    }
    subscription_columns = {
        column["name"] for column in inspector.get_columns("company_subscriptions")
    }

    assert {"created_by", "updated_by", "version_no"} <= work_schedule_columns
    assert {"created_by", "updated_by", "version_no"} <= employee_columns
    assert {"created_by", "updated_by", "version_no"} <= lifecycle_columns
    assert {"created_by", "updated_by", "version_no"} <= subscription_columns

    work_schedule_indexes = {
        index["name"] for index in inspector.get_indexes("work_schedules")
    }
    attendance_indexes = {
        index["name"] for index in inspector.get_indexes("attendance_records")
    }
    employee_indexes = {
        index["name"]: index for index in inspector.get_indexes("employees")
    }
    lifecycle_indexes = {
        index["name"] for index in inspector.get_indexes("employee_lifecycle_events")
    }

    assert "ix_work_schedules_site_date_status" in work_schedule_indexes
    assert "ix_work_schedules_deployment_date" in work_schedule_indexes
    assert "ix_attendance_records_site_date_status" in attendance_indexes
    assert "ux_employees_company_employee_number" in employee_indexes
    assert employee_indexes["ux_employees_company_employee_number"]["unique"] == 1
    assert employee_indexes["ux_employees_company_employee_number"]["column_names"] == [
        "company_id",
        "employee_number",
    ]
    assert "ix_employees_employee_number" not in employee_indexes
    assert "ix_employee_lifecycle_events_employee_effective_date" in lifecycle_indexes
    assert "ix_employee_lifecycle_events_action_type" in lifecycle_indexes

    with engine.begin() as connection:
        revisions = set(connection.execute(select(schema_migrations.c.revision)).scalars())

    expected_revisions = {
        "0001_base_schema",
        "0002_phase1_foundation",
        "0003_phase15_completion",
        "0004_phase2_database_hardening",
        "0005_phase3_auth_access_control",
        "0006_phase4_company_unique_hardening",
        "0007_phase4_master_hr_lifecycle",
    }
    assert expected_revisions.issubset(revisions)


def test_version_no_increments_on_orm_update():
    Base.metadata.drop_all(bind=engine)
    upgrade_database()
    with session_scope() as session:
        seed_reference_data(session)

    with session_scope() as session:
        company = session.execute(select(Company).where(Company.code == "BPE-HQ")).scalar_one()
        assert company.version_no == 1
        company.phone = "021-000000"
        session.flush()
        assert company.version_no == 2

    with session_scope() as session:
        schedule = (
            session.execute(select(WorkSchedule).order_by(WorkSchedule.id))
            .scalars()
            .first()
        )
        assert schedule is not None
        first_version = schedule.version_no
        schedule.schedule_status = "APPROVED"
        session.flush()
        assert schedule.version_no == first_version + 1
