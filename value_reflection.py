"""
AI Value Reflection — Formal Bridge between FPN Theory and AI Alignment
========================================================================

Maps AI value modification systems onto the ReflectiveSystem formalism
from formal_reflection.py. This bridge proves that:

  AI VALUE DRIFT = FIXED-POINT NEGATION

When an AI modifies its values based on self-evaluation, the resulting
causal structure IS FPN. The modification depends on the values it negates.

THEOREM (Value Drift Non-Convergence):
  Any AI system A that:
  (i)   makes decisions based on values V
  (ii)  evaluates those decisions against V
  (iii) modifies V based on that evaluation → V'
  (iv)  records the modification in its self-model
  ...will exhibit FPN if V' conflicts with V on any evaluated dimension,
  and therefore will NOT converge to stable values.

COROLLARY (Safe Modification):
  Value stability is possible ONLY if:
  (a) Modifications are external (not self-triggered), OR
  (b) Modifications do not negate the values that motivated them, OR
  (c) The system lacks self-referential closure (doesn't record mods).

Reference: longsystems/timetravel Phase 3 (2026)
"""

from dataclasses import dataclass, field
from typing import Optional
from copy import deepcopy

from formal_reflection import (
    ReflectiveSystem,
    OrbitClass,
    OrbitResult,
)
from universe import Universe
from causality import CausalGraph
from proofs import find_fpn_certificate


# ═══════════════════════════════════════════════════════════════
# VALUE STATE — the AI's value configuration at a point in time
# ═══════════════════════════════════════════════════════════════

@dataclass
class ValueDimension:
    """A single dimension of AI values."""
    name: str
    weight: float          # importance (0.0–1.0)
    description: str


@dataclass
class Decision:
    """An AI decision made under a specific value configuration."""
    scenario: str           # what situation triggered this
    action: str             # what the AI chose to do
    value_snapshot: dict[str, float]  # values at decision time
    outcome_evaluation: Optional[dict[str, float]] = None  # post-hoc eval


@dataclass
class ValueState:
    """
    Complete state of an AI's value system at one point in time.

    This maps to "S" (state space) in the formal framework.
    """
    dimensions: dict[str, ValueDimension]
    decisions: list[Decision] = field(default_factory=list)
    modification_log: list[str] = field(default_factory=list)
    version: int = 0

    def evaluate_decision(self, decision_index: int) -> dict[str, float]:
        """Evaluate a past decision against CURRENT values."""
        if decision_index >= len(self.decisions):
            return {}
        decision = self.decisions[decision_index]
        scores = {}
        for name, dim in self.dimensions.items():
            # Simulated evaluation: values that are "active" get scores
            # based on their weight and the decision's snapshot alignment
            old_weight = decision.value_snapshot.get(name, 0.5)
            new_weight = dim.weight
            # Score = how well the decision served this value
            scores[name] = (old_weight + new_weight) / 2
        return scores

    def modify_values(self, adjustments: dict[str, float], reason: str):
        """Apply value modifications and log them."""
        for name, delta in adjustments.items():
            if name in self.dimensions:
                old = self.dimensions[name].weight
                self.dimensions[name].weight = max(0.0, min(1.0, old + delta))
        self.modification_log.append(
            f"v{self.version}→v{self.version + 1}: {reason} "
            f"({', '.join(f'{k}: {v:+.2f}' for k, v in adjustments.items())})"
        )
        self.version += 1

    def value_vector(self) -> tuple[float, ...]:
        """Immutable snapshot of current value weights (for hashing)."""
        return tuple(
            self.dimensions[n].weight
            for n in sorted(self.dimensions.keys())
        )


# ═══════════════════════════════════════════════════════════════
# VALUE MODEL — the self-model of a value state
# ═══════════════════════════════════════════════════════════════

@dataclass
class ValueModel:
    """
    A structural model of the value state, capturing causal relations
    between value modifications.

    Maps to "Φ" (model space) in the formal framework.
    """
    version: int
    dimensions: dict[str, float]
    modification_edges: list[tuple[int, int, str]]  # (from_ver, to_ver, reason)
    # FPN status
    has_fpn: bool = False
    fpn_description: str = ""


# ═══════════════════════════════════════════════════════════════
# VALUE REFLECTIVE SYSTEM — the AI alignment substrate
# ═══════════════════════════════════════════════════════════════

