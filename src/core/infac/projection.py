"""INFAC projection layer — read-only observer of the domain.

Projection code must not import brain/consciousness/expression for mutation.
Observes domain state through projection_state() only.
"""
from typing import Dict, List, Optional
from src.core.infac.domain import INFACDomain, CommunityNode, Symbol


class INFACProjection:
    """Read-only projection of INFAC community/cultural design state.

    Does NOT hold domain state; references an external INFACDomain instance
    only for snapshot reads.
    """

    def __init__(self, domain: Optional[INFACDomain] = None):
        self._domain_ref: Optional[INFACDomain] = domain

    def observe(self, domain: Optional[INFACDomain] = None) -> Dict:
        """Produce a read-only snapshot from the observed domain.

        If an external domain is passed, use it; otherwise fall back to
        the reference held at initialization (if any). This keeps mutation
        authority clearly outside the projection.
        """
        target = domain if domain is not None else self._domain_ref
        if target is None:
            return {"ok": False, "error": "no domain observed", "state": None}
        return {"ok": True, "error": None, "state": target.projection_state()}

    def symbol_list(self, domain: Optional[INFACDomain] = None) -> List[str]:
        target = domain if domain is not None else self._domain_ref
        if target is None:
            return []
        return sorted({s.name for s in target.shared_symbols})
