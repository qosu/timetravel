"""
Singularity Engine — Self-Referential Universe with Internal Causal Mirror.

The engine that "touches infinity" not through quantum mechanics or
transfinite computation, but through self-reference.

A ReflectiveUniverse contains its own causal graph (the "mirror") as
a computable part of its state. When the mirror detects a paradox, the
universe resolves it — but the resolution changes the mirror, which may
reveal new paradoxes. This creates a feedback loop that, for certain
configurations, does not converge.

Non-convergence IS the singularity: the point where the universe cannot
settle into consistency because every resolution breeds new inconsistency.
This is Gödel's ghost in the machine of time travel.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from universe import Universe
from causality import CausalGraph, ParadoxType
from novikov import NovikovSolver, NovikovResolution, RealityFracture


class ReflectStatus(Enum):
    CONSISTENT = "consistent"        # no paradoxes, mirror stable
    EVOLVED = "evolved"              # resolution applied, state changed
    OSCILLATING = "oscillating"      # returned to a previously seen state
    SHATTERED = "shattered"          # no resolution possible
    DEPTH_EXCEEDED = "depth_exceeded" # iteration cap reached, unknown fate


@dataclass
class ReflectResult:
    """Outcome of one reflective iteration."""
    status: ReflectStatus
    iteration: int
    paradox_count: int
    resolution: Optional[NovikovResolution] = None
    state_hash: int = 0


@dataclass
class SingularityReport:
    """Complete analysis of a reflective universe's fate."""
    converged: bool
    total_iterations: int
    final_status: ReflectStatus
    visited_states: int
    oscillation_cycle: Optional[list[int]] = None
    description: str = ""


class ReflectiveUniverse:
    """
    A universe that observes itself.

    Properties:
    - Contains a Universe (entities, history, checkpoints)
    - mirror(): builds a CausalGraph from current state
    - reflect(): one iteration of detect → resolve → check
    - resolve_until(): iterate until convergence or divergence
    """

    def __init__(self, max_iterations: int = 100):
        self.u = Universe()
        self.iteration: int = 0
        self.max_iterations: int = max_iterations
        self.state_hashes: list[int] = []

    def mirror(self) -> CausalGraph:
        """Build the internal causal mirror — the universe's self-image."""
        return CausalGraph.from_history(
            self.u.history,
            ghost_event_ids=self.u.ghost_event_ids
        )

    def reflect(self) -> ReflectResult:
        """
        One iteration of the reflective loop.

        1. Build mirror
        2. Detect paradoxes
        3. If paradox: resolve via Novikov, apply resolution
        4. Return status
        """
        cg = self.mirror()
        paradoxes = cg.detect_paradoxes()
        grandfathers = [p for p in paradoxes if p.ptype == ParadoxType.GRANDFATHER]

        state_hash = self._structural_fingerprint()

        if not grandfathers:
            return ReflectResult(
                status=ReflectStatus.CONSISTENT,
                iteration=self.iteration,
                paradox_count=len(paradoxes),
                state_hash=state_hash,
            )

        solver = NovikovSolver(cg, max_removals=2)
        result = solver.resolve()

        if isinstance(result, RealityFracture):
            return ReflectResult(
                status=ReflectStatus.SHATTERED,
                iteration=self.iteration,
                paradox_count=len(paradoxes),
                state_hash=state_hash,
            )

        self._apply_resolution(result)
        self.iteration += 1

        return ReflectResult(
            status=ReflectStatus.EVOLVED,
            iteration=self.iteration,
            paradox_count=len(paradoxes),
            resolution=result,
            state_hash=state_hash,
        )

    def resolve_until(self) -> SingularityReport:
        """Iterate the reflective loop until convergence or non-convergence."""
        seen_hashes: dict[int, int] = {}  # hash → first iteration seen

        while self.iteration < self.max_iterations:
            result = self.reflect()
            h = result.state_hash

            if result.status == ReflectStatus.CONSISTENT:
                return SingularityReport(
                    converged=True,
                    total_iterations=self.iteration,
                    final_status=ReflectStatus.CONSISTENT,
                    visited_states=len(seen_hashes),
                    description=f"Universe converged to consistency after {self.iteration} reflection(s).",
                )

            if result.status == ReflectStatus.SHATTERED:
                return SingularityReport(
                    converged=False,
                    total_iterations=self.iteration,
                    final_status=ReflectStatus.SHATTERED,
                    visited_states=len(seen_hashes),
                    description="Universe shattered — no consistent subset exists.",
                )

            if h in seen_hashes:
                cycle_start = seen_hashes[h]
                cycle = list(range(cycle_start, self.iteration))
                return SingularityReport(
                    converged=False,
                    total_iterations=self.iteration,
                    final_status=ReflectStatus.OSCILLATING,
                    visited_states=len(seen_hashes),
                    oscillation_cycle=cycle,
                    description=(
                        f"OSCILLATION DETECTED: state {h} first seen at iteration "
                        f"{cycle_start}, returned at iteration {self.iteration}. "
                        f"Cycle length: {len(cycle)}. The universe cannot settle."
                    ),
                )

            seen_hashes[h] = self.iteration

        return SingularityReport(
            converged=False,
            total_iterations=self.iteration,
            final_status=ReflectStatus.DEPTH_EXCEEDED,
            visited_states=len(seen_hashes),
            description=(
                f"DEPTH EXCEEDED: {self.max_iterations} reflections without "
                f"convergence or detectable oscillation. "
                f"Visited {len(seen_hashes)} unique states. Fate unknown."
            ),
        )

    def _apply_resolution(self, resolution: NovikovResolution):
        """Apply a Novikov resolution by negating removed events."""
        for removed_id in resolution.removed_events:
            self.u.act(
                f"singularity_negate_{removed_id}",
                preconditions=(removed_id,),
                apply_fn=lambda e, rid=removed_id: e,
                negations=(removed_id,),
            )

    def _structural_fingerprint(self) -> int:
        """
        Hash the causal STRUCTURE, not event IDs.
        Two states with the same causal shape produce the same fingerprint,
        enabling oscillation detection even as event IDs change.
        """
        cg = self.mirror()
        cycles = cg.find_cycles()
        cycle_lengths = tuple(sorted(len(c) for c in cycles))
        entity_ids = tuple(sorted(self.u.entities.keys()))
        negation_count = sum(len(n) for n in cg.negates.values())
        ghost_count = len(self.u.ghost_event_ids)
        return hash((cycle_lengths, entity_ids, negation_count, ghost_count))
