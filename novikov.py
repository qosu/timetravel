"""
Novikov Constraint Solver — finds self-consistent subsets of events
satisfying the Novikov self-consistency principle.

When a paradox is detected, the solver searches for maximal consistent
subsets of history where:
  1. All causal preconditions are satisfied (closure)
  2. No event negates another event in the set (consistency)
  3. The subset is maximal (keeps as many events as possible)

If no consistent subset exists, the timeline is genuinely broken —
this is a "reality fracture."
"""

from dataclasses import dataclass
from itertools import combinations

from universe import CausalEvent
from causality import CausalGraph, ParadoxType


@dataclass
class NovikovResolution:
    """A self-consistent resolution of a paradoxical timeline."""
    kept_events: list[str]          # events that survive
    removed_events: list[str]       # events removed to restore consistency
    description: str
    is_natural: bool                # True if this is the "natural" Novikov resolution


@dataclass
class RealityFracture:
    """No consistent subset exists — reality is broken."""
    description: str
    conflicting_events: list[str]
    fracture_depth: int             # minimum events that must be removed, but still inconsistent


class NovikovSolver:
    """
    Finds Novikov-consistent event subsets.

    The Novikov principle: only self-consistent histories can occur.
    If multiple consistent subsets exist, the one closest to the
    original timeline (fewest removals) is preferred.
    """

    def __init__(self, graph: CausalGraph, max_removals: int = 3):
        self.graph = graph
        self.events: dict[str, CausalEvent] = graph.events
        self.event_ids = list(graph.events.keys())
        self.max_removals = max_removals

    def resolve(self) -> NovikovResolution | RealityFracture:
        """
        Find the maximal consistent subset of events.

        Strategy: start with all events, then try removing increasing
        numbers of events until we find a consistent subset.
        """
        paradoxes = self.graph.detect_paradoxes()
        grandfather_paradoxes = [p for p in paradoxes if p.ptype == ParadoxType.GRANDFATHER]

        if not grandfather_paradoxes:
            return NovikovResolution(
                kept_events=self.event_ids,
                removed_events=[],
                description="Timeline is already self-consistent. No resolution needed.",
                is_natural=True,
            )

        all_paradox_events: set[str] = set()
        for p in grandfather_paradoxes:
            all_paradox_events.update(p.cycle)

        # Cap paradox events for combinatorial search (C(15,5) ≈ 3003, C(20,5) ≈ 15504)
        MAX_PARADOX_SEARCH = 15
        paradox_list = list(all_paradox_events)
        truncated = False
        if len(paradox_list) > MAX_PARADOX_SEARCH:
            paradox_list = paradox_list[:MAX_PARADOX_SEARCH]
            truncated = True

        search_limit = min(self.max_removals, len(paradox_list))
        for k in range(1, search_limit + 1):
            for removed in combinations(paradox_list, k):
                removed_set = set(removed)
                kept_set = set(self.event_ids) - removed_set

                if self._is_consistent(kept_set):
                    trunc_note = " (search truncated)" if truncated else ""
                    return NovikovResolution(
                        kept_events=[e for e in self.event_ids if e in kept_set],
                        removed_events=list(removed),
                        description=(
                            f"Novikov resolution: removed {len(removed)} event(s) "
                            f"({', '.join(removed)}) to restore consistency.{trunc_note}"
                        ),
                        is_natural=(k == self._minimal_removal()),
                    )

        # No consistent subset found — reality fracture
        if truncated:
            desc = (
                f"No consistent subset found within search limits "
                f"({MAX_PARADOX_SEARCH} events, {self.max_removals} removals). "
                f"Reality may be fractured OR search space insufficient."
            )
        else:
            desc = (
                "No consistent subset exists after exhaustive search. "
                "Reality is genuinely broken — this is a causal singularity."
            )
        return RealityFracture(
            description=desc,
            conflicting_events=list(all_paradox_events),
            fracture_depth=len(all_paradox_events),
        )

    def _is_consistent(self, event_set: set[str]) -> bool:
        """Check if a set of events satisfies all causal constraints."""
        for eid in event_set:
            event = self.events[eid]
            # All preconditions must be in the set
            for precond in event.preconditions:
                if precond not in event_set:
                    return False
            # No negated event can be in the set
            for negated in event.negations:
                if negated in event_set:
                    return False
        return True

    def _minimal_removal(self) -> int:
        """Find the true minimum number of events to remove for consistency."""
        grandfather_paradoxes = [
            p for p in self.graph.detect_paradoxes()
            if p.ptype == ParadoxType.GRANDFATHER
        ]
        all_paradox_events: set[str] = set()
        for p in grandfather_paradoxes:
            all_paradox_events.update(p.cycle)

        for k in range(1, len(all_paradox_events) + 1):
            for removed in combinations(all_paradox_events, k):
                removed_set = set(removed)
                kept_set = set(self.event_ids) - removed_set
                if self._is_consistent(kept_set):
                    return k
        return -1  # unreachable if RealityFracture

    def all_resolutions(self) -> list[NovikovResolution]:
        """Enumerate all consistent subsets (may be many for complex paradoxes)."""
        paradoxes = self.graph.detect_paradoxes()
        grandfather_paradoxes = [p for p in paradoxes if p.ptype == ParadoxType.GRANDFATHER]

        if not grandfather_paradoxes:
            return [NovikovResolution(
                kept_events=self.event_ids,
                removed_events=[],
                description="Already consistent.",
                is_natural=True,
            )]

        all_paradox_events: set[str] = set()
        for p in grandfather_paradoxes:
            all_paradox_events.update(p.cycle)

        resolutions = []
        for k in range(1, len(all_paradox_events) + 1):
            for removed in combinations(all_paradox_events, k):
                removed_set = set(removed)
                kept_set = set(self.event_ids) - removed_set
                if self._is_consistent(kept_set):
                    resolutions.append(NovikovResolution(
                        kept_events=[e for e in self.event_ids if e in kept_set],
                        removed_events=list(removed),
                        description=(
                            f"Resolution: remove {list(removed)}"
                        ),
                        is_natural=False,
                    ))
            if resolutions:
                resolutions[0].is_natural = True
                break
        return resolutions
