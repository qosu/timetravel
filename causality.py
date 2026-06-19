"""
Causal Graph Engine — builds dependency graph from Universe history,
detects paradoxes, and classifies them by type.

Paradox types:
  GRANDFATHER:  event A depends on B but also negates B's precondition chain
  BOOTSTRAP:    causal loop with no external origin (information from nowhere)
  PREDESTINATION: closed causal loop where all events are mutually consistent
  GHOST_DEPENDENCY: active event depends on a ghost (overwritten) event
"""

from dataclasses import dataclass, field
from collections import deque
from enum import Enum

from universe import CausalEvent


class ParadoxType(Enum):
    GRANDFATHER = "grandfather"
    BOOTSTRAP = "bootstrap"
    PREDESTINATION = "predestination"
    GHOST_DEPENDENCY = "ghost_dependency"


@dataclass
class Paradox:
    """A detected causal inconsistency."""
    ptype: ParadoxType
    cycle: tuple[str, ...]            # event_ids forming the problematic cycle
    description: str
    severity: float                    # 0.0 (benign) → 1.0 (reality-breaking)


@dataclass
class CausalGraph:
    """
    Directed graph of causal dependencies extracted from universe history.

    Nodes are event_ids. Two edge types:
      - depends: A → B means B depends on A (A is a precondition of B)
      - negates: A ⊸ B means A invalidates B
    """
    events: dict[str, CausalEvent] = field(default_factory=dict)
    depends: dict[str, set[str]] = field(default_factory=dict)   # event_id → {precondition_ids}
    negates: dict[str, set[str]] = field(default_factory=dict)   # event_id → {negated_event_ids}
    ghost_events: set[str] = field(default_factory=set)          # events in overwritten timelines

    @classmethod
    def from_history(cls, history: list[CausalEvent],
                     ghost_event_ids: set[str] | None = None) -> 'CausalGraph':
        """Build causal graph from universe history."""
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
        """Is there a causal path from src to dst? (cause → effect direction)"""
        visited = set()
        queue = deque([src])
        while queue:
            node = queue.popleft()
            if node == dst:
                return True
            if node in visited:
                continue
            visited.add(node)
            # Forward causal edges: which events depend on 'node'?
            for event_id, preconds in self.depends.items():
                if node in preconds:
                    queue.append(event_id)
            # Negation edges: which events does 'node' negate?
            queue.extend(self.negates.get(node, set()))
        return False

    def find_cycles(self) -> list[tuple[str, ...]]:
        """Find all elementary cycles in the combined (causal ∪ negation) graph.

        Causal edges go FROM precondition TO dependent event (cause → effect).
        Negation edges go FROM negating event TO negated event.
        """
        all_edges: dict[str, set[str]] = {}

        # Causal edges: precondition → event (cause → effect)
        for event_id, preconds in self.depends.items():
            for precond in preconds:
                if precond not in all_edges:
                    all_edges[precond] = set()
                all_edges[precond].add(event_id)

        # Negation edges: negator → negated
        for event_id, negated in self.negates.items():
            if event_id not in all_edges:
                all_edges[event_id] = set()
            all_edges[event_id].update(negated)

        # Ensure all nodes have entries
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
        """Events with edges pointing TO event_id in the causal+negation graph."""
        incoming = set()
        # Causal: if event_id depends on Y, then Y → event_id
        incoming.update(self.depends.get(event_id, set()))
        # Negation: if Y negates event_id, then Y → event_id
        for nid, negs in self.negates.items():
            if event_id in negs:
                incoming.add(nid)
        return incoming

    # ── paradox detection ─────────────────────────────────────────

    def detect_paradoxes(self) -> list[Paradox]:
        """Find and classify all causal paradoxes in the graph."""
        paradoxes = []
        paradoxes.extend(self._detect_ghost_dependencies())
        paradoxes.extend(self._detect_cycle_paradoxes())
        return paradoxes

    def _detect_ghost_dependencies(self) -> list[Paradox]:
        """Active events that depend on ghost (overwritten) events."""
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
                    severity=0.3 + 0.1 * len(ghost_preconds)
                ))
        return results

    def _detect_cycle_paradoxes(self) -> list[Paradox]:
        """Classify all causal cycles into paradox types, keeping only maximal cycles."""
        cycles = self.find_cycles()
        if not cycles:
            return []

        # Deduplicate: keep maximal cycles (not proper subsets of another)
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
            ptype, desc, severity = self._classify_cycle(cycle)
            results.append(Paradox(
                ptype=ptype,
                cycle=cycle,
                description=desc,
                severity=severity,
            ))
        return results

    def _classify_cycle(self, cycle: tuple[str, ...]) -> tuple[ParadoxType, str, float]:
        """Classify a single causal cycle."""
        has_negation = self._cycle_has_negation(cycle)
        has_external_input = self._cycle_has_external_input(cycle)

        if has_negation:
            ptype = ParadoxType.GRANDFATHER
            desc = (
                f"Grandfather paradox: cycle {cycle} contains negation — "
                f"an event both requires and destroys part of the cycle's causal chain"
            )
            severity = 1.0
        elif not has_external_input:
            ptype = ParadoxType.BOOTSTRAP
            desc = (
                f"Bootstrap paradox: cycle {cycle} has no external cause — "
                f"information/state emerges from nothing"
            )
            severity = 0.5
        else:
            ptype = ParadoxType.PREDESTINATION
            desc = (
                f"Predestination loop: cycle {cycle} is causally closed but "
                f"internally consistent — Novikov-compatible"
            )
            severity = 0.0

        return ptype, desc, severity

    def _cycle_has_negation(self, cycle: tuple[str, ...]) -> bool:
        """Does any edge in the cycle represent a negation?"""
        for i, src in enumerate(cycle):
            dst = cycle[(i + 1) % len(cycle)]
            if dst in self.negates.get(src, set()):
                return True
        return False

    def _cycle_has_external_input(self, cycle: tuple[str, ...]) -> bool:
        """Does any node in the cycle have an incoming edge from outside?"""
        cycle_set = set(cycle)
        for node in cycle:
            all_incoming = self.incoming_edges(node)
            if all_incoming - cycle_set:
                return True
        return False
