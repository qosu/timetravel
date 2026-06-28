"""
Causal Graph Engine — builds dependency graph from Universe history,
detects paradoxes, and classifies them by type.

Paradox types:
  GRANDFATHER:  cycle in G* containing ≥1 negation edge. Three subtypes:
    PURE_FPN      — ∃ node e: dep-path v→*e exists AND e negates v
    MUTUAL_NEG    — all cycle edges are negation; no dep relationship
    MIXED_NONFPN  — dep+neg edges present but no node satisfies FPN condition
  BOOTSTRAP:    causal loop with no external origin (information from nowhere)
  PREDESTINATION: closed causal loop where all events are mutually consistent
  GHOST_DEPENDENCY: active event depends on a ghost (overwritten) event

Correction note (2026-06-21):
  Original has_path() traversed G* (dep ∪ neg edges), making FPN detection
  trivially equivalent to grandfather detection by cycle topology. This is
  circular. has_dep_path() now separates pure causal reachability from G*
  reachability. The FPN condition requires a PURE DEP path, not a G* path.
"""

from dataclasses import dataclass, field
from collections import deque
from enum import Enum
from typing import Optional

from universe import CausalEvent


class ParadoxType(Enum):
    GRANDFATHER = "grandfather"
    BOOTSTRAP = "bootstrap"
    PREDESTINATION = "predestination"
    GHOST_DEPENDENCY = "ghost_dependency"


class GrandfatherSubtype(Enum):
    """
    Subtypes of GRANDFATHER paradox, distinguished by dep-graph structure.

    The distinction matters for resolvability theory:
      PURE_FPN    — hardest: negator causally depends on what it destroys
      MUTUAL_NEG  — softer: mutual invalidation, no causal chain
      MIXED       — intermediate: some dep edges but FPN condition not met
    """
    PURE_FPN   = "pure_fpn"
    MUTUAL_NEG = "mutual_negation"
    MIXED      = "mixed_nonfpn"


@dataclass
class Paradox:
    """A detected causal inconsistency."""
    ptype: ParadoxType
    cycle: tuple[str, ...]
    description: str
    severity: float
    fpn_subtype: Optional[GrandfatherSubtype] = None  # set iff ptype == GRANDFATHER


