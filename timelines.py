"""
Timeline Manager — multiple history branching for paradox resolution.

When Novikov self-consistency has multiple valid resolutions, each becomes
a separate timeline branch. The TimelineManager tracks all branches,
their relationships, and supports navigation between them.

Inspired by Hauser & Shoshany (1911.11590): multiple histories with
finite cyclic resolution under certain divisibility conditions.
"""

from dataclasses import dataclass, field
from copy import deepcopy

from universe import Universe, CausalEvent
from causality import CausalGraph
from novikov import NovikovSolver


@dataclass
class Timeline:
    """A single consistent history branch."""
    timeline_id: str
    events: list[str]                # event_ids in this timeline (in temporal order)
    parent_id: str | None            # timeline this branched from
    branch_reason: str               # why this branch was created
    universe_snapshot: dict           # entity state at branch point


@dataclass
class TimelineForest:
    """
    Manages multiple timeline branches emerging from paradox resolution.

    When Novikov finds multiple consistent subsets, each becomes a timeline.
    The 'active' timeline is the one the observer currently experiences.
    """

    timelines: dict[str, Timeline] = field(default_factory=dict)
    active_id: str = "prime"
    branch_counter: int = 0
    _original_history: list[CausalEvent] = field(default_factory=list)

    @classmethod
    def from_universe(cls, universe: Universe) -> 'TimelineForest':
        """Create a timeline forest from a universe with paradoxes."""
        forest = cls()
        forest._original_history = list(universe.history)

        graph = CausalGraph.from_history(
            universe.history,
            ghost_event_ids=universe.ghost_event_ids
        )
        solver = NovikovSolver(graph)

        resolutions = solver.all_resolutions()

        if not resolutions:
            # No paradox, or no resolution found → single timeline
            forest.timelines["prime"] = Timeline(
                timeline_id="prime",
                events=[e.event_id for e in universe.history],
                parent_id=None,
                branch_reason="Original timeline (no paradox)",
                universe_snapshot=deepcopy(universe.entities),
            )
            return forest

        if len(resolutions) == 1:
            # Single Novikov resolution → still one timeline
            r = resolutions[0]
            forest.timelines["prime"] = Timeline(
                timeline_id="prime",
                events=r.kept_events,
                parent_id=None,
                branch_reason=(
                    f"Novikov-consistent timeline: removed {r.removed_events}"
                ),
                universe_snapshot=deepcopy(universe.entities),
            )
            return forest

        # Multiple resolutions → branch!
        for i, resolution in enumerate(resolutions):
            tid = f"branch_{i}"
            forest.timelines[tid] = Timeline(
                timeline_id=tid,
                events=resolution.kept_events,
                parent_id="prime",
                branch_reason=(
                    f"Resolution {i}: keep {resolution.kept_events}"
                ),
                universe_snapshot=deepcopy(universe.entities),
            )
        forest.active_id = "branch_0"
        return forest

    @property
    def active(self) -> Timeline:
        return self.timelines[self.active_id]

    def switch_to(self, timeline_id: str):
        """Observer shifts to a different timeline branch."""
        if timeline_id not in self.timelines:
            available = list(self.timelines.keys())
            raise ValueError(f"No timeline '{timeline_id}'. Available: {available}")
        self.active_id = timeline_id

    @property
    def branch_count(self) -> int:
        return len(self.timelines)

    @property
    def is_fractured(self) -> bool:
        """Multiple timelines exist — reality has split."""
        return len(self.timelines) > 1

    def summary(self) -> str:
        """Human-readable timeline forest summary."""
        lines = [f"TimelineForest: {len(self.timelines)} timeline(s), active={self.active_id}"]
        for tid, tl in self.timelines.items():
            marker = "→" if tid == self.active_id else " "
            lines.append(
                f"  {marker} [{tid}] {len(tl.events)} events "
                f"(parent={tl.parent_id}) {tl.branch_reason[:80]}"
            )
        return "\n".join(lines)
