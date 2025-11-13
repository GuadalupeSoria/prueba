from datetime import date

from app.models import (
    DebtStatus,
    MatchResult,
    PropertyAmenities,
    PropertyListing,
    PropertyContractVerification,
    UserPreferences,
    UserProfile,
    Lifestyle,
)
from app.services.matching import MatchingEngine


def build_user(**kwargs) -> UserProfile:
    defaults = dict(
        id="99999999Z",
        full_name="Test User",
        email="test@example.com",
        birthdate=date(1990, 1, 1),
        preferences=UserPreferences(
            max_budget=600,
            desired_locations=["Madrid"],
            lifestyle=Lifestyle.EARLY_BIRD,
            allows_pets=True,
            hobbies=["cine", "senderismo"],
        ),
        debt_status=DebtStatus.CLEAR,
    )
    defaults.update(kwargs)
    return UserProfile(**defaults)


def build_listing(**kwargs) -> PropertyListing:
    defaults = dict(
        id="prop-1",
        title="Habitación luminosa",
        description="Piso en el centro con compis amantes de cine y senderismo senderismo.",
        city="Madrid",
        monthly_price=550,
        available_from=date.today(),
        amenities=PropertyAmenities(
            wifi=True,
            has_workspace=True,
            allows_pets=True,
            bedrooms=3,
            bathrooms=1.5,
        ),
        contract_verification=PropertyContractVerification(
            verified=True,
            document_reference="contract-123",
            verified_at=date.today(),
        ),
    )
    defaults.update(kwargs)
    return PropertyListing(**defaults)


def test_matching_engine_returns_reasonable_score():
    engine = MatchingEngine(today=date(2024, 1, 1))
    user = build_user()
    listing = build_listing()

    results = engine.match(user, [listing])

    assert results
    match = results[0]
    assert isinstance(match, MatchResult)
    assert match.score > 0.8
    assert any("Propiedad verificada" in reason for reason in match.reasoning)


def test_matching_engine_rejects_users_with_debt():
    engine = MatchingEngine(today=date(2024, 1, 1))
    user = build_user(debt_status=DebtStatus.HAS_DEBT)
    listing = build_listing()

    results = engine.match(user, [listing])

    assert results == []
