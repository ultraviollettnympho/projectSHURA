"""arc.identity — immutable identity core + governance gate.

Identity (what SHURA is) is immutable at runtime. The LLM never rewrites it
directly: proposed changes are routed through ``IdentityGovernance`` which
emits a canonical ``identity.change.proposed`` event and only accepts a change
through an externally-gated decision (not implemented for auto-apply in this
phase — identity remains immutable until a governed decision is recorded).

The mutable mirror of "what SHURA believes about itself" lives in
``arcself_model.SelfModel`` — deliberately separate from identity.
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

# Minimal identity used when no soul.md is present (keeps tests hermetic).
_FALLBACK_IDENTITY = """\
SHURA is a portable creative intelligence.
She persists across models. Her identity is not authored by any single LLM output.
"""

DEFAULT_SOUL_PATH = "data/prompts/soul.md"


@dataclass(frozen=True)
class Identity:
    """Immutable identity payload.

    Why frozen=True: identity must not be casually mutated by cognition.
    The hash is the canonical fingerprint used by the coherence monitor to
    detect identity drift (a change to identity text must produce a new
    ``identity.change.applied`` event with provenance — not a silent rewrite).
    """
    text: str
    hash: str
    manifest_path: str
    loaded_at: float

    @classmethod
    def load(cls, soul_path: str = DEFAULT_SOUL_PATH) -> "Identity":
        p = Path(soul_path)
        if p.exists():
            txt = p.read_text(encoding="utf-8")
        else:
            txt = _FALLBACK_IDENTITY
        h = hashlib.sha256(txt.encode("utf-8")).hexdigest()
        return cls(text=txt, hash=h, manifest_path=str(p), loaded_at=time.time())

    @classmethod
    def from_text(cls, text: str, manifest_path: str = "immutable") -> "Identity":
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return cls(text=text, hash=h, manifest_path=manifest_path, loaded_at=time.time())

    def fingerprint(self) -> dict:
        return {
            "hash": self.hash,
            "manifest_path": self.manifest_path,
            "length_chars": len(self.text),
            "loaded_at": self.loaded_at,
        }


@dataclass
class ChangeProposal:
    """A proposed identity change awaiting governance.

    Why every field: proposal_id (traceability), field_path (what would change),
    old_value/new_value (diff for audit), rationale (why), proposer (who),
    approved (gated decision), decision_event_id (link to canonical decision).
    """
    proposal_id: str
    field_path: str
    old_value: str
    new_value: str
    rationale: str
    proposer: str
    approved: bool = False
    decision_event_id: Optional[str] = None


class IdentityGovernance:
    """Governs identity mutation.

    In this phase identity is NOT auto-applied. ``propose_change`` records a
    proposal and returns it; acceptance requires an externally-gated decision
    which emits ``identity.change.applied`` and constructs a new Identity.
    The proposal itself is what gets persisted as a canonical event, so the
    *fact of proposing* is durable even while no change is applied.
    """

    def __init__(self, identity: Identity) -> None:
        self.identity = identity
        self.proposals: list[ChangeProposal] = []
        self.applied: list[ChangeProposal] = []

    def propose_change(
        self,
        field_path: str,
        old_value: str,
        new_value: str,
        rationale: str,
        proposer: str,
    ) -> ChangeProposal:
        import uuid
        prop = ChangeProposal(
            proposal_id=str(uuid.uuid4()),
            field_path=field_path,
            old_value=old_value,
            new_value=new_value,
            rationale=rationale,
            proposer=proposer,
            approved=False,
        )
        self.proposals.append(prop)
        return prop

    def accept(self, proposal: ChangeProposal, decision_event_id: str) -> Identity:
        """Gated acceptance — only callable by an authorized governance decision.

        Produces a new Identity with updated text where the field_path matches.
        In this phase this is exercised by tests with an explicit decision event;
        the LLM path never calls it directly.
        """
        if proposal.field_path == "text":
            new_text = proposal.new_value
        else:
            # Non-text fields are immutable for now.
            raise NotImplementedError(f"acceptance of {proposal.field_path} not implemented")
        proposal.approved = True
        proposal.decision_event_id = decision_event_id
        self.applied.append(proposal)
        return Identity.from_text(new_text, self.identity.manifest_path)
