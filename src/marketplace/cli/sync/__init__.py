"""Manifest-driven sync flow: read agents-marketplace.yaml and install per agent."""

from __future__ import annotations

from marketplace.cli.sync.flow import run_sync

__all__ = ["run_sync"]
