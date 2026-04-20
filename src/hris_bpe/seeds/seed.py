from __future__ import annotations

from datetime import date, datetime, time, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from hris_bpe.common.security import hash_password
from hris_bpe.config.settings import get_settings
from hris_bpe.domains.access_control.models import (
    Permission,
    Role,
    RolePermission,
    User,
    UserRole,
    UserScopeAccess,
)
from hris_bpe.domains.client_contract.models import Client, ClientContract
from hris_bpe.domains.master_hr.models import Employee, GuardProfile
from hris_bpe.domains.organization.models import Branch, Company, Department, Position
from hris_bpe.domains.product_control.models import (
    CompanyFeatureModule,
    CompanySubscription,
    FeatureModule,
    ProductTier,
)
from hris_bpe.domains.site_operations.models import ClientSite, SitePost
from hris_bpe.domains.workforce_operations.models import (
    DeploymentHistory,
    EmployeeDeployment,
    ShiftType,
    WorkSchedule,
)


PHASE_ONE_PERMISSION_SEEDS = [
    ("product_control.read", "Read product tiers and feature modules", "product_control"),
    ("companies.read", "Read companies", "organization"),
    ("companies.manage", "Manage companies", "organization"),
    ("branches.read", "Read branches", "organization"),
    ("branches.manage", "Manage branches", "organization"),
    ("departments.read", "Read departments", "organization"),
    ("departments.manage", "Manage departments", "organization"),
    ("positions.read", "Read positions", "organization"),
    ("positions.manage", "Manage positions", "organization"),
    ("users.read", "Read users", "access_control"),
    ("users.manage", "Manage users", "access_control"),
    ("users.assign_roles", "Assign roles to users", "access_control"),
    ("roles.read", "Read roles", "access_control"),
    ("roles.manage", "Manage roles", "access_control"),
    ("permissions.read", "Read permissions", "access_control"),
    ("employees.read", "Read employees", "master_hr"),
    ("employees.manage", "Manage employees", "master_hr"),
    ("guards.manage", "Manage guard profiles", "master_hr"),
    ("employee_contracts.manage", "Manage employee contracts", "master_hr"),
    ("clients.read", "Read clients", "client_contract"),
    ("clients.manage", "Manage clients", "client_contract"),
    ("client_contracts.read", "Read client contracts", "client_contract"),
    ("client_contracts.manage", "Manage client contracts", "client_contract"),
    ("sites.read", "Read client sites", "site_operations"),
    ("sites.manage", "Manage client sites", "site_operations"),
    ("site_posts.read", "Read site posts", "site_operations"),
    ("site_posts.manage", "Manage site posts", "site_operations"),
    ("deployments.read", "Read deployments", "workforce_operations"),
    ("deployments.manage", "Manage deployments", "workforce_operations"),
    ("shift_types.read", "Read shift types", "workforce_operations"),
    ("shift_types.manage", "Manage shift types", "workforce_operations"),
    ("schedules.read", "Read work schedules", "workforce_operations"),
    ("schedules.manage", "Manage work schedules", "workforce_operations"),
    ("attendance.read", "Read attendance", "attendance"),
    ("attendance.manage", "Manage attendance", "attendance"),
    ("attendance.self_service", "Use self-service attendance", "attendance"),
    ("dashboard.read", "Read operational dashboard", "dashboard"),
]

ROLE_PERMISSION_MAP = {
    "company_owner": [code for code, _, _ in PHASE_ONE_PERMISSION_SEEDS],
    "hr_admin": [
        "companies.read",
        "branches.read",
        "departments.read",
        "positions.read",
        "users.read",
        "users.manage",
        "users.assign_roles",
        "roles.read",
        "permissions.read",
        "employees.read",
        "employees.manage",
        "guards.manage",
        "employee_contracts.manage",
        "attendance.read",
        "dashboard.read",
        "product_control.read",
    ],
    "ops_supervisor": [
        "companies.read",
        "branches.read",
        "employees.read",
        "clients.read",
        "client_contracts.read",
        "sites.read",
        "sites.manage",
        "site_posts.read",
        "site_posts.manage",
        "deployments.read",
        "deployments.manage",
        "shift_types.read",
        "shift_types.manage",
        "schedules.read",
        "schedules.manage",
        "attendance.read",
        "attendance.manage",
        "dashboard.read",
        "product_control.read",
    ],
    "guard": [
        "attendance.self_service",
        "schedules.read",
        "attendance.read",
        "dashboard.read",
        "product_control.read",
    ],
}


