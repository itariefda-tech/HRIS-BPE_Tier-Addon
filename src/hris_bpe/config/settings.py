from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "HRIS-BPE Tier Addons API"
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    cors_allowed_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,http://10.144.110.126:3000"
    )
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change-this-in-production-at-least-32-characters"
    access_token_expire_minutes: int = 720
    refresh_token_expire_days: int = 7
    database_url: str = "sqlite:///./.data/hris_bpe.db"
    auto_migrate_on_startup: bool = False
    seed_admin_email: str = "owner@bpe.co.id"
    seed_admin_password: str = "Admin123!"
    seed_guard_email: str = "guard@bpe.co.id"
    seed_guard_password: str = "Guard123!"
    seed_supervisor_email: str = "supervisor@bpe.co.id"
    seed_supervisor_password: str = "Supervisor123!"
    seed_hr_branch_email: str = "hr.branch@bpe.co.id"
    seed_hr_branch_password: str = "HrBranch123!"
    seed_company_scope_email: str = "company.scope@bpe.co.id"
    seed_company_scope_password: str = "CompanyScope123!"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_allowed_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allowed_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", Settings.model_fields["app_name"].default),
        app_env=os.getenv("APP_ENV", Settings.model_fields["app_env"].default),
        app_debug=os.getenv("APP_DEBUG", "true").lower() in {"1", "true", "yes"},
        app_host=os.getenv("APP_HOST", Settings.model_fields["app_host"].default),
        app_port=int(os.getenv("APP_PORT", Settings.model_fields["app_port"].default)),
        cors_allowed_origins=os.getenv(
            "CORS_ALLOWED_ORIGINS",
            Settings.model_fields["cors_allowed_origins"].default,
        ),
        api_v1_prefix=os.getenv(
            "API_V1_PREFIX", Settings.model_fields["api_v1_prefix"].default
        ),
        secret_key=os.getenv("SECRET_KEY", Settings.model_fields["secret_key"].default),
        access_token_expire_minutes=int(
            os.getenv(
                "ACCESS_TOKEN_EXPIRE_MINUTES",
                Settings.model_fields["access_token_expire_minutes"].default,
            )
        ),
        refresh_token_expire_days=int(
            os.getenv(
                "REFRESH_TOKEN_EXPIRE_DAYS",
                Settings.model_fields["refresh_token_expire_days"].default,
            )
        ),
        database_url=os.getenv(
            "DATABASE_URL", Settings.model_fields["database_url"].default
        ),
        auto_migrate_on_startup=os.getenv(
            "AUTO_MIGRATE_ON_STARTUP", "false"
        ).lower()
        in {"1", "true", "yes"},
        seed_admin_email=os.getenv(
            "SEED_ADMIN_EMAIL", Settings.model_fields["seed_admin_email"].default
        ),
        seed_admin_password=os.getenv(
            "SEED_ADMIN_PASSWORD",
            Settings.model_fields["seed_admin_password"].default,
        ),
        seed_guard_email=os.getenv(
            "SEED_GUARD_EMAIL", Settings.model_fields["seed_guard_email"].default
        ),
        seed_guard_password=os.getenv(
            "SEED_GUARD_PASSWORD",
            Settings.model_fields["seed_guard_password"].default,
        ),
        seed_supervisor_email=os.getenv(
            "SEED_SUPERVISOR_EMAIL",
            Settings.model_fields["seed_supervisor_email"].default,
        ),
        seed_supervisor_password=os.getenv(
            "SEED_SUPERVISOR_PASSWORD",
            Settings.model_fields["seed_supervisor_password"].default,
        ),
        seed_hr_branch_email=os.getenv(
            "SEED_HR_BRANCH_EMAIL",
            Settings.model_fields["seed_hr_branch_email"].default,
        ),
        seed_hr_branch_password=os.getenv(
            "SEED_HR_BRANCH_PASSWORD",
            Settings.model_fields["seed_hr_branch_password"].default,
        ),
        seed_company_scope_email=os.getenv(
            "SEED_COMPANY_SCOPE_EMAIL",
            Settings.model_fields["seed_company_scope_email"].default,
        ),
        seed_company_scope_password=os.getenv(
            "SEED_COMPANY_SCOPE_PASSWORD",
            Settings.model_fields["seed_company_scope_password"].default,
        ),
    )
