"""Core data models for the co-living matching demo."""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Lifestyle(str, Enum):
    """Simplified lifestyle categories used for affinity scoring."""

    EARLY_BIRD = "early_bird"
    NIGHT_OWL = "night_owl"
    FLEXIBLE = "flexible"


class UserPreferences(BaseModel):
    """Profile preferences that influence matchmaking."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    max_budget: int
    desired_locations: List[str] = Field(default_factory=list)
    lifestyle: Lifestyle = Lifestyle.FLEXIBLE
    allows_pets: bool = False
    hobbies: List[str] = Field(default_factory=list)

    @field_validator("max_budget")
    @classmethod
    def validate_budget(cls, value: int) -> int:
        if value < 0:
            raise ValueError("El presupuesto debe ser positivo")
        return value


class IdentityVerification(BaseModel):
    """Result of the biometric verification workflow."""

    verified: bool
    last_checked_at: Optional[date] = None
    provider_reference: Optional[str] = None


class DebtStatus(str, Enum):
    CLEAR = "clear"
    HAS_DEBT = "has_debt"


class UserProfile(BaseModel):
    """Aggregate user information consumed by the matching engine."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str
    email: str
    birthdate: date
    preferences: UserPreferences
    debt_status: DebtStatus = DebtStatus.CLEAR
    identity_verification: Optional[IdentityVerification] = None


class PropertyAmenities(BaseModel):
    wifi: bool = True
    has_workspace: bool = False
    allows_pets: bool = False
    bedrooms: int = 1
    bathrooms: float = 1.0

    @field_validator("bedrooms")
    @classmethod
    def validate_bedrooms(cls, value: int) -> int:
        if value < 1:
            raise ValueError("Debe haber al menos un dormitorio")
        return value

    @field_validator("bathrooms")
    @classmethod
    def validate_bathrooms(cls, value: float) -> float:
        if value < 0.5:
            raise ValueError("Debe haber al menos un baño compartido")
        return value


class PropertyContractVerification(BaseModel):
    verified: bool
    document_reference: Optional[str] = None
    verified_at: Optional[date] = None


class PropertyListing(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    city: str
    monthly_price: int
    available_from: date
    amenities: PropertyAmenities
    contract_verification: Optional[PropertyContractVerification] = None

    @field_validator("monthly_price")
    @classmethod
    def validate_price(cls, value: int) -> int:
        if value < 0:
            raise ValueError("El precio mensual debe ser positivo")
        return value


class MatchResult(BaseModel):
    user_id: str
    property_id: str
    score: float
    reasoning: List[str] = Field(default_factory=list)

    @field_validator("score")
    @classmethod
    def validate_score(cls, value: float) -> float:
        if not (0 <= value <= 1):
            raise ValueError("La puntuación debe estar entre 0 y 1")
        return value


class FacialVerificationRequest(BaseModel):
    """Payload used to trigger a biometric verification."""

    selfie_reference: str


class ContractVerificationRequest(BaseModel):
    """Payload used to trigger a property contract verification."""

    contract_reference: str