FEATURE_MODULES = [
    ("ORG_BASIC", "Organization & Branch Basic", "core", "BASIC", False),
    ("ACCESS_BASIC", "User, Role & Permission Basic", "core", "BASIC", False),
    ("EMPLOYEE_MASTER", "Employee & Guard Master", "core", "BASIC", False),
    ("CLIENT_SITE_BASIC", "Client, Contract, Site & Post Basic", "core", "BASIC", False),
    ("DEPLOYMENT_BASIC", "Deployment Management", "core", "BASIC", False),
    ("SHIFT_SCHEDULE_BASIC", "Shift & Schedule Basic", "core", "BASIC", False),
    ("ATTENDANCE_BASIC", "Attendance Basic", "core", "BASIC", False),
    ("DASHBOARD_BASIC", "Dashboard Basic", "core", "BASIC", False),
    ("LEAVE_REPLACEMENT", "Leave & Replacement", "core", "PRO", False),
    ("PATROL_BASIC", "Patrol Basic", "core", "PRO", False),
    ("INCIDENT_BASIC", "Incident Basic", "core", "PRO", False),
    ("PAYROLL_BASIC", "Payroll Basic", "core", "PRO", False),
    ("BILLING_FOUNDATION", "Billing Foundation", "enterprise", "ENTERPRISE", False),
    ("AUDIT_FOUNDATION", "Audit Foundation", "enterprise", "ENTERPRISE", False),
    ("INTEGRATION_FOUNDATION", "Integration Foundation", "integration", "ENTERPRISE", False),
    ("PORTAL_FOUNDATION", "Portal Foundation", "enterprise", "ENTERPRISE", False),
]


def _get_or_create(session: Session, model, defaults: dict | None = None, **filters):
    instance = session.execute(select(model).filter_by(**filters)).scalar_one_or_none()
    if instance is not None:
        return instance
    payload = dict(filters)
    if defaults:
        payload.update(defaults)
    instance = model(**payload)
    session.add(instance)
    session.flush()
    return instance


