"""arc.governance — graduated authority tiers.

Authority is tiered, not binary. Canonical history requires the strongest
protection; identity requires MODIFY/VETO via trusted decision; derived memory
is more permissive; experimental cognition is sandboxable.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, Optional, Set


class AuthorityTier(Enum):
    """Ascending authority levels (directive §11)."""
    OBSERVE = "observe"          # inspect state, events, memory provenance
    PROPOSE = "propose"          # suggest changes (identity/memory) as events
    INFLUENCE = "influence"      # shape retrieval, salience, response strategy
    MODIFY = "modify"            # alter derived state (memory accessibility, self-model)
    EXECUTE = "execute"          # perform actions in the world
    VETO = "veto"                # block/override identity or canonical changes


# Component -> allowed tiers. Canonical history and identity get the strictest
# protection. Experimental cognition is sandboxable (lower tier).
_DEFAULT_AUTHORITY: Dict[str, Set[AuthorityTier]] = {
    "canonical_history": {AuthorityTier.OBSERVE, AuthorityTier.EXECUTE},  # append-only via runtime
    "identity": {AuthorityTier.OBSERVE, AuthorityTier.PROPOSE, AuthorityTier.VETO, AuthorityTier.MODIFY},
    "derived_memory": {AuthorityTier.OBSERVE, AuthorityTier.INFLUENCE, AuthorityTier.MODIFY},
    "affective_state": {AuthorityTier.OBSERVE, AuthorityTier.INFLUENCE, AuthorityTier.MODIFY},
    "drives": {AuthorityTier.OBSERVE, AuthorityTier.INFLUENCE, AuthorityTier.MODIFY},
    "self_model": {AuthorityTier.OBSERVE, AuthorityTier.PROPOSE, AuthorityTier.MODIFY},
    "observer": {AuthorityTier.OBSERVE, AuthorityTier.PROPOSE},
    "consolidation": {AuthorityTier.OBSERVE, AuthorityTier.MODIFY},
    "experimental": {AuthorityTier.OBSERVE, AuthorityTier.PROPOSE, AuthorityTier.INFLUENCE},
}

# Actor -> max authority tier. The LLM/model may only PROPOSE; identity and
# canonical changes require VETO (trusted human/runtime) — not auto-rewritable.
_DEFAULT_ACTOR_TIERS: Dict[str, AuthorityTier] = {
    "system": AuthorityTier.VETO,
    "runtime": AuthorityTier.MODIFY,
    "observer": AuthorityTier.OBSERVE,
    "llm": AuthorityTier.PROPOSE,
    "model": AuthorityTier.PROPOSE,
    "user": AuthorityTier.VETO,
    "human": AuthorityTier.VETO,
}


class GovernanceController:
    """Enforces authority tiers and records authorization decisions."""

    def __init__(self, authority: Optional[Dict[str, Set[AuthorityTier]]] = None,
                 actor_tiers: Optional[Dict[str, AuthorityTier]] = None) -> None:
        self.authority: Dict[str, Set[AuthorityTier]] = dict(_DEFAULT_AUTHORITY)
        if authority:
            self.authority.update(authority)
        self.actor_tiers: Dict[str, AuthorityTier] = dict(_DEFAULT_ACTOR_TIERS)
        if actor_tiers:
            self.actor_tiers.update(actor_tiers)
        self.decisions: list = []

    def _actor_tier(self, actor: str) -> AuthorityTier:
        return self.actor_tiers.get(actor, AuthorityTier.OBSERVE)

    def authorized(self, component: str, required: AuthorityTier, actor: str = "system") -> bool:
        """True iff actor's tier meets `required` AND is permitted on component."""
        tier_order = {t: i for i, t in enumerate(AuthorityTier)}
        req_rank = tier_order.get(required, 0)
        actor_tier = self._actor_tier(actor)
        actor_rank = tier_order.get(actor_tier, 0)
        within_rank = actor_rank >= req_rank
        allowed = self.authority.get(component, set())
        within_component = actor_tier in allowed
        ok = within_rank and within_component
        self.decisions.append({
            "component": component, "required": required.value, "actor": actor,
            "actor_tier": actor_tier.value, "authorized": ok, "timestamp": _now(),
        })
        return ok

    def can_modify_canonical(self, actor: str) -> bool:
        """Canonical history is append-only and restricted to trusted writers."""
        return actor in _CANONICAL_WRITERS

    def can_modify_identity(self, actor: str) -> bool:
        """Identity changes require VETO-level (trusted decision), never the LLM."""
        return self.authorized("identity", AuthorityTier.VETO, actor=actor)

    def to_dict(self) -> dict:
        return {
            "authority": {k: [t.value for t in v] for k, v in self.authority.items()},
            "actor_tiers": {k: v.value for k, v in self.actor_tiers.items()},
            "canonical_writers": list(_CANONICAL_WRITERS),
            "decision_count": len(self.decisions),
        }


# Canonical history append is restricted: only the runtime / governance may
# append. The observer cannot.
_CANONICAL_WRITERS = {"runtime", "observer_runtime"}


def _now() -> float:
    import time
    return time.time()
