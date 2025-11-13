"""Verification utilities for identity and property validation."""
from __future__ import annotations

from datetime import date

from app.models import IdentityVerification, PropertyContractVerification


class FacialVerificationService:
    """Stub that simulates biometric verification against an external provider."""

    def verify(self, selfie_reference: str) -> IdentityVerification:
        # In a real integration, this method would send `selfie_reference` to a
        # biometric provider and parse the response.
        return IdentityVerification(
            verified=True,
            last_checked_at=date.today(),
            provider_reference=selfie_reference,
        )


class PropertyVerificationService:
    """Validates that a landlord has uploaded a signed ownership/lease contract."""

    def verify_contract(self, contract_reference: str) -> PropertyContractVerification:
        # This demo assumes any provided reference is valid. In production we
        # would cross-check cadastre records and notarised documents.
        return PropertyContractVerification(
            verified=True,
            document_reference=contract_reference,
            verified_at=date.today(),
        )
