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
from hris_bpe.common.security import hash_password
from hris_bpe.database.base import Base
from hris_bpe.database.session import engine, session_scope
from hris_bpe.domains.access_control.models import User
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
        assert user["preferred_language"] == "en"
        assert user["preferred_theme"] == "theme_4"
        assert token

        tiers = client.get(
            "/api/v1/product-control/tiers",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert tiers.status_code == 200
        assert len(tiers.json()["data"]) >= 3


def test_auth_me_and_preference_update_support_language_and_theme_preferences():
    with _bootstrap_app() as client:
        login_payload = _login_payload(client, "guard@bpe.co.id", "Guard123!")
        access_token = login_payload["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        assert login_payload["user"]["preferred_language"] == "en"
        assert login_payload["user"]["preferred_theme"] == "theme_2"

        me = client.get("/api/v1/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["data"]["preferred_language"] == "en"
        assert me.json()["data"]["preferred_theme"] == "theme_2"

        updated = client.put(
            "/api/v1/auth/preferences",
            headers=headers,
            json={
                "preferred_language": "id",
                "preferred_theme": "theme_5",
            },
        )
        assert updated.status_code == 200
        assert updated.json()["data"]["preferred_language"] == "id"
        assert updated.json()["data"]["preferred_theme"] == "theme_5"

        refreshed_me = client.get("/api/v1/auth/me", headers=headers)
        assert refreshed_me.status_code == 200
        assert refreshed_me.json()["data"]["preferred_language"] == "id"
        assert refreshed_me.json()["data"]["preferred_theme"] == "theme_5"


def test_company_default_preferences_can_be_updated_and_auth_fallback_uses_user_company_then_system():
    with _bootstrap_app() as client:
        owner_login = _login_payload(client, "owner@bpe.co.id", "Admin123!")
        owner_headers = {"Authorization": f"Bearer {owner_login['access_token']}"}
        guard_login = _login_payload(client, "guard@bpe.co.id", "Guard123!")
        guard_headers = {"Authorization": f"Bearer {guard_login['access_token']}"}

        companies = client.get("/api/v1/organization/companies", headers=owner_headers)
        assert companies.status_code == 200
        company_by_code = {item["code"]: item for item in companies.json()["data"]}
        primary_company = company_by_code["BPE-HQ"]
        assert primary_company["default_language"] == "en"
        assert primary_company["default_theme"] == "theme_4"

        updated_settings = client.put(
            f"/api/v1/organization/companies/{primary_company['id']}/settings",
            headers=owner_headers,
            json={
                "default_language": " id ",
                "default_theme": " THEME_5 ",
            },
        )
        assert updated_settings.status_code == 200
        assert updated_settings.json()["data"]["default_language"] == "id"
        assert updated_settings.json()["data"]["default_theme"] == "theme_5"

        owner_me = client.get("/api/v1/auth/me", headers=owner_headers)
        assert owner_me.status_code == 200
        assert owner_me.json()["data"]["preferred_language"] == "id"
        assert owner_me.json()["data"]["preferred_theme"] == "theme_5"

        guard_me = client.get("/api/v1/auth/me", headers=guard_headers)
        assert guard_me.status_code == 200
        assert guard_me.json()["data"]["preferred_language"] == "en"
        assert guard_me.json()["data"]["preferred_theme"] == "theme_2"

        with session_scope() as session:
            session.add(
                User(
                    username="system.fallback",
                    email="system.fallback@bpe.co.id",
                    password_hash=hash_password("Fallback123!"),
                    is_active=True,
                )
            )
            session.commit()

        system_fallback = _login_payload(
            client,
            "system.fallback@bpe.co.id",
            "Fallback123!",
        )
        assert system_fallback["user"]["preferred_language"] == "id"
        assert system_fallback["user"]["preferred_theme"] == "theme_1"


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


def test_selfie_validation_service_enforces_image_like_photo_for_selfie_method():
    with _bootstrap_app() as client:
        guard_token, _ = _login(client, "guard@bpe.co.id", "Guard123!")
        guard_headers = {"Authorization": f"Bearer {guard_token}"}

        schedules = client.get("/api/v1/workforce-operations/work-schedules", headers=guard_headers)
        assert schedules.status_code == 200
        schedule = schedules.json()["data"][0]

        invalid_selfie = client.post(
            "/api/v1/attendance/check-in",
            headers=guard_headers,
            json={
                "work_schedule_id": schedule["id"],
                "latitude": "-6.200000",
                "longitude": "106.816666",
                "method": "gps_selfie",
                "photo_path": "attendance/selfie/emp-0001.txt",
            },
        )
        assert invalid_selfie.status_code == 400

        valid_selfie = client.post(
            "/api/v1/attendance/check-in",
            headers=guard_headers,
            json={
                "work_schedule_id": schedule["id"],
                "latitude": "-6.200000",
                "longitude": "106.816666",
                "method": "gps_selfie",
                "photo_path": "attendance/selfie/emp-0001-check-in.jpg",
            },
        )
        assert valid_selfie.status_code == 200
        assert valid_selfie.json()["data"]["check_in_method"] == "gps_selfie"
        assert valid_selfie.json()["data"]["face_valid_flag"] is True


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


def test_qr_attendance_uses_separate_session_and_endpoint():
    with _bootstrap_app() as client:
        guard_token, _ = _login(client, "guard@bpe.co.id", "Guard123!")
        owner_token, _ = _login(client, "owner@bpe.co.id", "Admin123!")
        guard_headers = {"Authorization": f"Bearer {guard_token}"}
        owner_headers = {"Authorization": f"Bearer {owner_token}"}

        schedules = client.get("/api/v1/workforce-operations/work-schedules", headers=guard_headers)
        assert schedules.status_code == 200
        schedule = schedules.json()["data"][0]

        direct_qr = client.post(
            "/api/v1/attendance/check-in",
            headers=guard_headers,
            json={
                "work_schedule_id": schedule["id"],
                "method": "qr",
            },
        )
        assert direct_qr.status_code == 400

        qr_check_in_session = client.post(
            "/api/v1/attendance/qr-sessions",
            headers=owner_headers,
            json={
                "work_schedule_id": schedule["id"],
                "attendance_action": "CHECK_IN",
                "expires_in_minutes": 10,
            },
        )
        assert qr_check_in_session.status_code == 200
        qr_check_in_token = qr_check_in_session.json()["data"]["qr_token"]
        assert qr_check_in_session.json()["data"]["attendance_action"] == "CHECK_IN"

        qr_check_in = client.post(
            "/api/v1/attendance/check-in/qr",
            headers=guard_headers,
            json={
                "qr_token": qr_check_in_token,
                "photo_path": "attendance/qr/emp-0001-check-in.png",
            },
        )
        assert qr_check_in.status_code == 200
        assert qr_check_in.json()["data"]["check_in_method"] == "qr_selfie"
        assert qr_check_in.json()["data"]["face_valid_flag"] is True

        reused_qr_check_in = client.post(
            "/api/v1/attendance/check-in/qr",
            headers=guard_headers,
            json={"qr_token": qr_check_in_token},
        )
        assert reused_qr_check_in.status_code == 409

        qr_check_out_session = client.post(
            "/api/v1/attendance/qr-sessions",
            headers=owner_headers,
            json={
                "work_schedule_id": schedule["id"],
                "attendance_action": "CHECK_OUT",
                "expires_in_minutes": 10,
            },
        )
        assert qr_check_out_session.status_code == 200

        qr_check_out = client.post(
            "/api/v1/attendance/check-out/qr",
            headers=guard_headers,
            json={"qr_token": qr_check_out_session.json()["data"]["qr_token"]},
        )
        assert qr_check_out.status_code == 200
        assert qr_check_out.json()["data"]["check_out_method"] == "qr"
        assert qr_check_out.json()["data"]["attendance_status"] == "COMPLETED"


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


def test_dashboard_reports_and_ops_summary_follow_site_scope_for_supervisor():
    with _bootstrap_app() as client:
        owner_token, _ = _login(client, "owner@bpe.co.id", "Admin123!")
        supervisor_token, supervisor_user = _login(
            client, "supervisor@bpe.co.id", "Supervisor123!"
        )
        guard_token, _ = _login(client, "guard@bpe.co.id", "Guard123!")
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        supervisor_headers = {"Authorization": f"Bearer {supervisor_token}"}
        guard_headers = {"Authorization": f"Bearer {guard_token}"}

        schedules = client.get("/api/v1/workforce-operations/work-schedules", headers=guard_headers)
        assert schedules.status_code == 200
        today_schedule = next(
            item for item in schedules.json()["data"] if item["scheduled_date"] == date.today().isoformat()
        )

        check_in = client.post(
            "/api/v1/attendance/check-in",
            headers=guard_headers,
            json={
                "work_schedule_id": today_schedule["id"],
                "latitude": "-6.200000",
                "longitude": "106.816666",
                "method": "gps_selfie",
                "photo_path": "attendance/selfie/emp-0001-check-in.jpg",
            },
        )
        assert check_in.status_code == 200

        owner_summary = client.get("/api/v1/dashboard/ops-summary", headers=owner_headers)
        supervisor_summary = client.get("/api/v1/dashboard/ops-summary", headers=supervisor_headers)
        assert owner_summary.status_code == 200
        assert supervisor_summary.status_code == 200

        assert owner_summary.json()["data"] == {
            "employees_total": 4,
            "clients_total": 2,
            "sites_total": 2,
            "active_deployments": 2,
            "schedules_today": 2,
            "attendance_today": 1,
        }
        assert supervisor_summary.json()["data"] == {
            "employees_total": 1,
            "clients_total": 1,
            "sites_total": 1,
            "active_deployments": 1,
            "schedules_today": 1,
            "attendance_today": 1,
        }

        employee_report = client.get(
            "/api/v1/dashboard/reports/employees",
            headers=supervisor_headers,
        )
        assert employee_report.status_code == 200
        assert employee_report.json()["data"]["total_employees"] == 1
        assert employee_report.json()["data"]["active_employees"] == 1
        assert employee_report.json()["data"]["by_branch"][0]["branch_name"] == "Head Office"
        assert employee_report.json()["data"]["by_branch"][0]["total"] == 1

        deployment_report = client.get(
            "/api/v1/dashboard/reports/deployments",
            headers=supervisor_headers,
        )
        assert deployment_report.status_code == 200
        assert deployment_report.json()["data"]["total_deployments"] == 1
        assert deployment_report.json()["data"]["active_deployments"] == 1
        assert deployment_report.json()["data"]["by_site"] == [
            {
                "client_site_id": supervisor_user["site_scope_ids"][0],
                "site_name": "Demo Site",
                "total": 1,
            }
        ]

        schedule_report = client.get(
            f"/api/v1/dashboard/reports/schedules?date_from={date.today().isoformat()}&date_to={date.today().isoformat()}",
            headers=supervisor_headers,
        )
        assert schedule_report.status_code == 200
        assert schedule_report.json()["data"]["total_schedules"] == 1
        assert schedule_report.json()["data"]["published_schedules"] == 1
        assert schedule_report.json()["data"]["approved_schedules"] == 0

        attendance_report = client.get(
            f"/api/v1/dashboard/reports/attendance?date_from={date.today().isoformat()}&date_to={date.today().isoformat()}",
            headers=supervisor_headers,
        )
        assert attendance_report.status_code == 200
        assert attendance_report.json()["data"]["total_attendance"] == 1
        assert attendance_report.json()["data"]["gps_valid_total"] == 1
        assert attendance_report.json()["data"]["geofence_valid_total"] == 1
        assert attendance_report.json()["data"]["face_valid_total"] == 1
        assert attendance_report.json()["data"]["by_site"] == [
            {
                "client_site_id": supervisor_user["site_scope_ids"][0],
                "site_name": "Demo Site",
                "total": 1,
            }
        ]


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


def test_company_unique_code_validation_is_case_insensitive_and_scoped_per_company():
    with _bootstrap_app() as client:
        owner_token, _ = _login(client, "owner@bpe.co.id", "Admin123!")
        owner_headers = {"Authorization": f"Bearer {owner_token}"}

        companies = client.get("/api/v1/organization/companies", headers=owner_headers)
        branches = client.get("/api/v1/organization/branches", headers=owner_headers)
        assert companies.status_code == 200
        assert branches.status_code == 200

        company_by_code = {item["code"]: item for item in companies.json()["data"]}
        branch_by_company = {item["company_id"]: item for item in branches.json()["data"]}
        primary_company = company_by_code["BPE-HQ"]
        secondary_company = company_by_code["BPE-SBY"]
        primary_branch = branch_by_company[primary_company["id"]]
        secondary_branch = branch_by_company[secondary_company["id"]]

        duplicate_branch = client.post(
            "/api/v1/organization/branches",
            headers=owner_headers,
            json={
                "company_id": primary_company["id"],
                "code": " hq ",
                "name": "Duplicate Head Office",
                "city": "Jakarta",
                "province": "DKI Jakarta",
            },
        )
        assert duplicate_branch.status_code == 409

        cross_company_branch = client.post(
            "/api/v1/organization/branches",
            headers=owner_headers,
            json={
                "company_id": secondary_company["id"],
                "code": " hq ",
                "name": "Surabaya HQ",
                "city": "Surabaya",
                "province": "Jawa Timur",
            },
        )
        assert cross_company_branch.status_code == 200
        assert cross_company_branch.json()["data"]["code"] == "HQ"

        duplicate_employee = client.post(
            "/api/v1/master-hr/employees",
            headers=owner_headers,
            json={
                "company_id": primary_company["id"],
                "branch_id": primary_branch["id"],
                "employee_number": " emp-0001 ",
                "full_name": "Duplicate Demo Guard",
                "employment_status": "contract",
            },
        )
        assert duplicate_employee.status_code == 409

        cross_company_employee = client.post(
            "/api/v1/master-hr/employees",
            headers=owner_headers,
            json={
                "company_id": secondary_company["id"],
                "branch_id": secondary_branch["id"],
                "employee_number": " emp-0001 ",
                "full_name": "Surabaya Guard 01",
                "employment_status": "contract",
                "employee_status": "ACTIVE",
            },
        )
        assert cross_company_employee.status_code == 200
        assert cross_company_employee.json()["data"]["employee_number"] == "EMP-0001"
        assert cross_company_employee.json()["data"]["company_id"] == secondary_company["id"]


def test_batch_import_employee_returns_per_row_result_and_continues_on_error():
    with _bootstrap_app() as client:
        owner_token, _ = _login(client, "owner@bpe.co.id", "Admin123!")
        owner_headers = {"Authorization": f"Bearer {owner_token}"}

        companies = client.get("/api/v1/organization/companies", headers=owner_headers)
        branches = client.get("/api/v1/organization/branches", headers=owner_headers)
        assert companies.status_code == 200
        assert branches.status_code == 200

        company_by_code = {item["code"]: item for item in companies.json()["data"]}
        branch_by_company = {item["company_id"]: item for item in branches.json()["data"]}
        primary_company = company_by_code["BPE-HQ"]
        secondary_company = company_by_code["BPE-SBY"]

        imported = client.post(
            "/api/v1/master-hr/employees/imports/batch",
            headers=owner_headers,
            json={
                "employees": [
                    {
                        "company_id": primary_company["id"],
                        "branch_id": branch_by_company[primary_company["id"]]["id"],
                        "employee_number": " emp-0200 ",
                        "full_name": "Batch Guard HQ",
                        "employment_status": "contract",
                    },
                    {
                        "company_id": primary_company["id"],
                        "branch_id": branch_by_company[primary_company["id"]]["id"],
                        "employee_number": " emp-0001 ",
                        "full_name": "Duplicate Guard HQ",
                        "employment_status": "contract",
                    },
                    {
                        "company_id": secondary_company["id"],
                        "branch_id": branch_by_company[secondary_company["id"]]["id"],
                        "employee_number": " emp-0200 ",
                        "full_name": "Batch Guard SBY",
                        "employment_status": "contract",
                    },
                ]
            },
        )
        assert imported.status_code == 200
        assert imported.json()["meta"]["requested_total"] == 3
        assert imported.json()["meta"]["created"] == 2
        assert imported.json()["meta"]["failed"] == 1
        assert imported.json()["meta"]["stopped_early"] is False

        row_statuses = [item["status"] for item in imported.json()["data"]]
        assert row_statuses == ["CREATED", "FAILED", "CREATED"]
        assert imported.json()["data"][0]["employee"]["employee_number"] == "EMP-0200"
        assert imported.json()["data"][1]["message"] == "Employee number sudah digunakan pada company ini."
        assert imported.json()["data"][2]["employee"]["company_id"] == secondary_company["id"]

        employees = client.get("/api/v1/master-hr/employees", headers=owner_headers)
        assert employees.status_code == 200
        imported_employee_keys = {
            (item["company_id"], item["employee_number"]) for item in employees.json()["data"]
        }
        assert (primary_company["id"], "EMP-0200") in imported_employee_keys
        assert (secondary_company["id"], "EMP-0200") in imported_employee_keys


def test_employee_lifecycle_events_update_employee_state_and_keep_history():
    with _bootstrap_app() as client:
        owner_token, _ = _login(client, "owner@bpe.co.id", "Admin123!")
        owner_headers = {"Authorization": f"Bearer {owner_token}"}

        employees = client.get("/api/v1/master-hr/employees", headers=owner_headers)
        branches = client.get("/api/v1/organization/branches", headers=owner_headers)
        assert employees.status_code == 200
        assert branches.status_code == 200

        employee_by_number = {
            item["employee_number"]: item for item in employees.json()["data"]
        }
        branch_by_code = {item["code"]: item for item in branches.json()["data"]}
        target_employee = employee_by_number["EMP-0002"]
        target_branch = branch_by_code["HQ"]

        transfer = client.post(
            f"/api/v1/master-hr/employees/{target_employee['id']}/lifecycle-events",
            headers=owner_headers,
            json={
                "action_type": "transfer",
                "effective_date": date.today().isoformat(),
                "new_branch_id": target_branch["id"],
                "remarks": "Mutasi ke head office",
            },
        )
        assert transfer.status_code == 200
        assert transfer.json()["data"]["event"]["action_type"] == "TRANSFER"
        assert transfer.json()["data"]["event"]["old_branch_id"] == target_employee["branch_id"]
        assert transfer.json()["data"]["employee"]["branch_id"] == target_branch["id"]
        assert transfer.json()["data"]["employee"]["employee_status"] == "ACTIVE"

        resign = client.post(
            f"/api/v1/master-hr/employees/{target_employee['id']}/lifecycle-events",
            headers=owner_headers,
            json={
                "action_type": "RESIGN",
                "effective_date": (date.today() + timedelta(days=1)).isoformat(),
                "remarks": "Pengunduran diri demo",
            },
        )
        assert resign.status_code == 200
        assert resign.json()["data"]["employee"]["employee_status"] == "RESIGNED"
        assert resign.json()["data"]["employee"]["resign_date"] == (
            date.today() + timedelta(days=1)
        ).isoformat()

        reactivate = client.post(
            f"/api/v1/master-hr/employees/{target_employee['id']}/lifecycle-events",
            headers=owner_headers,
            json={
                "action_type": "REACTIVATE",
                "effective_date": (date.today() + timedelta(days=2)).isoformat(),
                "new_employment_status": "PERMANENT",
                "remarks": "Aktivasi ulang demo",
            },
        )
        assert reactivate.status_code == 200
        assert reactivate.json()["data"]["employee"]["employee_status"] == "ACTIVE"
        assert reactivate.json()["data"]["employee"]["employment_status"] == "PERMANENT"
        assert reactivate.json()["data"]["employee"]["resign_date"] is None

        lifecycle_events = client.get(
            f"/api/v1/master-hr/employees/{target_employee['id']}/lifecycle-events",
            headers=owner_headers,
        )
        assert lifecycle_events.status_code == 200
        assert lifecycle_events.json()["meta"]["total"] == 3
        action_types = [item["action_type"] for item in lifecycle_events.json()["data"]]
        assert action_types == ["REACTIVATE", "RESIGN", "TRANSFER"]


def test_employee_emergency_contacts_and_documents_follow_employee_scope():
    with _bootstrap_app() as client:
        owner_token, _ = _login(client, "owner@bpe.co.id", "Admin123!")
        hr_token, _ = _login(client, "hr.branch@bpe.co.id", "HrBranch123!")
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        hr_headers = {"Authorization": f"Bearer {hr_token}"}

        employees = client.get("/api/v1/master-hr/employees", headers=owner_headers)
        assert employees.status_code == 200
        employee_by_number = {
            item["employee_number"]: item for item in employees.json()["data"]
        }
        in_scope_employee = employee_by_number["EMP-0001"]
        out_of_scope_employee = employee_by_number["EMP-0002"]

        created_contact = client.post(
            f"/api/v1/master-hr/employees/{in_scope_employee['id']}/emergency-contacts",
            headers=hr_headers,
            json={
                "contact_name": "Ibu Guard",
                "relationship_type": "PARENT",
                "phone": "081299999999",
                "alternate_phone": "081288888888",
                "email": "ibu.guard@bpe.co.id",
                "address": "Bekasi",
                "is_primary": True,
                "notes": "Kontak utama darurat",
            },
        )
        assert created_contact.status_code == 200
        assert created_contact.json()["data"]["employee_id"] == in_scope_employee["id"]
        assert created_contact.json()["data"]["is_primary"] is True

        listed_contacts = client.get(
            f"/api/v1/master-hr/employees/{in_scope_employee['id']}/emergency-contacts",
            headers=hr_headers,
        )
        assert listed_contacts.status_code == 200
        assert listed_contacts.json()["meta"]["total"] == 1
        assert listed_contacts.json()["data"][0]["contact_name"] == "Ibu Guard"

        created_document = client.post(
            f"/api/v1/master-hr/employees/{in_scope_employee['id']}/documents",
            headers=hr_headers,
            json={
                "document_type": "ID_CARD",
                "document_name": "KTP Demo Guard",
                "file_path": "employee-documents/emp-0001/ktp.jpg",
                "document_number": "3171000000000001",
                "issued_date": date.today().isoformat(),
                "active_flag": True,
                "notes": "Dokumen onboarding",
            },
        )
        assert created_document.status_code == 200
        assert created_document.json()["data"]["employee_id"] == in_scope_employee["id"]
        assert created_document.json()["data"]["document_type"] == "ID_CARD"

        listed_documents = client.get(
            f"/api/v1/master-hr/employees/{in_scope_employee['id']}/documents",
            headers=hr_headers,
        )
        assert listed_documents.status_code == 200
        assert listed_documents.json()["meta"]["total"] == 1
        assert listed_documents.json()["data"][0]["document_name"] == "KTP Demo Guard"

        denied_contact = client.get(
            f"/api/v1/master-hr/employees/{out_of_scope_employee['id']}/emergency-contacts",
            headers=hr_headers,
        )
        assert denied_contact.status_code == 403

        denied_document = client.post(
            f"/api/v1/master-hr/employees/{out_of_scope_employee['id']}/documents",
            headers=hr_headers,
            json={
                "document_type": "CERTIFICATE",
                "document_name": "Out of Scope",
                "file_path": "employee-documents/emp-0002/cert.pdf",
            },
        )
        assert denied_document.status_code == 403


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


def test_core_detail_and_update_endpoints_support_basic_ui_workflow():
    with _bootstrap_app() as client:
        owner_token, _ = _login(client, "owner@bpe.co.id", "Admin123!")
        owner_headers = {"Authorization": f"Bearer {owner_token}"}

        employees = client.get("/api/v1/master-hr/employees", headers=owner_headers)
        clients = client.get("/api/v1/client-contract/clients", headers=owner_headers)
        sites = client.get("/api/v1/site-operations/sites", headers=owner_headers)
        posts = client.get("/api/v1/site-operations/posts", headers=owner_headers)
        deployments = client.get("/api/v1/workforce-operations/deployments", headers=owner_headers)
        schedules = client.get("/api/v1/workforce-operations/work-schedules", headers=owner_headers)

        assert employees.status_code == 200
        assert clients.status_code == 200
        assert sites.status_code == 200
        assert posts.status_code == 200
        assert deployments.status_code == 200
        assert schedules.status_code == 200

        employee = next(
            item for item in employees.json()["data"] if item["employee_number"] == "EMP-0001"
        )
        client_item = next(
            item for item in clients.json()["data"] if item["code"] == "CLI-DEMO"
        )
        site = next(item for item in sites.json()["data"] if item["code"] == "SITE-DEMO")
        post = next(item for item in posts.json()["data"] if item["code"] == "POST-A")
        deployment = next(
            item for item in deployments.json()["data"] if item["employee_id"] == employee["id"]
        )
        schedule = next(
            item for item in schedules.json()["data"] if item["employee_id"] == employee["id"]
        )

        employee_detail = client.get(
            f"/api/v1/master-hr/employees/{employee['id']}",
            headers=owner_headers,
        )
        assert employee_detail.status_code == 200
        assert employee_detail.json()["data"]["full_name"] == "Demo Guard"

        updated_employee = client.put(
            f"/api/v1/master-hr/employees/{employee['id']}",
            headers=owner_headers,
            json={
                "phone": "081299999999",
                "address": "Jakarta Selatan",
            },
        )
        assert updated_employee.status_code == 200
        assert updated_employee.json()["data"]["phone"] == "081299999999"
        assert updated_employee.json()["data"]["address"] == "Jakarta Selatan"

        client_detail = client.get(
            f"/api/v1/client-contract/clients/{client_item['id']}",
            headers=owner_headers,
        )
        assert client_detail.status_code == 200
        assert client_detail.json()["data"]["name"] == "Demo Client"

        updated_client = client.put(
            f"/api/v1/client-contract/clients/{client_item['id']}",
            headers=owner_headers,
            json={
                "contact_person_name": "PIC Demo Updated",
                "billing_address": "Jakarta Selatan",
            },
        )
        assert updated_client.status_code == 200
        assert updated_client.json()["data"]["contact_person_name"] == "PIC Demo Updated"
        assert updated_client.json()["data"]["billing_address"] == "Jakarta Selatan"

        site_detail = client.get(
            f"/api/v1/site-operations/sites/{site['id']}",
            headers=owner_headers,
        )
        assert site_detail.status_code == 200
        assert site_detail.json()["data"]["name"] == "Demo Site"

        updated_site = client.put(
            f"/api/v1/site-operations/sites/{site['id']}",
            headers=owner_headers,
            json={
                "city": "Jakarta Selatan",
                "radius_meters": 175,
            },
        )
        assert updated_site.status_code == 200
        assert updated_site.json()["data"]["city"] == "Jakarta Selatan"
        assert updated_site.json()["data"]["radius_meters"] == 175

        post_detail = client.get(
            f"/api/v1/site-operations/posts/{post['id']}",
            headers=owner_headers,
        )
        assert post_detail.status_code == 200
        assert post_detail.json()["data"]["name"] == "Main Gate"

        updated_post = client.put(
            f"/api/v1/site-operations/posts/{post['id']}",
            headers=owner_headers,
            json={
                "description": "Main gate updated for UI detail testing",
            },
        )
        assert updated_post.status_code == 200
        assert (
            updated_post.json()["data"]["description"]
            == "Main gate updated for UI detail testing"
        )

        deployment_detail = client.get(
            f"/api/v1/workforce-operations/deployments/{deployment['id']}",
            headers=owner_headers,
        )
        assert deployment_detail.status_code == 200
        assert deployment_detail.json()["data"]["employee_id"] == employee["id"]

        updated_deployment = client.put(
            f"/api/v1/workforce-operations/deployments/{deployment['id']}",
            headers=owner_headers,
            json={
                "source_type": "manual_update",
                "notes": "Updated deployment note for basic UI",
            },
        )
        assert updated_deployment.status_code == 200
        assert updated_deployment.json()["data"]["source_type"] == "manual_update"
        assert (
            updated_deployment.json()["data"]["notes"]
            == "Updated deployment note for basic UI"
        )

        schedule_detail = client.get(
            f"/api/v1/workforce-operations/work-schedules/{schedule['id']}",
            headers=owner_headers,
        )
        assert schedule_detail.status_code == 200
        assert schedule_detail.json()["data"]["employee_id"] == employee["id"]

        updated_schedule = client.put(
            f"/api/v1/workforce-operations/work-schedules/{schedule['id']}",
            headers=owner_headers,
            json={
                "scheduled_start_datetime": f"{schedule['scheduled_date']}T08:00:00Z",
                "scheduled_end_datetime": f"{schedule['scheduled_date']}T16:00:00Z",
            },
        )
        assert updated_schedule.status_code == 200
        assert updated_schedule.json()["data"]["scheduled_start_datetime"].startswith(
            f"{schedule['scheduled_date']}T08:00:00"
        )
        assert updated_schedule.json()["data"]["scheduled_end_datetime"].startswith(
            f"{schedule['scheduled_date']}T16:00:00"
        )


def test_my_schedules_exposes_guard_contract_only_for_self_and_published_schedules():
    with _bootstrap_app() as client:
        owner_token, _ = _login(client, "owner@bpe.co.id", "Admin123!")
        guard_token, guard_user = _login(client, "guard@bpe.co.id", "Guard123!")
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        guard_headers = {"Authorization": f"Bearer {guard_token}"}

        my_schedules = client.get("/api/v1/my/schedules", headers=guard_headers)
        assert my_schedules.status_code == 200
        assert my_schedules.json()["meta"]["total"] == 1
        assert all(
            item["employee_id"] == guard_user["employee_id"]
            for item in my_schedules.json()["data"]
        )

        deployments = client.get("/api/v1/workforce-operations/deployments", headers=owner_headers)
        shift_types = client.get("/api/v1/workforce-operations/shift-types", headers=owner_headers)
        assert deployments.status_code == 200
        assert shift_types.status_code == 200

        guard_deployment = next(
            item
            for item in deployments.json()["data"]
            if item["employee_id"] == guard_user["employee_id"]
        )
        draft_schedule = client.post(
            "/api/v1/workforce-operations/work-schedules",
            headers=owner_headers,
            json={
                "employee_deployment_id": guard_deployment["id"],
                "shift_type_id": shift_types.json()["data"][0]["id"],
                "scheduled_date": (date.today() + timedelta(days=3)).isoformat(),
                "schedule_status": "DRAFT",
            },
        )
        assert draft_schedule.status_code == 200

        refreshed_my_schedules = client.get("/api/v1/my/schedules", headers=guard_headers)
        assert refreshed_my_schedules.status_code == 200
        my_schedule_ids = {item["id"] for item in refreshed_my_schedules.json()["data"]}
        assert draft_schedule.json()["data"]["id"] not in my_schedule_ids

        owner_my_schedules = client.get("/api/v1/my/schedules", headers=owner_headers)
        assert owner_my_schedules.status_code == 403


def test_detail_routes_respect_scope_and_attendance_detail_is_available():
    with _bootstrap_app() as client:
        owner_token, _ = _login(client, "owner@bpe.co.id", "Admin123!")
        supervisor_token, supervisor_user = _login(
            client, "supervisor@bpe.co.id", "Supervisor123!"
        )
        guard_token, _ = _login(client, "guard@bpe.co.id", "Guard123!")
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        supervisor_headers = {"Authorization": f"Bearer {supervisor_token}"}
        guard_headers = {"Authorization": f"Bearer {guard_token}"}

        sites = client.get("/api/v1/site-operations/sites", headers=owner_headers)
        assert sites.status_code == 200
        other_site = next(
            item
            for item in sites.json()["data"]
            if item["id"] != supervisor_user["site_scope_ids"][0]
        )

        denied_site_detail = client.get(
            f"/api/v1/site-operations/sites/{other_site['id']}",
            headers=supervisor_headers,
        )
        assert denied_site_detail.status_code == 403

        schedules = client.get("/api/v1/workforce-operations/work-schedules", headers=guard_headers)
        assert schedules.status_code == 200
        today_schedule = next(
            item for item in schedules.json()["data"] if item["scheduled_date"] == date.today().isoformat()
        )

        checked_in = client.post(
            "/api/v1/attendance/check-in",
            headers=guard_headers,
            json={
                "work_schedule_id": today_schedule["id"],
                "latitude": "-6.200000",
                "longitude": "106.816666",
                "method": "gps",
            },
        )
        assert checked_in.status_code == 200

        checked_out = client.post(
            "/api/v1/attendance/check-out",
            headers=guard_headers,
            json={
                "work_schedule_id": today_schedule["id"],
                "latitude": "-6.200000",
                "longitude": "106.816666",
                "method": "gps",
            },
        )
        assert checked_out.status_code == 200
        attendance_id = checked_out.json()["data"]["id"]

        attendance_detail = client.get(
            f"/api/v1/attendance/records/{attendance_id}",
            headers=owner_headers,
        )
        assert attendance_detail.status_code == 200
        assert attendance_detail.json()["data"]["id"] == attendance_id
        assert attendance_detail.json()["data"]["attendance_status"] == "COMPLETED"
