"""
Digital Universe — deterministic state machine with explicit causal tracking.
Foundation of the Time Travel Engine.

Invariants:
- Every state mutation is a CausalEvent with declared preconditions
- The causal graph is maintained automatically — no manual annotation
- Checkpoints enable time travel: state reversion + causal loop detection
- Time is discrete, monotonically non-decreasing within a timeline
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional
from enum import Enum
import copy
import itertools


class EntityStatus(Enum):
    ALIVE = "alive"
    DEAD = "dead"


@dataclass(frozen=True)
class CausalEvent:
    """An irreducible state transition with explicit causal dependencies."""
    event_id: str
    tick: int                           # discrete time when this occurred
    preconditions: tuple[str, ...]      # event_ids that MUST have occurred for this to be possible
    negations: tuple[str, ...]          # event_ids that this event undoes/invalidates
    description: str
    # entity changes: (entity_id, new_properties | None=destroyed)
    mutations: tuple[tuple[str, Optional[dict[str, Any]]], ...]

    @property
    def invalidates(self) -> tuple[str, ...]:
        return self.negations


class Universe:
    """
    Deterministic state machine where every action carries explicit causal preconditions.

    Usage:
        u = Universe()
        u.spawn('grandfather', {'status': 'alive'})
        u.checkpoint('origin')
        u.act('beget_parent', preconds=(...), apply_fn=lambda e: ...)
        u.travel_to('origin')       # time travel!
        u.act('kill_grandfather', preconds=(...), apply_fn=...)
        # -> ParadoxError if causal cycle detected
    """

    def __init__(self, seed_events: Optional[list[CausalEvent]] = None):
        self.tick: int = 0
        self.entities: dict[str, dict[str, Any]] = {}
        self.history: list[CausalEvent] = []        # complete linear history
        self.active_from: int = 0                    # index in history where current timeline starts
        self.ghost_event_ids: set[str] = set()       # events from overwritten timelines
        self._event_counter = itertools.count()
        self.checkpoints: dict[str, int] = {}        # name -> history index

        if seed_events:
            for evt in seed_events:
                self._apply_mutations(evt.mutations)
                self.history.append(evt)
                self.tick = evt.tick + 1
            self.active_from = len(self.history)

    # ── core operations ────────────────────────────────────────────

    def spawn(self, entity_id: str, properties: dict[str, Any],
              preconditions: tuple[str, ...] = ()) -> str:
        """Create a new entity — a causal event in spacetime."""
        if entity_id in self.entities:
            raise ValueError(f"Entity '{entity_id}' already exists at tick {self.tick}")
        return self._record(
            f"spawn_{entity_id}",
            preconditions=preconditions,
            negations=(),
            description=f"Spawn entity '{entity_id}'",
            mutations=((entity_id, dict(properties)),)
        )

    def act(self, name: str, preconditions: tuple[str, ...],
            apply_fn: Callable[[dict[str, dict]], dict[str, dict]],
            negations: tuple[str, ...] = ()) -> str:
        """
        Apply a state transformation with declared causal preconditions.

        Args:
            name: human-readable action label
            preconditions: event_ids this action causally depends on
            apply_fn: pure function (entities -> new_entities); must not mutate input
            negations: event_ids that this action invalidates (e.g. killing grandfather
                       invalidates all events that depended on him being alive)

        Returns the new event_id.
        """
        snapshot_before = copy.deepcopy(self.entities)
        new_entities = apply_fn(copy.deepcopy(self.entities))

        mutations = self._diff(snapshot_before, new_entities)

        return self._record(
            name,
            preconditions=preconditions,
            negations=negations,
            description=name,
            mutations=mutations
        )

    def kill(self, entity_id: str, preconditions: tuple[str, ...],
             negations: tuple[str, ...] = ()) -> str:
        """Destroy an entity — shorthand for act with deletion."""
        if entity_id not in self.entities:
            raise ValueError(f"Cannot kill nonexistent entity '{entity_id}' at tick {self.tick}")

        def _remove(entities):
            entities.pop(entity_id, None)
            return entities

        return self.act(
            f"kill_{entity_id}",
            preconditions=preconditions,
            apply_fn=_remove,
            negations=negations
        )

    # ── time travel ────────────────────────────────────────────────

    def checkpoint(self, name: str):
        """Mark this moment. You can return here later."""
        self.checkpoints[name] = len(self.history)

    def travel_to(self, checkpoint_name: str):
        """
        Rewind state to a checkpoint.

        History AFTER the checkpoint is NOT deleted — it becomes a 'future shadow'
        that new actions can reference (and potentially invalidate).

        This is the operational essence of time travel in this engine.
        """
        if checkpoint_name not in self.checkpoints:
            available = list(self.checkpoints.keys())
            raise ValueError(
                f"No checkpoint '{checkpoint_name}'. Available: {available}"
            )

        idx = self.checkpoints[checkpoint_name]
        if idx > len(self.history):
            raise ValueError(
                f"Checkpoint '{checkpoint_name}' at index {idx} is beyond "
                f"history length {len(self.history)} — temporal corruption"
            )

        # Rebuild entity state from history[0:idx]
        self.entities = {}
        for event in self.history[:idx]:
            self._apply_mutations(event.mutations)

        # Mark overwritten events as ghosts
        for event in self.history[idx:]:
            self.ghost_event_ids.add(event.event_id)

        self.active_from = idx
        self.tick = self.history[idx - 1].tick + 1 if idx > 0 else 0

    # ── internal ───────────────────────────────────────────────────

    def _record(self, name: str, preconditions: tuple[str, ...],
                negations: tuple[str, ...], description: str,
                mutations: tuple[tuple[str, Optional[dict[str, Any]]], ...]) -> str:
        event_id = f"{name}@{self.tick}#{next(self._event_counter)}"
        event = CausalEvent(
            event_id=event_id,
            tick=self.tick,
            preconditions=preconditions,
            negations=negations,
            description=description,
            mutations=mutations,
        )
        self._apply_mutations(mutations)
        self.history.append(event)
        self.tick += 1
        return event_id

    @staticmethod
    def _diff(before: dict[str, dict], after: dict[str, dict]) -> tuple:
        """Compute minimal mutation set from before -> after."""
        mutations = []
        for eid, props in after.items():
            if eid not in before or before[eid] != props:
                mutations.append((eid, dict(props)))
        for eid in before:
            if eid not in after:
                mutations.append((eid, None))  # destroyed
        return tuple(mutations)

    def _apply_mutations(self, mutations: tuple[tuple[str, Optional[dict]], ...]):
        """Apply mutations to self.entities."""
        for eid, props in mutations:
            if props is None:
                self.entities.pop(eid, None)
            else:
                self.entities[eid] = dict(props)
