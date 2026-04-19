from __future__ import annotations

from collections.abc import Callable, Iterable

from fastapi import HTTPException, status

from hris_bpe.common.dependencies import CurrentUserContext


def has_unscoped_permission(
    current_user: CurrentUserContext, permission_code: str
) -> bool:
    return permission_code in current_user.permission_codes and not current_user.has_explicit_scope


def resolve_company_scope_ids(current_user: CurrentUserContext) -> set[int]:
    if current_user.company_scope_ids:
        return set(current_user.company_scope_ids)
    return set(current_user.company_ids)


def filter_items_by_company_scope(
    current_user: CurrentUserContext,
    items: Iterable,
    company_id_getter: Callable[[object], int | None],
):
    allowed_company_ids = resolve_company_scope_ids(current_user)
    if not allowed_company_ids:
        return list(items)
    return [
        item
        for item in items
        if company_id_getter(item) in allowed_company_ids
    ]


def ensure_company_access(
    current_user: CurrentUserContext,
    company_id: int | None,
    *,
    detail: str = "Resource company tidak berada dalam scope user.",
) -> None:
    allowed_company_ids = resolve_company_scope_ids(current_user)
    if company_id is None or not allowed_company_ids:
        return
    if company_id not in allowed_company_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