@dataclass
class CausalGraph:
    """
    Directed graph of causal dependencies extracted from universe history.

    Nodes are event_ids. Two edge types:
      - depends: A → B means B depends on A (A is a precondition of B)
      - negates: A ⊸ B means A invalidates B

    Combined graph G* = (V, E_dep ∪ E_neg) is used for cycle detection.
    FPN condition requires a PURE DEP path, not a G* path.
    """
    events: dict[str, CausalEvent] = field(default_factory=dict)
    depends: dict[str, set[str]] = field(default_factory=dict)   # event_id → {precondition_ids}
    negates: dict[str, set[str]] = field(default_factory=dict)   # event_id → {negated_event_ids}
    ghost_events: set[str] = field(default_factory=set)

    @classmethod
    def from_history(cls, history: list[CausalEvent],
                     ghost_event_ids: set[str] | None = None) -> 'CausalGraph':
        graph = cls()
        for event in history:
            graph.events[event.event_id] = event
            graph.depends[event.event_id] = set(event.preconditions)
            graph.negates[event.event_id] = set(event.negations)
        if ghost_event_ids:
            graph.ghost_events = ghost_event_ids
        return graph

    # ── graph queries ────────────────────────────────────────────

    def has_path(self, src: str, dst: str) -> bool:
        """
        Reachability in G* (dep ∪ neg edges).

        NOTE: This traverses BOTH edge types. For FPN detection use
        has_dep_path(), which traverses dep edges only. Confusing these
        two makes FPN trivially equivalent to cycle membership.
        """
        visited = set()
        queue = deque([src])
        while queue:
            node = queue.popleft()
            if node == dst:
                return True
            if node in visited:
                continue
            visited.add(node)
            for event_id, preconds in self.depends.items():
                if node in preconds:
                    queue.append(event_id)
            queue.extend(self.negates.get(node, set()))
        return False

    def has_dep_path(self, src: str, dst: str) -> bool:
        """
        Reachability via PURE DEPENDENCY edges only (no negation).

        src →_dep* dst means: dst is causally downstream of src.
        Equivalently: dst depends (directly or transitively) on src.
        Use this for FPN condition (i): e causally depends on v.
        """
        visited = set()
        queue = deque([src])
        while queue:
            node = queue.popleft()
            if node == dst:
                return True
            if node in visited:
                continue
            visited.add(node)
            for event_id, preconds in self.depends.items():
                if node in preconds:
                    queue.append(event_id)
        return False

    def fpn_nodes_in_cycle(self, cycle: tuple[str, ...]) -> list[tuple[str, str]]:
        """
        Find (negator, negated) pairs in this cycle where negator has a
        PURE DEP path from negated. These are proper FPN instances.

        FPN(negator, negated) holds iff:
          (i)  negated →_dep* negator  (dep path, not G* path)
          (ii) negator negates negated (negation edge exists)
        """
        result = []
        for i, src in enumerate(cycle):
            dst = cycle[(i + 1) % len(cycle)]
            if dst in self.negates.get(src, set()):
                if self.has_dep_path(dst, src):
                    result.append((src, dst))
        return result

    def find_cycles(self) -> list[tuple[str, ...]]:
        """Find all elementary cycles in the combined (dep ∪ neg) graph G*."""
        all_edges: dict[str, set[str]] = {}

        for event_id, preconds in self.depends.items():
            for precond in preconds:
                if precond not in all_edges:
                    all_edges[precond] = set()
                all_edges[precond].add(event_id)

        for event_id, negated in self.negates.items():
            if event_id not in all_edges:
                all_edges[event_id] = set()
            all_edges[event_id].update(negated)

        for nid in set(self.depends) | set(self.negates):
            if nid not in all_edges:
                all_edges[nid] = set()

        cycles = []
        visited: set[str] = set()
        stack: list[str] = []
        on_stack: set[str] = set()

        def dfs(node: str):
            if node in on_stack:
                cycle_start = stack.index(node)
                cycle = tuple(stack[cycle_start:])
                cycles.append(cycle)
                return
            if node in visited:
                return
            visited.add(node)
            on_stack.add(node)
            stack.append(node)
            for neighbor in all_edges.get(node, set()):
                dfs(neighbor)
            stack.pop()
            on_stack.discard(node)

        for node in all_edges:
            if node not in visited:
                dfs(node)

        return cycles

    def incoming_edges(self, event_id: str) -> set[str]:
        """Events with edges pointing TO event_id in G*."""
        incoming = set()
        incoming.update(self.depends.get(event_id, set()))
        for nid, negs in self.negates.items():
            if event_id in negs:
                incoming.add(nid)
        return incoming

    # ── paradox detection ─────────────────────────────────────────

    def detect_paradoxes(self) -> list[Paradox]:
        paradoxes = []
        paradoxes.extend(self._detect_ghost_dependencies())
        paradoxes.extend(self._detect_cycle_paradoxes())
        return paradoxes

    def _detect_ghost_dependencies(self) -> list[Paradox]:
        results = []
        for eid, event in self.events.items():
            if eid in self.ghost_events:
                continue
            ghost_preconds = [p for p in event.preconditions if p in self.ghost_events]
            if ghost_preconds:
                results.append(Paradox(
                    ptype=ParadoxType.GHOST_DEPENDENCY,
                    cycle=(eid, *ghost_preconds),
                    description=(
                        f"Active event '{eid}' depends on ghost event(s) "
                        f"{ghost_preconds} from an overwritten timeline"
                    ),
                    severity=0.3 + 0.1 * len(ghost_preconds),
                ))
        return results

    def _detect_cycle_paradoxes(self) -> list[Paradox]:
        cycles = self.find_cycles()
        if not cycles:
            return []

        cycle_sets = [frozenset(c) for c in cycles]
        maximal = []
        for i, c in enumerate(cycles):
            is_subset = any(
                cycle_sets[i].issubset(cycle_sets[j]) and len(cycle_sets[i]) < len(cycle_sets[j])
                for j in range(len(cycles))
            )
            if not is_subset:
                maximal.append(c)

        results = []
        for cycle in maximal:
            ptype, subtype, desc, severity = self._classify_cycle(cycle)
            results.append(Paradox(
                ptype=ptype,
                fpn_subtype=subtype,
                cycle=cycle,
                description=desc,
                severity=severity,
            ))
        return results

    def _classify_cycle(
        self, cycle: tuple[str, ...]
    ) -> tuple[ParadoxType, Optional[GrandfatherSubtype], str, float]:
        """Classify a single cycle, returning (ptype, subtype, desc, severity)."""
        has_negation = self._cycle_has_negation(cycle)
        has_external_input = self._cycle_has_external_input(cycle)

        if has_negation:
            fpn_nodes = self.fpn_nodes_in_cycle(cycle)
            all_neg_edges = all(
                cycle[(i + 1) % len(cycle)] in self.negates.get(cycle[i], set())
                for i in range(len(cycle))
            )

            if fpn_nodes:
                subtype = GrandfatherSubtype.PURE_FPN
                negator, negated = fpn_nodes[0]
                desc = (
                    f"Grandfather/PURE_FPN: {negator} has dep-path from {negated} "
                    f"and negates {negated}. Self-undermining causal structure."
                )
            elif all_neg_edges:
                subtype = GrandfatherSubtype.MUTUAL_NEG
                desc = (
                    f"Grandfather/MUTUAL_NEG: cycle {cycle} consists entirely of "
                    f"negation edges — mutual invalidation, no causal dependency."
                )
            else:
                subtype = GrandfatherSubtype.MIXED
                desc = (
                    f"Grandfather/MIXED_NONFPN: cycle {cycle} has dep+neg edges "
                    f"but no node satisfies the pure-dep FPN condition."
                )
            return ParadoxType.GRANDFATHER, subtype, desc, 1.0

        elif not has_external_input:
            return ParadoxType.BOOTSTRAP, None, (
                f"Bootstrap paradox: cycle {cycle} has no external cause"
            ), 0.5
        else:
            return ParadoxType.PREDESTINATION, None, (
                f"Predestination loop: cycle {cycle} is causally closed but consistent"
            ), 0.0

    def _cycle_has_negation(self, cycle: tuple[str, ...]) -> bool:
        for i, src in enumerate(cycle):
            dst = cycle[(i + 1) % len(cycle)]
            if dst in self.negates.get(src, set()):
                return True
        return False

    def _cycle_has_external_input(self, cycle: tuple[str, ...]) -> bool:
        cycle_set = set(cycle)
        for node in cycle:
            all_incoming = self.incoming_edges(node)
            if all_incoming - cycle_set:
                return True
        return False
