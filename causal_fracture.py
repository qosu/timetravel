"""
Causal Fracture Spectrum — continuous metric for reality consistency.

Instead of binary paradox detection (yes/no), this module produces a
continuous "fracture score" from 0.0 (perfectly consistent) to 1.0
(complete reality breakdown with irreconcilable paradoxes).

Phases:
  STABLE    [0.00–0.20] — no paradoxes, clean causal chain
  STRESSED  [0.20–0.40] — ghost dependencies, minor anomalies
  CRACKING  [0.40–0.60] — bootstrap paradoxes, non-trivial cycles
  FRACTURED [0.60–0.80] — grandfather paradoxes, negation cycles
  SHATTERED [0.80–1.00] — multiple irreconcilable paradoxes, branching required

This is the novel contribution: operationalizing "reality breaking" as
a quantitative, measurable property of a causal event graph.
"""

from dataclasses import dataclass
from enum import Enum

from universe import CausalEvent
from causality import CausalGraph, ParadoxType


class FracturePhase(Enum):
    STABLE = "stable"
    STRESSED = "stressed"
    CRACKING = "cracking"
    FRACTURED = "fractured"
    SHATTERED = "shattered"


@dataclass
class FractureSpectrum:
    """Complete causal fracture analysis of a universe."""
    score: float                     # 0.0 → 1.0
    phase: FracturePhase
    components: dict[str, float]     # sub-metrics
    description: str
    axiom_violation: float = 0.0     # external shock magnitude (0.0 → 1.0)


def analyze(universe_history: list[CausalEvent],
            ghost_event_ids: set[str]) -> FractureSpectrum:
    """
    Compute the causal fracture spectrum for a universe.

    The score is a weighted composite of five sub-metrics, each
    capturing a different dimension of causal consistency.
    """
    graph = CausalGraph.from_history(universe_history, ghost_event_ids=ghost_event_ids)
    paradoxes = graph.detect_paradoxes()

    total = max(len(universe_history), 1)

    # ── Component 1: Ghost Density (weight 0.15) ──────────────
    ghost_ratio = len(ghost_event_ids) / total

    # ── Component 2: Paradox Severity (weight 0.35) ───────────
    severity_scores = {
        ParadoxType.GHOST_DEPENDENCY: 0.30,
        ParadoxType.PREDESTINATION: 0.10,
        ParadoxType.BOOTSTRAP: 0.55,
        ParadoxType.GRANDFATHER: 1.00,
    }
    max_paradox_severity = max(
        (severity_scores.get(p.ptype, 0.5) for p in paradoxes),
        default=0.0
    )
    avg_paradox_severity = (
        sum(severity_scores.get(p.ptype, 0.5) for p in paradoxes) / len(paradoxes)
        if paradoxes else 0.0
    )
    paradox_severity = 0.6 * max_paradox_severity + 0.4 * avg_paradox_severity

    # ── Component 3: Cycle Density (weight 0.20) ──────────────
    cycles = graph.find_cycles()
    cycle_density = min(len(cycles) / max(total, 1), 1.0)

    # ── Component 4: Negation Ratio (weight 0.15) ─────────────
    total_negations = sum(len(n) for n in graph.negates.values())
    total_depends = sum(len(d) for d in graph.depends.values())
    negation_ratio = (
        total_negations / max(total_negations + total_depends, 1)
    )

    # ── Component 5: Resolution Cost (weight 0.15) ────────────
    # This requires the Novikov solver, but we compute a simpler proxy:
    # number of events that are both negating AND negated
    negating_events = set()
    negated_events = set()
    for eid, negs in graph.negates.items():
        if negs:
            negating_events.add(eid)
        negated_events.update(negs)
    mutual_negation = len(negating_events & negated_events)
    resolution_cost = min(mutual_negation / max(len(negating_events | negated_events), 1), 1.0)

    # ── Composite Score ───────────────────────────────────────
    score = (
        0.15 * ghost_ratio +
        0.35 * paradox_severity +
        0.20 * cycle_density +
        0.15 * negation_ratio +
        0.15 * resolution_cost
    )

    score = min(max(score, 0.0), 1.0)

    # ── Phase Determination ───────────────────────────────────
    if score < 0.20:
        phase = FracturePhase.STABLE
        desc = "Causal fabric is intact. No paradoxes detected."
    elif score < 0.40:
        phase = FracturePhase.STRESSED
        desc = "Minor anomalies: ghost dependencies or weak causal loops."
    elif score < 0.60:
        phase = FracturePhase.CRACKING
        desc = "Significant causal stress: bootstrap paradoxes or dense cycles."
    elif score < 0.80:
        phase = FracturePhase.FRACTURED
        desc = "Reality fracture: grandfather paradoxes, negation cycles active."
    else:
        phase = FracturePhase.SHATTERED
        desc = "Reality is shattered. Multiple irreconcilable paradoxes. Branching unavoidable."

    components = {
        "ghost_density": round(ghost_ratio, 4),
        "paradox_severity": round(paradox_severity, 4),
        "cycle_density": round(cycle_density, 4),
        "negation_ratio": round(negation_ratio, 4),
        "resolution_cost": round(resolution_cost, 4),
    }

    return FractureSpectrum(
        score=round(score, 4),
        phase=phase,
        components=components,
        description=desc,
    )


def phase_report(spectrum: FractureSpectrum) -> str:
    """Multi-line human-readable fracture report."""
    bar_len = 30
    filled = int(spectrum.score * bar_len)
    bar = "▓" * filled + "░" * (bar_len - filled)

    lines = [
        "╔══════════════════════════════════════════╗",
        "║  CAUSAL FRACTURE SPECTRUM               ║",
        "╠══════════════════════════════════════════╣",
        f"║  Score: {spectrum.score:.4f}  [{bar}]  ║",
        f"║  Phase: {spectrum.phase.value.upper():<12s}                      ║",
        "╠══════════════════════════════════════════╣",
    ]
    for name, value in spectrum.components.items():
        sub_bar_len = 20
        sub_filled = int(value * sub_bar_len)
        sub_bar = "█" * sub_filled + "·" * (sub_bar_len - sub_filled)
        lines.append(f"║  {name:<18s} {value:.3f} [{sub_bar}] ║")

    lines.append("╠══════════════════════════════════════════╣")
    lines.append(f"║  {spectrum.description:<38s} ║")
    lines.append("╚══════════════════════════════════════════╝")

    return "\n".join(lines)
