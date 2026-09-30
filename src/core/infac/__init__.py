"""INFAC — community / cultural design domain.

Architectural position: separate domain, not a brain skill, not a renderer
feature, not an independent personality. Keeps philosophical/community-building
design distinct from any operational harm pathway.

Invariants (verified before any edit):
- Does NOT import brain, consciousness, expression, or renderer internals.
- Does NOT expose mutation hooks back into core cognition.
- Projection layer is read-only; domain state lives in this module.
- Identity-independent: no provider, avatar, or runtime coupling.
- Separate from the 7 mood IDs and from any skill registry identity.
"""
