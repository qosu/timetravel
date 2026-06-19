"""
Grandfather Paradox — Full Observable Demo.

Demonstrates the complete Time Travel Engine pipeline:
  1. Digital Universe — timeline construction
  2. Causal Graph — automatic paradox detection
  3. Novikov Solver — self-consistency enforcement
  4. Timeline Forest — multiple history branching

Run: python3 demo_grandfather.py
"""

import sys
from universe import Universe
from causality import CausalGraph
from novikov import NovikovSolver
from timelines import TimelineForest


def sep(title: str = ""):
    print(f"\n{'─'*60}")
    if title:
        print(f"  {title}")
        print(f"{'─'*60}")


def demo():
    # ── Phase 1: Build the Timeline ────────────────────────────
    sep("PHASE 1: CONSTRUCTING THE TIMELINE")

    u = Universe()
    print("Tick 0: The universe begins. A grandfather exists.")
    g = u.spawn('grandfather', {'status': 'alive', 'age': 30})

    print("Tick 1: Grandfather begets a parent.")
    u.checkpoint('EDEN')  # The point of no return
    p = u.spawn('parent', {'status': 'alive', 'age': 0}, preconditions=(g,))

    print("Tick 2: Parent begets a child — the future time traveler.")
    t = u.spawn('traveler', {'status': 'alive', 'age': 0}, preconditions=(p,))

    print(f"\n  Entities: {list(u.entities.keys())}")
    print(f"  Checkpoints: {list(u.checkpoints.keys())}")

    # ── Phase 2: Show the Causal Chain ─────────────────────────
    sep("PHASE 2: CAUSAL DEPENDENCY CHAIN")

    print("Causal chain before time travel:")
    for e in u.history:
        deps = ', '.join(e.preconditions) if e.preconditions else 'none'
        negs = ', '.join(e.negations) if e.negations else 'none'
        print(f"  tick={e.tick} | {e.event_id}")
        print(f"    depends on: [{deps}]")
        print(f"    negates:    [{negs}]")

    # ── Phase 3: Time Travel ───────────────────────────────────
    sep("PHASE 3: TIME TRAVEL — BACK TO EDEN")

    print("The traveler activates the time machine...")
    print("Destination: EDEN checkpoint (tick 1)")
    u.travel_to('EDEN')

    print(f"\n  Current tick: {u.tick}")
    print(f"  Active entities: {list(u.entities.keys())}")
    print(f"  Ghost events: {list(u.ghost_event_ids)}")

    # ── Phase 4: The Killing ───────────────────────────────────
    sep("PHASE 4: THE PARADOXICAL ACT")

    print("The traveler attempts to kill grandfather...")
    print("This action:")
    print("  - Depends on: traveler existing (a GHOST event!)")
    print("  - Negates: grandfather, parent, AND traveler")
    k = u.kill('grandfather',
               preconditions=(t,),      # depends on future event
               negations=(g, p, t))     # destroys own causal chain

    print(f"\n  Kill event: {k}")
    print(f"  Entities after kill: {list(u.entities.keys())}")

    # ── Phase 5: Paradox Detection ─────────────────────────────
    sep("PHASE 5: PARADOX DETECTION")

    graph = CausalGraph.from_history(u.history, ghost_event_ids=u.ghost_event_ids)
    paradoxes = graph.detect_paradoxes()

    if not paradoxes:
        print("  ⚠️  No paradoxes detected — this should not happen!")
        sys.exit(1)

    print(f"  🔴 {len(paradoxes)} PARADOX(ES) DETECTED:\n")
    for px in paradoxes:
        severity_bar = "█" * int(px.severity * 10) + "░" * (10 - int(px.severity * 10))
        print(f"  ┌─ [{px.ptype.value.upper()}]")
        print(f"  │  Severity: [{severity_bar}] {px.severity:.2f}")
        print(f"  │  Cycle:    {' → '.join(px.cycle)}")
        print(f"  │  {px.description}")
        print(f"  └─")

    # ── Phase 6: Novikov Resolution ────────────────────────────
    sep("PHASE 6: NOVIKOV SELF-CONSISTENCY RESOLUTION")

    solver = NovikovSolver(graph)
    result = solver.resolve()

    from novikov import NovikovResolution, RealityFracture

    if isinstance(result, NovikovResolution):
        print(f"  ✅ NOVIKOV CONSISTENT\n")
        print(f"  The universe enforces self-consistency.")
        print(f"  Events KEPT:    {result.kept_events}")
        print(f"  Events REMOVED: {result.removed_events}")
        print(f"\n  → {result.description}")
        print(f"\n  💡 The traveler CANNOT kill grandfather.")
        print(f"     Something always intervenes. The bullet jams.")
        print(f"     The gun misfires. The traveler slips.")
        print(f"     The universe protects its own consistency.")

        # Show all possible resolutions
        all_res = solver.all_resolutions()
        if len(all_res) > 1:
            print(f"\n  Alternative resolutions exist ({len(all_res)} total):")
            for r in all_res[1:]:
                print(f"    • Remove {r.removed_events}")

    elif isinstance(result, RealityFracture):
        print(f"  💀 REALITY FRACTURE\n")
        print(f"  {result.description}")
        print(f"  Fracture depth: {result.fracture_depth}")
        print(f"  Conflicting: {result.conflicting_events}")
        print(f"\n  ⚡ The universe CANNOT resolve this paradox.")
        print(f"     Multiple histories MUST branch.")

    # ── Phase 7: Timeline Forest ───────────────────────────────
    sep("PHASE 7: TIMELINE FOREST")

    forest = TimelineForest.from_universe(u)
    print(forest.summary())
    print(f"\n  Reality fractured: {forest.is_fractured}")
    print(f"  Active timeline:  {forest.active_id}")
    print(f"  Branch count:     {forest.branch_count}")

    # ── Phase 8: Causal Fracture Metrics ───────────────────────
    sep("PHASE 8: CAUSAL FRACTURE METRICS")

    total_events = len(u.history)
    ghost_count = len(u.ghost_event_ids)
    paradox_count = len(paradoxes)
    grandfather_count = sum(1 for p in paradoxes if p.ptype.value == 'grandfather')
    ghost_dep_count = sum(1 for p in paradoxes if p.ptype.value == 'ghost_dependency')

    max_severity = max((p.severity for p in paradoxes), default=0)
    avg_severity = sum(p.severity for p in paradoxes) / len(paradoxes) if paradoxes else 0

    # Causal fracture score: composite metric
    fracture_score = (
        0.3 * (ghost_count / max(total_events, 1)) +
        0.4 * max_severity +
        0.3 * (paradox_count / max(total_events, 1))
    )

    print(f"  Total events:        {total_events}")
    print(f"  Ghost events:        {ghost_count} ({ghost_count/max(total_events,1):.0%})")
    print(f"  Paradoxes detected:  {paradox_count}")
    print(f"    - Grandfather:     {grandfather_count}")
    print(f"    - Ghost dependency:{ghost_dep_count}")
    print(f"  Max severity:        {max_severity:.2f}")
    print(f"  Avg severity:        {avg_severity:.2f}")
    print(f"  ──────────────────────────")
    print(f"  FRACTURE SCORE:      {fracture_score:.3f}")
    fracture_bar = "▓" * int(fracture_score * 20) + "░" * (20 - int(fracture_score * 20))
    print(f"  [{fracture_bar}]")

    if fracture_score > 0.7:
        print(f"\n  🔴 CRITICAL: Reality is severely fractured.")
    elif fracture_score > 0.3:
        print(f"\n  🟡 WARNING: Significant causal stress detected.")
    else:
        print(f"\n  🟢 STABLE: Timeline is largely consistent.")

    sep("DEMO COMPLETE")
    print("\n  The Grandfather Paradox has been observed, detected,")
    print("  classified, and resolved through digital time travel.")
    print("  Novikov self-consistency holds in this universe —")
    print("  but the causal fracture score reveals the stress")
    print("  that paradoxes place on the fabric of reality.\n")


if __name__ == '__main__':
    demo()
