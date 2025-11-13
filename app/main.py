"""FastAPI application exposing the co-living matching capabilities."""
from __future__ import annotations

from datetime import date
from typing import Dict, List

from fastapi import FastAPI, HTTPException, status

from app.models import (
    ContractVerificationRequest,
    DebtStatus,
    FacialVerificationRequest,
    MatchResult,
    PropertyListing,
    UserProfile,
)
from app.services.debt_registry import DebtRegistryClient
from app.services.matching import MatchingEngine
from app.services.verification import (
    FacialVerificationService,
    PropertyVerificationService,
)

app = FastAPI(title="Coliving Match API", version="0.1.0")

# In-memory stores for the demo purposes.
USERS: Dict[str, UserProfile] = {}
PROPERTIES: Dict[str, PropertyListing] = {}

# Shared services.
DEBT_REGISTRY = DebtRegistryClient({"12345678A"})
MATCHING_ENGINE = MatchingEngine()
FACIAL_VERIFICATION = FacialVerificationService()
PROPERTY_VERIFICATION = PropertyVerificationService()


def get_user_or_404(user_id: str) -> UserProfile:
    try:
        return USERS[user_id]
    except KeyError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado") from exc


def get_property_or_404(property_id: str) -> PropertyListing:
    try:
        return PROPERTIES[property_id]
    except KeyError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Propiedad no encontrada") from exc


@app.post("/users", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def create_user(profile: UserProfile) -> UserProfile:
    debt_status = DebtStatus.CLEAR if DEBT_REGISTRY.is_clear(profile.id) else DebtStatus.HAS_DEBT

    if profile.identity_verification and not profile.identity_verification.verified:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Identidad no verificada")

    stored_profile = profile.model_copy(update={"debt_status": debt_status})
    USERS[profile.id] = stored_profile
    return stored_profile


@app.post("/users/{user_id}/verify", response_model=UserProfile)
async def verify_user(user_id: str, payload: FacialVerificationRequest) -> UserProfile:
    profile = get_user_or_404(user_id)
    verification = FACIAL_VERIFICATION.verify(payload.selfie_reference)
    updated_profile = profile.model_copy(update={"identity_verification": verification})
    USERS[user_id] = updated_profile
    return updated_profile


@app.post("/properties", response_model=PropertyListing, status_code=status.HTTP_201_CREATED)
async def create_property(listing: PropertyListing) -> PropertyListing:
    if listing.contract_verification and not listing.contract_verification.verified:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Contrato sin verificar")

    PROPERTIES[listing.id] = listing
    return listing


@app.post("/properties/{property_id}/verify", response_model=PropertyListing)
async def verify_property(
    property_id: str, payload: ContractVerificationRequest
) -> PropertyListing:
    listing = get_property_or_404(property_id)
    verification = PROPERTY_VERIFICATION.verify_contract(payload.contract_reference)
    updated_listing = listing.model_copy(update={"contract_verification": verification})
    PROPERTIES[property_id] = updated_listing
    return updated_listing


@app.get("/users/{user_id}/matches", response_model=List[MatchResult])
async def get_matches(user_id: str) -> List[MatchResult]:
    profile = get_user_or_404(user_id)
    matches = MATCHING_ENGINE.match(profile, list(PROPERTIES.values()))
    if not matches:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No hay coincidencias disponibles")
    return matches


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "date": date.today().isoformat()}