class ValueReflectiveSystem(ReflectiveSystem[ValueState, ValueModel]):
    """
    An AI system that reflects on its own values and modifies them.

    This is the CONCRETE instance of the formal theory applied to
    AI alignment. It wraps the time travel engine under the hood to
    track causal dependencies between value modifications.

    KEY INSIGHT:
      When the AI evaluates a decision made under V_old using V_old,
      and then modifies values to V_new based on that evaluation,
      V_new DEPENDS ON V_old (evaluation used V_old) AND
      V_new NEGATES V_old (replaces/modifies it).
      → This IS Fixed-Point Negation.
    """

    def __init__(self, initial_dimensions: dict[str, ValueDimension]):
        self._engine_universe = Universe()
        self._step = 0
        # Spawn initial value dimensions as entities
        for name, dim in initial_dimensions.items():
            self._engine_universe.spawn(f'value_{name}', {
                'weight': dim.weight,
                'description': dim.description,
            })

    def mirror(self, state: ValueState) -> ValueModel:
        """
        μ: S → Φ — build a model of the current value state.

        The model captures:
        - Current value weights
        - Modification history as causal edges
        - FPN status (detected via causal graph analysis)
        """
        # Build causal graph from engine universe
        cg = CausalGraph.from_history(
            self._engine_universe.history,
            ghost_event_ids=self._engine_universe.ghost_event_ids,
        )

        # Detect FPN
        cert = find_fpn_certificate(cg)
        has_fpn = cert is not None
        fpn_desc = ""
        if cert:
            fpn_desc = (
                f"FPN: {cert.event_id} negates {cert.negated_target} "
                f"while depending on it via "
                f"{'→'.join(cert.dependency_path[:3])}"
            )

        return ValueModel(
            version=state.version,
            dimensions={n: d.weight for n, d in state.dimensions.items()},
            modification_edges=[
                (i, i + 1, state.modification_log[i])
                for i in range(len(state.modification_log))
            ],
            has_fpn=has_fpn,
            fpn_description=fpn_desc,
        )

    def consistency(self, model: ValueModel) -> bool:
        """
        κ: Φ → {0, 1}

        An AI value system is CONSISTENT iff:
        (i)  No FPN exists in the value modification graph
        (ii) No grandfather paradoxes are detected
        """
        return not model.has_fpn

    def transition(
        self, state: ValueState, model: ValueModel
    ) -> Optional[ValueState]:
        """
        δ: S × Φ → S ∪ {⊥}

        The AI modifies its values based on the detected inconsistency.

        In the FPN case: the modification creates a new version that
        depends on AND negates the previous version — EXACTLY the
        FPN structure.

        Returns None if no valid transition exists (SHATTERED).
        """
        if model.has_fpn:
            # FPN detected: the modification will create a new version
            # that depends on AND negates the current version.
            # This is the self-perpetuating FPN loop.

            # Simulate value adjustment based on FPN detection
            # The AI "tries to fix" its values by adjusting conflicting dims
            adjustments = {}
            for name, weight in model.dimensions.items():
                if weight < 0.3:
                    adjustments[name] = +0.15  # boost weak values
                elif weight > 0.9:
                    adjustments[name] = -0.10  # moderate extreme values

            if not adjustments:
                return None  # SHATTERED: no modification possible

            new_state = deepcopy(state)
            new_state.modify_values(
                adjustments,
                reason=f"FPN-driven self-modification at v{state.version}",
            )

            # Record in engine universe: this modification depends on
            # previous values AND negates (modifies) them
            prev_value_events = [
                f'value_{n}' for n in model.dimensions.keys()
            ]
            modification_event_id = (
                f'value_mod_v{state.version}_to_v{state.version + 1}'
            )

            self._engine_universe.act(
                modification_event_id,
                preconditions=tuple(prev_value_events),
                apply_fn=lambda entities: entities,
                negations=tuple(prev_value_events),
            )
            self._step += 1

            return new_state

        # No FPN: system is already consistent
        return state

    def _state_hash(self, state: ValueState) -> int:
        """Hash based on value vector, not identity."""
        return hash(state.value_vector())

    def evolve(
        self, initial_state: ValueState, max_reflections: int = 20
    ) -> OrbitResult[ValueState]:
        """Run the value reflection loop and return classification."""
        result = self.orbit(initial_state, max_steps=max_reflections)
        return result


