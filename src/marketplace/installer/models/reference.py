from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceSpec:
    """How to point an agent's top-level instructions file at an installed rules dir."""

    candidates: list[str]
    fallback: str
    fallback_header: str = ""
