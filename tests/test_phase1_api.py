from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path

from fastapi.testclient import TestClient


TEST_DB_PATH = Path(".data/test_phase1_api.db")
if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-characters"
os.environ["APP_DEBUG"] = "false"
os.environ["AUTO_MIGRATE_ON_STARTUP"] = "false"

from hris_bpe.bootstrap.app import create_application
from hris_bpe.database.base import Base
from hris_bpe.database.session import engine, session_scope
from hris_bpe.migrations.runner import upgrade_database
from hris_bpe.seeds.seed import seed_reference_data


def _bootstrap_app() -> TestClient:
    Base.metadata.drop_all(bind=engine)
    upgrade_database()
    with session_scope() as session:
        seed_reference_data(session)
    return TestClient(create_application())


def _login(client: TestClient, identifier: str, password: str) -> tuple[str, dict]:
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": identifier, "password": password},
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    return payload["access_token"], payload["user"]


def _login_payload(client: TestClient, identifier: str, password: str) -> dict:
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": identifier, "password": password},
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_health_and_owner_login():
    with _bootstrap_app() as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        token, user = _login(client, "owner@bpe.co.id", "Admin123!")
        assert user["has_explicit_scope"] is False
        assert token

        tiers = client.get(
            "/api/v1/product-control/tiers",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert tiers.status_code == 200
        assert len(tiers.json()["data"]) >= 3


def test_guard_can_check_in_check_out_and_owner_can_adjust_attendance():
    with _bootstrap_app() as client:
        guard_token, _ = _login(client, "guard@bpe.co.id", "Guard123!")
        owner_token, _ = _login(client, "owner@bpe.co.id", "Admin123!")
        guard_headers = {"Authorization": f"Bearer {guard_token}"}
        owner_headers = {"Authorization": f"Bearer {owner_token}"}

        schedules = client.get("/api/v1/workforce-operations/work-schedules", headers=guard_headers)
        assert schedules.status_code == 200
        assert schedules.json()["meta"]["total"] == 1
        schedule = schedules.json()["data"][0]

        check_in = client.post(
            "/api/v1/attendance/check-in",
            headers=guard_headers,
            json={
                "work_schedule_id": schedule["id"],
                "latitude": "-6.200000",
                "longitude": "106.816666",
                "method": "gps",
            },
        )
        assert check_in.status_code == 200
        assert check_in.json()["data"]["attendance_status"] in {"PRESENT", "LATE"}

        check_out = client.post(
            "/api/v1/attendance/check-out",
            headers=guard_headers,
            json={
                "work_schedule_id": schedule["id"],
                "latitude": "-6.200000",
                "longitude": "106.816666",
                "method": "gps",
            },
        )
        assert check_out.status_code == 200
        record = check_out.json()["data"]
        assert record["attendance_status"] == "COMPLETED"

        scheduled_date = schedule["scheduled_date"]
        adjustment = client.post(
            "/api/v1/attendance/manual-adjustments",
            headers=owner_headers,
            json={
                "attendance_record_id": record["id"],
                "new_check_in_datetime": f"{scheduled_date}T07:05:00Z",
                "new_check_out_datetime": f"{scheduled_date}T15:10:00Z",
                "reason": "Supervisor correction",
            },
        )
        assert adjustment.status_code == 200

        adjustments = client.get("/api/v1/attendance/manual-adjustments", headers=owner_headers)
        assert adjustments.status_code == 200
        assert adjustments.json()["meta"]["total"] == 1

        records = client.get("/api/v1/attendance/records", headers=owner_headers)
        assert records.status_code == 200
        adjusted = next(item for item in records.json()["data"] if item["id"] == record["id"])
        assert adjusted["working_minutes"] == 485
        assert adjusted["overtime_minutes"] == 5
        assert adjusted["remarks"] == "Supervisor correction"


def test_company_scoped_user_only_sees_first_company_scope():
    with _bootstrap_app() as client:
        owner_token, owner_user = _login(client, "owner@bpe.co.id", "Admin123!")
        scoped_token, scoped_user = _login(
            client, "company.scope@bpe.co.id", "CompanyScope123!"
        )
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        scoped_headers = {"Authorization": f"Bearer {scoped_token}"}

        assert len(owner_user["company_ids"]) == 2
        assert scoped_user["has_explicit_scope"] is True
        assert len(scoped_user["company_ids"]) == 2
        assert len(scoped_user["company_scope_ids"]) == 1

        owner_companies = client.get("/api/v1/organization/companies", headers=owner_headers)
        scoped_companies = client.get("/api/v1/organization/companies", headers=scoped_headers)
        assert owner_companies.status_code == 200
        assert scoped_companies.status_code == 200
        assert owner_companies.json()["meta"]["total"] == 2
        assert scoped_companies.json()["meta"]["total"] == 1

        scoped_company_id = scoped_companies.json()["data"][0]["id"]
        other_company_id = next(
            item["id"] for item in owner_companies.json()["data"] if item["id"] != scoped_company_id
        )

        scoped_branches = client.get("/api/v1/organization/branches", headers=scoped_headers)
        assert scoped_branches.status_code == 200
        assert all(item["company_id"] == scoped_company_id for item in scoped_branches.json()["data"])

        scoped_clients = client.get("/api/v1/client-contract/clients", headers=scoped_headers)
        assert scoped_clients.status_code == 200
        assert scoped_clients.json()["meta"]["total"] == 1
        assert all(item["company_id"] == scoped_company_id for item in scoped_clients.json()["data"])

        denied_branch = client.post(
            "/api/v1/organization/branches",
            headers=scoped_headers,
            json={
                "company_id": other_company_id,
                "code": "DENY-SBY",
                "name": "Denied Branch",
                "city": "Surabaya",
                "province": "Jawa Timur",
            },
        )
        assert denied_branch.status_code == 403


def test_schedule_publish_approve_workflow_and_draft_schedule_cannot_be_used():
    with _bootstrap_app() as client:
        owner_token, _ = _login(client, "owner@bpe.co.id", "Admin123!")
        guard_token, _ = _login(client, "guard@bpe.co.id", "Guard123!")
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        guard_headers = {"Authorization": f"Bearer {guard_token}"}

        deployments = client.get("/api/v1/workforce-operations/deployments", headers=owner_headers)
        shift_types = client.get("/api/v1/workforce-operations/shift-types", headers=owner_headers)
        assert deployments.status_code == 200
        assert shift_types.status_code == 200

        guard_deployment_id = deployments.json()["data"][0]["id"]
        shift_type_id = shift_types.json()["data"][0]["id"]
        target_date = (date.today() + timedelta(days=2)).isoformat()

        created = client.post(
            "/api/v1/workforce-operations/work-schedules",
            headers=owner_headers,
            json={
                "employee_deployment_id": guard_deployment_id,
                "shift_type_id": shift_type_id,
                "scheduled_date": target_date,
                "schedule_status": "DRAFT",
            },
        )
        assert created.status_code == 200
        draft_schedule = created.json()["data"]
        assert draft_schedule["schedule_status"] == "DRAFT"
        assert draft_schedule["approved_by"] is None

        draft_check_in = client.post(
            "/api/v1/attendance/check-in",
            headers=guard_headers,
            json={
                "work_schedule_id": draft_schedule["id"],
                "latitude": "-6.200000",
                "longitude": "106.816666",
                "method": "gps",
            },
        )
        assert draft_check_in.status_code == 400

        published = client.post(
            f"/api/v1/workforce-operations/work-schedules/{draft_schedule['id']}/publish",
            headers=owner_headers,
        )
        assert published.status_code == 200
        assert published.json()["data"]["schedule_status"] == "PUBLISHED"
        assert published.json()["data"]["approved_by"] is None

        approved = client.post(
            f"/api/v1/workforce-operations/work-schedules/{draft_schedule['id']}/approve",
            headers=owner_headers,
        )
        assert approved.status_code == 200
        assert approved.json()["data"]["schedule_status"] == "APPROVED"
        assert approved.json()["data"]["approved_by"] is not None


def test_attendance_exception_workflow_is_separate_from_manual_adjustment():
    with _bootstrap_app() as client:
        guard_token, _ = _login(client, "guard@bpe.co.id", "Guard123!")
        owner_token, _ = _login(client, "owner@bpe.co.id", "Admin123!")
        guard_headers = {"Authorization": f"Bearer {guard_token}"}
        owner_headers = {"Authorization": f"Bearer {owner_token}"}

        schedules = client.get("/api/v1/workforce-operations/work-schedules", headers=guard_headers)
        assert schedules.status_code == 200
        seeded_schedule = next(
            item for item in schedules.json()["data"] if item["scheduled_date"] == date.today().isoformat()
        )

        check_in = client.post(
            "/api/v1/attendance/check-in",
            headers=guard_headers,
            json={
                "work_schedule_id": seeded_schedule["id"],
                "latitude": "-6.200000",
                "longitude": "106.816666",
                "method": "gps",
            },
        )
        assert check_in.status_code == 200

        check_out = client.post(
            "/api/v1/attendance/check-out",
            headers=guard_headers,
            json={
                "work_schedule_id": seeded_schedule["id"],
                "latitude": "-6.200000",
                "longitude": "106.816666",
                "method": "gps",
            },
        )
        assert check_out.status_code == 200
        record_id = check_out.json()["data"]["id"]

        created_exception = client.post(
            "/api/v1/attendance/exceptions",
            headers=guard_headers,
            json={
                "attendance_record_id": record_id,
                "exception_type": "GPS_REVIEW",
                "description": "Butuh review validasi attendance guard.",
            },
        )
        assert created_exception.status_code == 200
        exception_id = created_exception.json()["data"]["id"]
        assert created_exception.json()["data"]["resolution_status"] == "OPEN"

        guard_exceptions = client.get("/api/v1/attendance/exceptions", headers=guard_headers)
        assert guard_exceptions.status_code == 200
        assert guard_exceptions.json()["meta"]["total"] == 1

        resolved = client.post(
            f"/api/v1/attendance/exceptions/{exception_id}/resolve",
            headers=owner_headers,
            json={"resolution_status": "RESOLVED"},
        )
        assert resolved.status_code == 200
        assert resolved.json()["data"]["resolution_status"] == "RESOLVED"
        assert resolved.json()["data"]["resolved_by"] is not None

        owner_exceptions = client.get("/api/v1/attendance/exceptions", headers=owner_headers)
        assert owner_exceptions.status_code == 200
        assert owner_exceptions.json()["meta"]["total"] == 1


def test_site_scoped_supervisor_only_sees_and_writes_inside_site_scope():
    with _bootstrap_app() as client:
        owner_token, _ = _login(client, "owner@bpe.co.id", "Admin123!")
        supervisor_token, supervisor_user = _login(
            client, "supervisor@bpe.co.id", "Supervisor123!"
        )
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        supervisor_headers = {"Authorization": f"Bearer {supervisor_token}"}
        site_scope_id = supervisor_user["site_scope_ids"][0]

        assert supervisor_user["has_explicit_scope"] is True

        sites = client.get("/api/v1/site-operations/sites", headers=supervisor_headers)
        assert sites.status_code == 200
        assert sites.json()["meta"]["total"] == 1
        assert sites.json()["data"][0]["id"] == site_scope_id

        deployments = client.get("/api/v1/workforce-operations/deployments", headers=supervisor_headers)
        assert deployments.status_code == 200
        assert deployments.json()["meta"]["total"] == 1

        histories = client.get(
            "/api/v1/workforce-operations/deployment-histories",
            headers=supervisor_headers,
        )
        assert histories.status_code == 200
        assert histories.json()["meta"]["total"] == 1
        assert histories.json()["data"][0]["new_client_site_id"] == site_scope_id

        owner_sites = client.get("/api/v1/site-operations/sites", headers=owner_headers)
        assert owner_sites.status_code == 200
        other_site_id = next(
            item["id"] for item in owner_sites.json()["data"] if item["id"] != site_scope_id
        )
        denied_post = client.post(
            "/api/v1/site-operations/posts",
            headers=supervisor_headers,
            json={
                "client_site_id": other_site_id,
                "code": "POST-X",
                "name": "Out of Scope",
            },
        )
        assert denied_post.status_code == 403

        owner_deployments = client.get("/api/v1/workforce-operations/deployments", headers=owner_headers)
        shift_types = client.get("/api/v1/workforce-operations/shift-types", headers=owner_headers)
        assert owner_deployments.status_code == 200
        assert shift_types.status_code == 200

        generate = client.post(
            "/api/v1/workforce-operations/work-schedules/generate",
            headers=supervisor_headers,
            json={
                "employee_deployment_ids": [
                    item["id"] for item in owner_deployments.json()["data"]
                ],
                "shift_type_id": shift_types.json()["data"][0]["id"],
                "date_from": (date.today() + timedelta(days=1)).isoformat(),
                "date_to": (date.today() + timedelta(days=1)).isoformat(),
                "schedule_status": "PUBLISHED",
            },
        )
        assert generate.status_code == 200
        assert generate.json()["meta"]["total"] == 1
        assert generate.json()["data"][0]["client_site_id"] == site_scope_id


def test_branch_scoped_hr_only_sees_employees_inside_branch_scope():
    with _bootstrap_app() as client:
        hr_token, hr_user = _login(client, "hr.branch@bpe.co.id", "HrBranch123!")
        hr_headers = {"Authorization": f"Bearer {hr_token}"}

        assert hr_user["has_explicit_scope"] is True
        assert len(hr_user["branch_scope_ids"]) == 1

        employees = client.get("/api/v1/master-hr/employees", headers=hr_headers)
        assert employees.status_code == 200
        employee_numbers = {item["employee_number"] for item in employees.json()["data"]}

        assert "EMP-0001" in employee_numbers
        assert "EMP-0100" in employee_numbers
        assert "EMP-0101" in employee_numbers
        assert "EMP-0002" not in employee_numbers


def test_refresh_and_logout_revoke_current_auth_session():
    with _bootstrap_app() as client:
        login_payload = _login_payload(client, "owner@bpe.co.id", "Admin123!")
        access_token = login_payload["access_token"]
        refresh_token = login_payload["refresh_token"]
        session_id = login_payload["session_id"]

        me = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert me.status_code == 200

        refreshed = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refreshed.status_code == 200
        refreshed_payload = refreshed.json()["data"]
        assert refreshed_payload["session_id"] == session_id
        assert refreshed_payload["refresh_token"] != refresh_token
        refreshed_access_token = refreshed_payload["access_token"]
        refreshed_refresh_token = refreshed_payload["refresh_token"]

        logout = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {refreshed_access_token}"},
        )
        assert logout.status_code == 200
        assert logout.json()["data"]["revoked_session_id"] == session_id

        revoked_me = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {refreshed_access_token}"},
        )
        assert revoked_me.status_code == 401

        revoked_refresh = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refreshed_refresh_token},
        )
        assert revoked_refresh.status_code == 401