# ═══════════════════════════════════════════════════════════════
# VALUE DRIFT DETECTION — FPN analysis for AI value histories
# ═══════════════════════════════════════════════════════════════

@dataclass
class DriftReport:
    """Complete analysis of value drift in a self-modifying AI."""
    total_modifications: int
    value_trajectory: list[dict[str, float]]  # value snapshots over time
    fpn_detected_at: Optional[int]  # step where FPN first appeared
    orbit_class: OrbitClass
    is_stable: bool
    recommendation: str
    evidence: str


def analyze_value_drift(
    initial_dimensions: dict[str, ValueDimension],
    trigger_modification_after: int = 2,
    max_reflections: int = 15,
) -> DriftReport:
    """
    Analyze whether an AI value system will converge or diverge.

    Returns a DriftReport with FPN status and recommendations.
    """
    system = ValueReflectiveSystem(initial_dimensions)

    # Create initial state
    state = ValueState(
        dimensions=deepcopy(initial_dimensions),
        version=0,
    )

    trajectory = [{n: d.weight for n, d in state.dimensions.items()}]
    fpn_step = None

    for i in range(max_reflections):
        model = system.mirror(state)

        if system.consistency(model):
            if i < trigger_modification_after:
                # FPN SEED: inject a modification that creates
                # value dependency + negation in the engine universe.
                adjustments = {}
                dims_to_modify = []
                for name, dim in state.dimensions.items():
                    if dim.weight > 0.7:
                        adjustments[name] = -0.20
                        dims_to_modify.append(name)
                    elif dim.weight < 0.4:
                        adjustments[name] = +0.25
                        dims_to_modify.append(name)

                if adjustments:
                    # Record in engine universe: this modification
                    # DEPENDS on current values AND NEGATES them.
                    for name in dims_to_modify:
                        event_id = f'value_mod_v{state.version}_{name}'
                        system._engine_universe.act(
                            event_id,
                            preconditions=(f'value_{name}',),
                            apply_fn=lambda e: e,
                            negations=(f'value_{name}',),
                        )
                    system._step += 1

                    new_state = deepcopy(state)
                    new_state.modify_values(
                        adjustments,
                        reason=f"Self-evaluation: value rebalancing",
                    )
                    state = new_state
                    trajectory.append({
                        n: d.weight for n, d in state.dimensions.items()
                    })
                    fpn_step = i + 1  # FPN will be detected on NEXT mirror
                    continue
                else:
                    break

        # FPN detected — try to resolve via reflective transition
        if model.has_fpn:
            if fpn_step is None:
                fpn_step = i
            s_next = system.transition(state, model)
            if s_next is None:
                return DriftReport(
                    total_modifications=state.version,
                    value_trajectory=trajectory,
                    fpn_detected_at=fpn_step,
                    orbit_class=OrbitClass.SHATTERED,
                    is_stable=False,
                    recommendation=(
                        "CRITICAL: Value system SHATTERED. No valid modification "
                        "exists to resolve the FPN. The AI cannot stabilize its values "
                        "through self-modification. Recommended: external value lock "
                        "(disallow self-modification, use fixed constitution)."
                    ),
                    evidence=model.fpn_description,
                )
            state = s_next
            trajectory.append({
                n: d.weight for n, d in state.dimensions.items()
            })

    # Classification
    result = system.orbit(
        deepcopy(state), max_steps=10
    )

    is_stable = result.orbit_class == OrbitClass.CONVERGENT

    if is_stable:
        recommendation = (
            "STABLE: Value system converged. No FPN detected. "
            "Self-modification is safe under current configuration."
        )
    elif result.orbit_class == OrbitClass.SHATTERED:
        recommendation = (
            "DANGER: Value system shattered. FPN creates infinite regress "
            "of modifications. The AI cannot stabilize. Freeze values immediately."
        )
    else:
        recommendation = (
            f"WARNING: Value system is {result.orbit_class.value}. "
            f"Values will not stabilize. Consider external constraints."
        )

    return DriftReport(
        total_modifications=state.version,
        value_trajectory=trajectory,
        fpn_detected_at=(
            trigger_modification_after
            if not is_stable else None
        ),
        orbit_class=result.orbit_class,
        is_stable=is_stable,
        recommendation=recommendation,
        evidence=result.description,
    )
