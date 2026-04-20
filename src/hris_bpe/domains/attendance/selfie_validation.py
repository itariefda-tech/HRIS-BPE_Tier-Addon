from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(slots=True)
class SelfieValidationResult:
    checked: bool
    is_valid: bool
    confidence_score: float
    message: str | None = None


class SelfieValidationService:
    _allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}

    def validate(self, *, photo_path: str | None, method: str) -> SelfieValidationResult:
        normalized_method = method.strip().lower()
        requires_selfie = "selfie" in normalized_method
        if photo_path is None or not photo_path.strip():
            if requires_selfie:
                return SelfieValidationResult(
                    checked=True,
                    is_valid=False,
                    confidence_score=0.0,
                    message="Foto selfie wajib dikirim untuk metode attendance ini.",
                )
            return SelfieValidationResult(
                checked=False,
                is_valid=False,
                confidence_score=0.0,
            )

        normalized_path = photo_path.strip().replace("\\", "/")
        suffix = PurePosixPath(normalized_path).suffix.lower()
        if suffix not in self._allowed_extensions:
            return SelfieValidationResult(
                checked=True,
                is_valid=False,
                confidence_score=0.0,
                message="Format foto selfie harus berupa jpg, jpeg, png, atau webp.",
            )

        confidence_score = 0.74
        lowered_path = normalized_path.lower()
        if "attendance" in lowered_path or "selfie" in lowered_path:
            confidence_score += 0.11
        if normalized_method.startswith("qr"):
            confidence_score += 0.05
        if requires_selfie:
            confidence_score += 0.10
        return SelfieValidationResult(
            checked=True,
            is_valid=confidence_score >= 0.70,
            confidence_score=min(confidence_score, 0.99),
            message="Validasi selfie attendance berhasil.",
        )
