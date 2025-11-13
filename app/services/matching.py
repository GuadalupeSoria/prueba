"""Affinity scoring logic for the co-living marketplace."""
from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Iterable, List

from app.models import DebtStatus, Lifestyle, MatchResult, PropertyListing, UserProfile


class MatchingEngine:
    """Computes match scores between users and property listings."""

    def __init__(self, today: date | None = None) -> None:
        self._today = today or date.today()

    def match(self, user: UserProfile, properties: Iterable[PropertyListing]) -> List[MatchResult]:
        """Return the best property matches for the provided user."""

        results: List[MatchResult] = []
        for listing in properties:
            score, reasons = self._score_listing(user, listing)
            if score <= 0:
                continue
            results.append(
                MatchResult(
                    user_id=user.id,
                    property_id=listing.id,
                    score=round(min(score, 1.0), 3),
                    reasoning=reasons,
                )
            )

        return sorted(results, key=lambda r: r.score, reverse=True)

    # ------------------------------------------------------------------
    # Scoring helpers
    def _score_listing(self, user: UserProfile, listing: PropertyListing) -> tuple[float, List[str]]:
        if user.debt_status == DebtStatus.HAS_DEBT:
            return 0.0, ["El perfil aparece en el fichero de morosos"]

        score = 0.0
        reasons: List[str] = []

        price_factor = self._budget_score(user, listing)
        score += price_factor * 0.4
        if price_factor > 0:
            reasons.append(f"Precio compatible (factor {price_factor:.2f})")

        location_factor = self._location_score(user, listing)
        score += location_factor * 0.25
        if location_factor > 0:
            reasons.append(f"Ubicación deseada: {listing.city}")

        lifestyle_factor = self._lifestyle_score(user, listing)
        score += lifestyle_factor * 0.2
        if lifestyle_factor > 0:
            reasons.append("Estilo de vida compatible")

        hobby_factor = self._hobby_score(user, listing)
        score += hobby_factor * 0.1
        if hobby_factor > 0:
            reasons.append("Intereses compartidos con coinquilinos")

        amenities_factor = self._amenities_score(user, listing)
        score += amenities_factor * 0.05
        if amenities_factor > 0:
            reasons.append("Amenities acordes a las preferencias")

        if listing.contract_verification and listing.contract_verification.verified:
            score += 0.05
            reasons.append("Propiedad verificada por contrato")

        return score, reasons

    def _budget_score(self, user: UserProfile, listing: PropertyListing) -> float:
        budget = user.preferences.max_budget
        price = listing.monthly_price
        if price > budget:
            return max(0.0, 1 - (price - budget) / max(budget, 1))
        return 1.0

    def _location_score(self, user: UserProfile, listing: PropertyListing) -> float:
        if not user.preferences.desired_locations:
            return 0.5
        return 1.0 if listing.city in user.preferences.desired_locations else 0.0

    def _lifestyle_score(self, user: UserProfile, listing: PropertyListing) -> float:
        # Demo heuristic: workspace and quiet listings better for early birds,
        # city-centre nightlife suits night owls.
        lifestyle = user.preferences.lifestyle
        if lifestyle == Lifestyle.FLEXIBLE:
            return 0.5
        if lifestyle == Lifestyle.EARLY_BIRD:
            return 1.0 if listing.amenities.has_workspace else 0.3
        if lifestyle == Lifestyle.NIGHT_OWL:
            return 1.0 if "centro" in listing.description.lower() else 0.3
        return 0.0

    def _hobby_score(self, user: UserProfile, listing: PropertyListing) -> float:
        if not user.preferences.hobbies:
            return 0.2

        current_roommates = self._extract_roommate_hobbies(listing.description)
        shared = set(map(str.lower, user.preferences.hobbies)) & current_roommates
        return min(1.0, len(shared) / max(1, len(user.preferences.hobbies)))

    def _amenities_score(self, user: UserProfile, listing: PropertyListing) -> float:
        score = 0.0
        if user.preferences.allows_pets and listing.amenities.allows_pets:
            score += 0.6
        if listing.amenities.wifi:
            score += 0.2
        if listing.amenities.has_workspace:
            score += 0.2
        return min(score, 1.0)

    @staticmethod
    def _extract_roommate_hobbies(description: str) -> set[str]:
        words = [token.strip('.,') for token in description.lower().split()]
        counter = Counter(words)
        frequent = {word for word, count in counter.items() if count >= 2 and len(word) > 4}
        return frequent