def seed_reference_data(session: Session) -> None:
    settings = get_settings()

    tier_basic = _get_or_create(
        session,
        ProductTier,
        code="BASIC",
        defaults={"name": "Basic", "description": "Foundation tier", "sort_order": 1},
    )
    tier_pro = _get_or_create(
        session,
        ProductTier,
        code="PRO",
        defaults={"name": "Pro", "description": "Operational control tier", "sort_order": 2},
    )
    tier_enterprise = _get_or_create(
        session,
        ProductTier,
        code="ENTERPRISE",
        defaults={
            "name": "Enterprise",
            "description": "Governance and billing tier",
            "sort_order": 3,
        },
    )
    tier_map = {
        "BASIC": tier_basic,
        "PRO": tier_pro,
        "ENTERPRISE": tier_enterprise,
    }

    for code, name, category, default_tier, is_add_on in FEATURE_MODULES:
        _get_or_create(
            session,
            FeatureModule,
            code=code,
            defaults={
                "name": name,
                "module_category": category,
                "default_tier_id": tier_map[default_tier].id,
                "is_add_on": is_add_on,
            },
        )

    company = _get_or_create(
        session,
        Company,
        code="BPE-HQ",
        defaults={
            "name": "BPE Demo Security",
            "legal_name": "PT BPE Demo Security",
            "tax_number": "00.000.000.0-000.000",
            "address": "Jakarta",
            "phone": "021000000",
            "email": "contact@bpe.co.id",
            "status": "ACTIVE",
        },
    )
    secondary_company = _get_or_create(
        session,
        Company,
        code="BPE-SBY",
        defaults={
            "name": "BPE Surabaya Security",
            "legal_name": "PT BPE Surabaya Security",
            "tax_number": "22.222.222.2-222.222",
            "address": "Surabaya",
            "phone": "031000000",
            "email": "surabaya@bpe.co.id",
            "status": "ACTIVE",
        },
    )
    branch = _get_or_create(
        session,
        Branch,
        company_id=company.id,
        code="HQ",
        defaults={
            "name": "Head Office",
            "address": "Jakarta",
            "city": "Jakarta",
            "province": "DKI Jakarta",
            "phone": "021000000",
            "status": "ACTIVE",
        },
    )
    _get_or_create(
        session,
        Branch,
        company_id=secondary_company.id,
        code="SBY",
        defaults={
            "name": "Surabaya Branch",
            "address": "Surabaya",
            "city": "Surabaya",
            "province": "Jawa Timur",
            "phone": "031000100",
            "status": "ACTIVE",
        },
    )
    branch_bekasi = _get_or_create(
        session,
        Branch,
        company_id=company.id,
        code="BKS",
        defaults={
            "name": "Bekasi Branch",
            "address": "Bekasi",
            "city": "Bekasi",
            "province": "Jawa Barat",
            "phone": "021000100",
            "status": "ACTIVE",
        },
    )
    department = _get_or_create(
        session,
        Department,
        company_id=company.id,
        code="OPS",
        defaults={"name": "Operations", "description": "Operational command"},
    )
    hr_department = _get_or_create(
        session,
        Department,
        company_id=company.id,
        code="HR",
        defaults={"name": "Human Resource", "description": "HR management"},
    )
    guard_position = _get_or_create(
        session,
        Position,
        company_id=company.id,
        code="SEC_GUARD",
        defaults={
            "name": "Security Guard",
            "category": "FIELD",
            "level_order": 1,
            "description": "Guard operational position",
        },
    )
    supervisor_position = _get_or_create(
        session,
        Position,
        company_id=company.id,
        code="OPS_SUP",
        defaults={
            "name": "Operations Supervisor",
            "category": "SUPERVISOR",
            "level_order": 2,
            "description": "Site operations supervisor",
        },
    )
    hr_position = _get_or_create(
        session,
        Position,
        company_id=company.id,
        code="HR_ADMIN",
        defaults={
            "name": "HR Admin",
            "category": "BACKOFFICE",
            "level_order": 2,
            "description": "HR and access control admin",
        },
    )

    subscription = _get_or_create(
        session,
        CompanySubscription,
        company_id=company.id,
        product_tier_id=tier_basic.id,
        defaults={
            "start_date": date.today(),
            "subscription_status": "ACTIVE",
            "notes": "Seeded basic subscription",
        },
    )

    for feature in session.execute(select(FeatureModule)).scalars().all():
        activation_type = "included"
        active_flag = feature.default_tier_id == tier_basic.id
        if feature.code in {"LEAVE_REPLACEMENT", "PATROL_BASIC", "INCIDENT_BASIC", "PAYROLL_BASIC"}:
            activation_type = "planned"
            active_flag = False
        if feature.code in {"BILLING_FOUNDATION", "AUDIT_FOUNDATION", "INTEGRATION_FOUNDATION", "PORTAL_FOUNDATION"}:
            activation_type = "planned"
            active_flag = False
        _get_or_create(
            session,
            CompanyFeatureModule,
            company_subscription_id=subscription.id,
            feature_module_id=feature.id,
            defaults={
                "activation_type": activation_type,
                "active_flag": active_flag,
                "notes": "Seeded feature activation state",
            },
        )

    for code, name, module_name in PHASE_ONE_PERMISSION_SEEDS:
        _get_or_create(
            session,
            Permission,
            code=code,
            defaults={"name": name, "module_name": module_name},
        )

    role_company_owner = _get_or_create(
        session,
        Role,
        company_id=company.id,
        code="company_owner",
        defaults={"name": "Company Owner", "description": "Primary owner role"},
    )
    role_company_owner_secondary = _get_or_create(
        session,
        Role,
        company_id=secondary_company.id,
        code="company_owner",
        defaults={"name": "Company Owner", "description": "Secondary owner role"},
    )
    role_hr_admin = _get_or_create(
        session,
        Role,
        company_id=company.id,
        code="hr_admin",
        defaults={"name": "HR Admin", "description": "HR management role"},
    )
    role_ops_supervisor = _get_or_create(
        session,
        Role,
        company_id=company.id,
        code="ops_supervisor",
        defaults={"name": "Ops Supervisor", "description": "Operational supervisor role"},
    )
    role_guard = _get_or_create(
        session,
        Role,
        company_id=company.id,
        code="guard",
        defaults={"name": "Guard", "description": "Field guard role"},
    )
    roles_by_code = {
        role_company_owner.code: role_company_owner,
        role_hr_admin.code: role_hr_admin,
        role_ops_supervisor.code: role_ops_supervisor,
        role_guard.code: role_guard,
    }

    permission_map = {
        permission.code: permission
        for permission in session.execute(select(Permission)).scalars().all()
    }
    for role_code, permission_codes in ROLE_PERMISSION_MAP.items():
        role = roles_by_code[role_code]
        for permission_code in permission_codes:
            _get_or_create(
                session,
                RolePermission,
                role_id=role.id,
                permission_id=permission_map[permission_code].id,
            )
    for permission_code in ROLE_PERMISSION_MAP["company_owner"]:
        _get_or_create(
            session,
            RolePermission,
            role_id=role_company_owner_secondary.id,
            permission_id=permission_map[permission_code].id,
        )

    owner_user = _get_or_create(
        session,
        User,
        email=settings.seed_admin_email,
        defaults={
            "username": "company.owner",
            "phone": "081111111111",
            "password_hash": hash_password(settings.seed_admin_password),
            "is_active": True,
        },
    )
    _get_or_create(session, UserRole, user_id=owner_user.id, role_id=role_company_owner.id)
    _get_or_create(session, UserRole, user_id=owner_user.id, role_id=role_company_owner_secondary.id)

    company_scope_user = _get_or_create(
        session,
        User,
        email=settings.seed_company_scope_email,
        defaults={
            "username": "company.scope",
            "phone": "081777777777",
            "password_hash": hash_password(settings.seed_company_scope_password),
            "is_active": True,
        },
    )
    _get_or_create(session, UserRole, user_id=company_scope_user.id, role_id=role_company_owner.id)
    _get_or_create(
        session,
        UserRole,
        user_id=company_scope_user.id,
        role_id=role_company_owner_secondary.id,
    )

    guard_employee = _get_or_create(
        session,
        Employee,
        company_id=company.id,
        employee_number="EMP-0001",
        defaults={
            "branch_id": branch.id,
            "department_id": department.id,
            "position_id": guard_position.id,
            "full_name": "Demo Guard",
            "nik": "3171000000000001",
            "email": settings.seed_guard_email,
            "phone": "081222222222",
            "address": "Bekasi",
            "gender": "M",
            "marital_status": "single",
            "hire_date": date.today(),
            "employment_status": "permanent",
            "employee_status": "ACTIVE",
        },
    )
    _get_or_create(
        session,
        GuardProfile,
        employee_id=guard_employee.id,
        defaults={
            "guard_registration_number": "GAR-0001",
            "guard_level": "GADA_PRATAMA",
            "uniform_size": "L",
            "shoe_size": "42",
            "blood_type": "O",
            "firearm_license_flag": False,
            "driving_license_type": "A",
            "fitness_status": "FIT",
            "blacklist_flag": False,
        },
    )

    guard_user = _get_or_create(
        session,
        User,
        email=settings.seed_guard_email,
        defaults={
            "employee_id": guard_employee.id,
            "username": "demo.guard",
            "phone": guard_employee.phone,
            "password_hash": hash_password(settings.seed_guard_password),
            "preferred_language": "en",
            "preferred_theme": "theme_2",
            "is_active": True,
        },
    )
    if guard_user.employee_id != guard_employee.id:
        guard_user.employee_id = guard_employee.id
    _get_or_create(session, UserRole, user_id=guard_user.id, role_id=role_guard.id)

    supervisor_employee = _get_or_create(
        session,
        Employee,
        company_id=company.id,
        employee_number="EMP-0100",
        defaults={
            "branch_id": branch.id,
            "department_id": department.id,
            "position_id": supervisor_position.id,
            "full_name": "Demo Ops Supervisor",
            "nik": "3171000000000100",
            "email": settings.seed_supervisor_email,
            "phone": "081444444444",
            "address": "Jakarta",
            "gender": "M",
            "marital_status": "married",
            "hire_date": date.today(),
            "employment_status": "permanent",
            "employee_status": "ACTIVE",
        },
    )
    supervisor_user = _get_or_create(
        session,
        User,
        email=settings.seed_supervisor_email,
        defaults={
            "employee_id": supervisor_employee.id,
            "username": "ops.supervisor",
            "phone": supervisor_employee.phone,
            "password_hash": hash_password(settings.seed_supervisor_password),
            "is_active": True,
        },
    )
    if supervisor_user.employee_id != supervisor_employee.id:
        supervisor_user.employee_id = supervisor_employee.id
    _get_or_create(session, UserRole, user_id=supervisor_user.id, role_id=role_ops_supervisor.id)

    hr_employee = _get_or_create(
        session,
        Employee,
        company_id=company.id,
        employee_number="EMP-0101",
        defaults={
            "branch_id": branch.id,
            "department_id": hr_department.id,
            "position_id": hr_position.id,
            "full_name": "Demo HR Branch",
            "nik": "3171000000000101",
            "email": settings.seed_hr_branch_email,
            "phone": "081555555555",
            "address": "Jakarta",
            "gender": "F",
            "marital_status": "single",
            "hire_date": date.today(),
            "employment_status": "permanent",
            "employee_status": "ACTIVE",
        },
    )
    hr_user = _get_or_create(
        session,
        User,
        email=settings.seed_hr_branch_email,
        defaults={
            "employee_id": hr_employee.id,
            "username": "hr.branch",
            "phone": hr_employee.phone,
            "password_hash": hash_password(settings.seed_hr_branch_password),
            "is_active": True,
        },
    )
    if hr_user.employee_id != hr_employee.id:
        hr_user.employee_id = hr_employee.id
    _get_or_create(session, UserRole, user_id=hr_user.id, role_id=role_hr_admin.id)

    second_guard_employee = _get_or_create(
        session,
        Employee,
        company_id=company.id,
        employee_number="EMP-0002",
        defaults={
            "branch_id": branch_bekasi.id,
            "department_id": department.id,
            "position_id": guard_position.id,
            "full_name": "Demo Guard Bekasi",
            "nik": "3171000000000002",
            "email": "guard2@bpe.co.id",
            "phone": "081666666666",
            "address": "Bekasi",
            "gender": "M",
            "marital_status": "single",
            "hire_date": date.today(),
            "employment_status": "contract",
            "employee_status": "ACTIVE",
        },
    )
    _get_or_create(
        session,
        GuardProfile,
        employee_id=second_guard_employee.id,
        defaults={
            "guard_registration_number": "GAR-0002",
            "guard_level": "GADA_PRATAMA",
            "uniform_size": "L",
            "shoe_size": "42",
            "blood_type": "A",
            "firearm_license_flag": False,
            "driving_license_type": "C",
            "fitness_status": "FIT",
            "blacklist_flag": False,
        },
    )

    _get_or_create(
        session,
        Client,
        company_id=company.id,
        code="CLI-DEMO",
        defaults={
            "name": "Demo Client",
            "industry_type": "Security Outsourcing",
            "contact_person_name": "PIC Demo",
            "contact_person_phone": "081333333333",
            "contact_person_email": "pic@client.co.id",
            "billing_address": "Jakarta",
            "tax_number": "11.111.111.1-111.111",
            "status": "ACTIVE",
        },
    )
    _get_or_create(
        session,
        Client,
        company_id=secondary_company.id,
        code="CLI-SBY",
        defaults={
            "name": "Surabaya Client",
            "industry_type": "Security Outsourcing",
            "contact_person_name": "PIC SBY",
            "contact_person_phone": "081388888888",
            "contact_person_email": "pic.sby@client.co.id",
            "billing_address": "Surabaya",
            "tax_number": "33.333.333.3-333.333",
            "status": "ACTIVE",
        },
    )
    session.flush()
    demo_client = session.execute(select(Client).where(Client.code == "CLI-DEMO")).scalar_one()
    _get_or_create(
        session,
        ClientContract,
        client_id=demo_client.id,
        contract_number="CTR-DEMO-001",
        defaults={
            "contract_title": "Demo Security Service Contract",
            "start_date": date.today(),
            "contract_type": "annual",
            "currency": "IDR",
            "tax_included_flag": True,
            "payment_term_days": 30,
            "sla_description": "Phase 1 demo contract",
            "status": "ACTIVE",
        },
    )
    demo_contract = session.execute(
        select(ClientContract).where(ClientContract.contract_number == "CTR-DEMO-001")
    ).scalar_one()
    _get_or_create(
        session,
        ClientSite,
        client_id=demo_client.id,
        code="SITE-DEMO",
        defaults={
            "name": "Demo Site",
            "address": "Jakarta",
            "city": "Jakarta",
            "province": "DKI Jakarta",
            "latitude": Decimal("-6.200000"),
            "longitude": Decimal("106.816666"),
            "radius_meters": 150,
            "status": "ACTIVE",
        },
    )
    demo_site = session.execute(
        select(ClientSite).where(ClientSite.code == "SITE-DEMO")
    ).scalar_one()
    _get_or_create(
        session,
        ClientSite,
        client_id=demo_client.id,
        code="SITE-BKS",
        defaults={
            "name": "Bekasi Site",
            "address": "Bekasi",
            "city": "Bekasi",
            "province": "Jawa Barat",
            "latitude": Decimal("-6.234567"),
            "longitude": Decimal("107.001122"),
            "radius_meters": 120,
            "status": "ACTIVE",
        },
    )
    second_site = session.execute(
        select(ClientSite).where(ClientSite.code == "SITE-BKS")
    ).scalar_one()
    _get_or_create(
        session,
        SitePost,
        client_site_id=demo_site.id,
        code="POST-A",
        defaults={"name": "Main Gate", "description": "Primary entrance", "active_flag": True},
    )
    demo_post = session.execute(
        select(SitePost).where(SitePost.code == "POST-A")
    ).scalar_one()
    _get_or_create(
        session,
        SitePost,
        client_site_id=second_site.id,
        code="POST-B",
        defaults={"name": "Loading Dock", "description": "Secondary post", "active_flag": True},
    )
    second_post = session.execute(
        select(SitePost).where(SitePost.code == "POST-B")
    ).scalar_one()
    _get_or_create(
        session,
        ShiftType,
        company_id=company.id,
        code="SHIFT-PAGI",
        defaults={
            "name": "Shift Pagi",
            "start_time": time.fromisoformat("07:00"),
            "end_time": time.fromisoformat("15:00"),
            "cross_day_flag": False,
            "break_minutes": 60,
            "tolerance_late_minutes": 10,
            "overtime_after_minutes": 480,
        },
    )
    demo_shift = session.execute(
        select(ShiftType).where(ShiftType.code == "SHIFT-PAGI")
    ).scalar_one()
    _get_or_create(
        session,
        EmployeeDeployment,
        employee_id=guard_employee.id,
        client_id=demo_client.id,
        client_contract_id=demo_contract.id,
        client_site_id=demo_site.id,
        site_post_id=demo_post.id,
        defaults={
            "position_id": guard_position.id,
            "start_date": date.today(),
            "deployment_status": "ACTIVE",
            "source_type": "seed",
            "notes": "Seeded active deployment",
        },
    )
    demo_deployment = session.execute(
        select(EmployeeDeployment).where(EmployeeDeployment.employee_id == guard_employee.id)
    ).scalar_one()
    _get_or_create(
        session,
        EmployeeDeployment,
        employee_id=second_guard_employee.id,
        client_id=demo_client.id,
        client_contract_id=demo_contract.id,
        client_site_id=second_site.id,
        site_post_id=second_post.id,
        defaults={
            "position_id": guard_position.id,
            "start_date": date.today(),
            "deployment_status": "ACTIVE",
            "source_type": "seed",
            "notes": "Seeded secondary deployment",
        },
    )
    second_deployment = session.execute(
        select(EmployeeDeployment).where(EmployeeDeployment.employee_id == second_guard_employee.id)
    ).scalar_one()
    _get_or_create(
        session,
        UserScopeAccess,
        user_id=supervisor_user.id,
        scope_type="SITE",
        client_site_id=demo_site.id,
    )
    _get_or_create(
        session,
        UserScopeAccess,
        user_id=hr_user.id,
        scope_type="BRANCH",
        branch_id=branch.id,
    )
    _get_or_create(
        session,
        UserScopeAccess,
        user_id=company_scope_user.id,
        scope_type="COMPANY",
        company_id=company.id,
    )
    _get_or_create(
        session,
        DeploymentHistory,
        employee_deployment_id=demo_deployment.id,
        action_type="CREATE",
        action_date=demo_deployment.start_date,
        defaults={
            "old_client_site_id": None,
            "new_client_site_id": demo_site.id,
            "old_site_post_id": None,
            "new_site_post_id": demo_post.id,
            "remarks": "Seeded deployment history",
            "created_by": owner_user.id,
            "created_at": datetime.now(timezone.utc),
        },
    )
    _get_or_create(
        session,
        DeploymentHistory,
        employee_deployment_id=second_deployment.id,
        action_type="CREATE",
        action_date=second_deployment.start_date,
        defaults={
            "old_client_site_id": None,
            "new_client_site_id": second_site.id,
            "old_site_post_id": None,
            "new_site_post_id": second_post.id,
            "remarks": "Seeded deployment history",
            "created_by": owner_user.id,
            "created_at": datetime.now(timezone.utc),
        },
    )
    _get_or_create(
        session,
        WorkSchedule,
        employee_deployment_id=demo_deployment.id,
        scheduled_date=date.today(),
        defaults={
            "employee_id": guard_employee.id,
            "client_site_id": demo_site.id,
            "site_post_id": demo_post.id,
            "shift_type_id": demo_shift.id,
            "scheduled_start_datetime": datetime.combine(
                date.today(),
                time.fromisoformat("07:00"),
                tzinfo=timezone.utc,
            ),
            "scheduled_end_datetime": datetime.combine(
                date.today(),
                time.fromisoformat("15:00"),
                tzinfo=timezone.utc,
            ),
            "schedule_status": "PUBLISHED",
            "generated_by": owner_user.id,
            "approved_by": owner_user.id,
        },
    )
    _get_or_create(
        session,
        WorkSchedule,
        employee_deployment_id=second_deployment.id,
        scheduled_date=date.today(),
        defaults={
            "employee_id": second_guard_employee.id,
            "client_site_id": second_site.id,
            "site_post_id": second_post.id,
            "shift_type_id": demo_shift.id,
            "scheduled_start_datetime": datetime.combine(
                date.today(),
                time.fromisoformat("07:00"),
                tzinfo=timezone.utc,
            ),
            "scheduled_end_datetime": datetime.combine(
                date.today(),
                time.fromisoformat("15:00"),
                tzinfo=timezone.utc,
            ),
            "schedule_status": "PUBLISHED",
            "generated_by": owner_user.id,
            "approved_by": owner_user.id,
        },
    )

    session.commit()
