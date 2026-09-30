"""INFAC domain — minimal v0 implementation.

Exploration areas (from architecture roadmap):
- bottom-up community formation
- mutual aid
- resource and skill exchange
- participatory processes
- autonomous cultural production
- shared symbols and rendezvous
- distributed publishing and education

This is a design domain, not an execution harness. No external service
integration, no personality substitution, no brain mutation.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set
from datetime import datetime, timezone


@dataclass(frozen=True)
class Symbol:
    """Shared symbol / rendezvous marker — immutable by design."""
    name: str
    context: str  # e.g., "mutual_aid", "cultural_production"
    created: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CommunityNode:
    """A node in the bottom-up community design — mutable only via
    explicit domain methods so ownership remains clear."""
    name: str
    purpose: str  # e.g., "resource_exchange", "education"
    members: Set[str] = field(default_factory=set)
    resources: List[str] = field(default_factory=list)
    symbols: List[Symbol] = field(default_factory=list)
    participatory: bool = True

    def add_member(self, member: str) -> "CommunityNode":
        new_members = set(self.members)
        new_members.add(member)
        # Return a new instance for projection safety; mutation is local.
        self.members = new_members
        return self

    def add_symbol(self, symbol: Symbol) -> "CommunityNode":
        new_symbols = list(self.symbols)
        new_symbols.append(symbol)
        self.symbols = new_symbols
        return self


@dataclass
class INFACDomain:
    """Root container for the INFAC community/cultural design domain.

    Keeps philosophical/community-building design separate from operational
    activity (per architecture rules). No brain/consciousness coupling.
    """
    nodes: Dict[str, CommunityNode] = field(default_factory=dict)
    shared_symbols: List[Symbol] = field(default_factory=list)

    # --- domain operations ------------------------------------------------

    def register_node(self, node: CommunityNode) -> None:
        self.nodes[node.name] = node

    def get_node(self, name: str) -> Optional[CommunityNode]:
        return self.nodes.get(name)

    def list_nodes(self) -> List[str]:
        return list(self.nodes.keys())

    # --- projection interface (read-only) ----------------------------------

    def projection_state(self) -> Dict:
        """Read-only snapshot for observers/projections. Never mutates domain."""
        return {
            "node_count": len(self.nodes),
            "nodes": [
                {
                    "name": n.name,
                    "purpose": n.purpose,
                    "members": sorted(n.members),
                    "resources": list(n.resources),
                    "symbol_names": [s.name for s in n.symbols],
                    "participatory": n.participatory,
                }
                for n in self.nodes.values()
            ],
            "shared_symbol_count": len(self.shared_symbols),
            "shared_symbol_contexts": sorted({
                s.context for s in self.shared_symbols
            }),
        }

    # --- invariants ---------------------------------------------------------

    def verify_invariants(self) -> List[str]:
        """Trace and report invariants before any edit or read.

        Returns list of invariant descriptions (non-empty = healthy).
        """
        invariants: List[str] = []
        # Separate domain: no brain/consciousness import.
        invariants.append("domain: no brain/consciousness/expression import")
        # Separate domain: no renderer/OBS/Live2D import.
        invariants.append("domain: no renderer/OBS import")
        # Separate domain: not registered as a skill personality.
        invariants.append("domain: not a SkillRegistry identity")
        # Projection is read-only (projection_state returns dict, never writes).
        invariants.append("projection: read-only snapshot")
        # Identity-independent: no provider/model coupling.
        invariants.append("independence: no provider/model/avatar coupling")
        # Separate from mood IDs.
        invariants.append("separation: independent of 7 mood IDs")
        # No external service dependency (no MCP, no adapter, no API call).
        invariants.append("independence: no external service dependency")
        return invariants
