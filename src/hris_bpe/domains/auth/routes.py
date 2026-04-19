from fastapi import APIRouter, Depends

from hris_bpe.common.dependencies import CurrentUser, DbSession
from hris_bpe.common.responses import success_payload
from hris_bpe.domains.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
)
from hris_bpe.domains.auth.service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginRequest, db: DbSession):
    service = AuthService(db)
    result = service.login(payload)
    return success_payload("Login berhasil.", data=result.model_dump(mode="json"))


@router.get("/me")
def me(db: DbSession, current_user: CurrentUser):
    service = AuthService(db)
    return success_payload(
        "Profil user berhasil diambil.",
        data=service.me(current_user).model_dump(mode="json"),
    )


@router.post("/refresh")
def refresh_token(payload: RefreshTokenRequest, db: DbSession):
    service = AuthService(db)
    return success_payload(
        "Refresh token berhasil diproses.",
        data=service.refresh(payload).model_dump(mode="json"),
    )


@router.post("/logout")
def logout(db: DbSession, current_user: CurrentUser):
    service = AuthService(db)
    return success_payload(
        "Logout berhasil.",
        data=service.logout(current_user).model_dump(mode="json"),
    )


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    service = AuthService(db)
    return success_payload(
        "Password berhasil diperbarui.",
        data=service.change_password(current_user, payload).model_dump(mode="json"),
    )
