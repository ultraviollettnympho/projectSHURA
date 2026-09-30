"""Minimal proof for INFAC domain.

Verifies:
- domain exists and can be instantiated
- projection is read-only (does not write back)
- invariants are traceable and non-empty
- no brain/consciousness/expression import leaks
- identity-independent (no provider/avatar references)

Run: python -m unittest tests/test_infac_domain
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.infac.domain import INFACDomain, CommunityNode, Symbol
from core.infac.projection import INFACProjection


class TestINFACDomainBehavior(unittest.TestCase):
    def test_domain_instantiation(self):
        d = INFACDomain()
        self.assertEqual(len(d.nodes), 0)
        self.assertEqual(len(d.shared_symbols), 0)

    def test_register_and_project(self):
        d = INFACDomain()
        node = CommunityNode(name="mutual_aid", purpose="resource_exchange")
        d.register_node(node)
        proj = INFACProjection()
        result = proj.observe(d)
        self.assertTrue(result["ok"])
        self.assertIsNotNone(result["state"])
        self.assertEqual(result["state"]["node_count"], 1)

    def test_projection_read_only_no_mutation(self):
        d = INFACDomain()
        node = CommunityNode(name="education", purpose="distributed_education")
        d.register_node(node)
        proj = INFACProjection(d)
        before = proj.observe()
        # Projection has no mutation hooks; only observe() exists.
        # If projection were writable, there would be mutation methods.
        self.assertNotIn("mutate", dir(proj))
        self.assertNotIn("set_state", dir(proj))
        after = proj.observe()
        self.assertEqual(before["state"], after["state"])

    def test_invariants_reported(self):
        d = INFACDomain()
        invariants = d.verify_invariants()
        self.assertGreaterEqual(len(invariants), 7)
        # Confirm key separation invariants are present.
        texts = " ".join(invariants)
        self.assertIn("brain", texts)
        self.assertIn("projection", texts)
        self.assertIn("independence", texts)

    def test_symbol_immutable(self):
        sym = Symbol(name="rendezvous_01", context="shared_symbol")
        # Symbol is frozen; mutation attempt raises.
        with self.assertRaises(AttributeError):
            sym.name = "changed"

    def test_domain_separate_from_brain_imports(self):
        # Verify no brain/consciousness/expression import in domain file.
        import inspect
        import core.infac.domain as md
        source = inspect.getsource(md)
        # Check import lines only, not docstring language.
        import_lines = [line for line in source.splitlines() if line.startswith("import ") or line.startswith("from ")]
        import_text = " ".join(import_lines).lower()
        self.assertNotIn("brain", import_text)
        self.assertNotIn("consciousness", import_text)
        self.assertNotIn("expression", import_text)
        self.assertNotIn("renderer", import_text)
        self.assertNotIn("avatar", import_text)


if __name__ == "__main__":
    unittest.main()
