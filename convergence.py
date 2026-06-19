"""
Convergence Analysis — classify the fate of a self-referential universe.

When a ReflectiveUniverse runs its mirror-solve-modify loop, it exhibits
one of four asymptotic behaviors:

  CONVERGENT   — reaches a fixed point (no paradoxes) in finite steps
  OSCILLATING  — cycles through a finite set of states indefinitely
  DIVERGENT    — visits unboundedly many unique states (infinite regress)
  SHATTERED    — encounters an unresolvable paradox (RealityFracture)

This module provides tools to detect, classify, and visualize these
behaviors, including attractor basin analysis.
"""

from dataclasses import dataclass
from enum import Enum

from singularity import (
    ReflectiveUniverse,
    ReflectStatus,
    SingularityReport,
)


class ConvergenceClass(Enum):
    CONVERGENT = "convergent"
    OSCILLATING = "oscillating"
    DIVERGENT = "divergent"
    SHATTERED = "shattered"


@dataclass
class ConvergenceAnalysis:
    """Complete analysis of a reflective loop's asymptotic behavior."""
    convergence_class: ConvergenceClass
    report: SingularityReport
    state_trace: list[int]                    # state hashes in order
    cycle_detected: bool
    cycle_period: int = 0
    convergence_rate: float = 0.0             # steps to converge / total events

    def summary(self) -> str:
        lines = [
            f"Convergence: {self.convergence_class.value.upper()}",
            f"Iterations:  {self.report.total_iterations}",
            f"States:      {self.report.visited_states} unique",
        ]
        if self.cycle_detected:
            lines.append(f"Cycle:       period={self.cycle_period}")
        if self.convergence_class == ConvergenceClass.CONVERGENT:
            lines.append(f"Converged in {self.report.total_iterations} steps")
        elif self.convergence_class == ConvergenceClass.OSCILLATING:
            osc = self.report.oscillation_cycle or []
            lines.append(f"Oscillation: {len(osc)} states in cycle starting at iter {osc[0] if osc else '?'}")
        elif self.convergence_class == ConvergenceClass.DIVERGENT:
            lines.append("No convergence or cycle detected within depth limit")
        elif self.convergence_class == ConvergenceClass.SHATTERED:
            lines.append("Universe fractured — no consistent subset exists")
        return "\n".join(lines)


def analyze(reflective: ReflectiveUniverse, max_iterations: int = 200) -> ConvergenceAnalysis:
    """
    Run the reflective loop to completion (or depth cap) and classify
    the asymptotic behavior.
    """
    reflective.max_iterations = max_iterations
    report = reflective.resolve_until()

    if report.final_status == ReflectStatus.CONSISTENT:
        conv_class = ConvergenceClass.CONVERGENT
    elif report.final_status == ReflectStatus.OSCILLATING:
        conv_class = ConvergenceClass.OSCILLATING
    elif report.final_status == ReflectStatus.SHATTERED:
        conv_class = ConvergenceClass.SHATTERED
    else:
        conv_class = ConvergenceClass.DIVERGENT

    cycle_detected = report.oscillation_cycle is not None
    cycle_period = len(report.oscillation_cycle) if report.oscillation_cycle else 0

    return ConvergenceAnalysis(
        convergence_class=conv_class,
        report=report,
        state_trace=list(reflective.state_hashes),
        cycle_detected=cycle_detected,
        cycle_period=cycle_period,
        convergence_rate=(
            report.total_iterations / max(len(reflective.u.history), 1)
        ),
    )


def trace_states(reflective: ReflectiveUniverse, max_iter: int = 50) -> list[dict]:
    """
    Run the reflective loop and capture detailed state at each iteration.
    Returns a trace suitable for visualization.
    """
    reflective.max_iterations = max_iter
    trace = []

    for i in range(max_iter):
        cg = reflective.mirror()
        paradoxes = cg.detect_paradoxes()
        grandfathers = [p for p in paradoxes if p.ptype.value == 'grandfather']

        entry = {
            'iteration': i,
            'tick': reflective.u.tick,
            'history_len': len(reflective.u.history),
            'entity_count': len(reflective.u.entities),
            'ghost_count': len(reflective.u.ghost_event_ids),
            'paradox_count': len(paradoxes),
            'grandfather_count': len(grandfathers),
            'state_hash': reflective._structural_fingerprint(),
        }

        if not grandfathers:
            entry['status'] = 'consistent'
            trace.append(entry)
            break

        result = reflective.reflect()
        entry['status'] = result.status.value
        if result.resolution:
            entry['removed'] = list(result.resolution.removed_events)
        trace.append(entry)

    return trace
