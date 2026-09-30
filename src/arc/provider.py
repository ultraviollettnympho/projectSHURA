"""arc.provider — model/provider abstraction for cognition.

The model provider must NOT define SHURA's identity (ADR-005). Cognition
operates through a ``CognitiveProvider`` ABC; the concrete provider is an
interchangeable executor. Two stub implementations exercise provider-swap
continuity without requiring live API keys.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class CognitiveProvider(ABC):
    """Exchangeable cognitive executor (Phase 5 ActionProposal contract)."""

    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def complete(self, messages: List[dict]) -> str:
        """Return a textual completion. Must be deterministic given identical input."""


class StubCognitiveProvider(CognitiveProvider):
    """Deterministic stub: returns a fixed completion. No network."""

    def __init__(self, reply: str = "stub:acknowledged") -> None:
        self._reply = reply

    def name(self) -> str:
        return "stub"

    def complete(self, messages: List[dict]) -> str:
        return self._reply


class EchoCognitiveProvider(CognitiveProvider):
    """Deterministic stub: echoes the last user message. No network."""

    def name(self) -> str:
        return "echo"

    def complete(self, messages: List[dict]) -> str:
        for msg in reversed(messages):
            if msg.get("role") == "user":
                return str(msg.get("content", ""))
        return ""