def test_access_control_audit_log_records_role_and_scope_changes():
    with _bootstrap_app() as client:
        owner_token, _ = _login(client, "owner@bpe.co.id", "Admin123!")
        owner_headers = {"Authorization": f"Bearer {owner_token}"}

        users = client.get("/api/v1/access-control/users", headers=owner_headers)
        roles = client.get("/api/v1/access-control/roles", headers=owner_headers)
        companies = client.get("/api/v1/organization/companies", headers=owner_headers)

        assert users.status_code == 200
        assert roles.status_code == 200
        assert companies.status_code == 200

        guard_user = next(
            item for item in users.json()["data"] if item["email"] == "guard@bpe.co.id"
        )
        hr_role = next(item for item in roles.json()["data"] if item["code"] == "hr_admin")
        company_id = companies.json()["data"][0]["id"]

        assign_roles = client.post(
            f"/api/v1/access-control/users/{guard_user['id']}/roles",
            headers=owner_headers,
            json={"role_ids": [hr_role["id"]]},
        )
        assert assign_roles.status_code == 200
        assert assign_roles.json()["data"]["role_codes"] == ["hr_admin"]

        replace_scopes = client.put(
            f"/api/v1/access-control/users/{guard_user['id']}/scopes",
            headers=owner_headers,
            json=[
                {
                    "scope_type": "COMPANY",
                    "company_id": company_id,
                }
            ],
        )
        assert replace_scopes.status_code == 200
        assert replace_scopes.json()["meta"]["total"] == 1

        audit_logs = client.get(
            f"/api/v1/access-control/audit-logs?target_user_id={guard_user['id']}",
            headers=owner_headers,
        )
        assert audit_logs.status_code == 200
        assert audit_logs.json()["meta"]["total"] == 2

        logs_by_action = {
            item["action_type"]: item for item in audit_logs.json()["data"]
        }
        assert logs_by_action["USER_ROLES_REPLACED"]["old_data"] == ["guard"]
        assert logs_by_action["USER_ROLES_REPLACED"]["new_data"] == ["hr_admin"]
        assert logs_by_action["USER_SCOPES_REPLACED"]["old_data"] == []
        assert logs_by_action["USER_SCOPES_REPLACED"]["new_data"] == [
            {
                "branch_id": None,
                "client_site_id": None,
                "company_id": company_id,
                "scope_type": "COMPANY",
            }
        ]
