"""Simplified interface for consulting an external debt registry."""
from __future__ import annotations

from typing import Set


class DebtRegistryClient:
    """Mocked gateway that would connect to an external morosos registry."""

    def __init__(self, debtor_identifiers: Set[str] | None = None) -> None:
        self._debtors = debtor_identifiers or set()

    def is_clear(self, national_id: str) -> bool:
        """Return True when the identifier has no active debts."""

        return national_id not in self._debtors

    def add_debtor(self, national_id: str) -> None:
        self._debtors.add(national_id)

    def remove_debtor(self, national_id: str) -> None:
        self._debtors.discard(national_id)
