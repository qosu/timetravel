"""
Multiple History Branching Demo.

Demonstrates the TimelineForest when Novikov finds multiple valid
resolutions for a paradox — reality splits into parallel histories.

Run: python3 demo_multihistory.py
"""

from universe import Universe
from causality import CausalGraph
from novikov import NovikovSolver
from timelines import TimelineForest
from causal_fracture import analyze, phase_report


def demo():
    print("╔══════════════════════════════════════════════════════╗")
    print("║     MULTIPLE HISTORY BRANCHING DEMO                 ║")
    print("║     When reality cannot agree on one answer         ║")
    print("╚══════════════════════════════════════════════════════╝")

    # ── Build a mutual-negation paradox ────────────────────────
    print("\n── Constructing Mutual-Negation Paradox ──\n")

    u = Universe()

    print("Tick 0-1: Two entities enter existence: X and Y")
    x_id = u.spawn('X', {'exists': True, 'value': 'X'})
    y_id = u.spawn('Y', {'exists': True, 'value': 'Y'})

    print("Tick 2: X negates Y (X declares Y must not exist)")
    nx_id = u.act(
        'X_negates_Y',
        preconditions=(x_id,),
        apply_fn=lambda e: {**e, 'X': {**e['X'], 'target': 'Y'}},
        negations=(y_id,)
    )

    print("Tick 3: Y negates X (Y declares X must not exist)")
    ny_id = u.act(
        'Y_negates_X',
        preconditions=(y_id,),
        apply_fn=lambda e: {**e, 'Y': {**e['Y'], 'target': 'X'}},
        negations=(x_id,)
    )

    # ── Show the full history ─────────────────────────────────
    print("\n── Causal Record ──\n")
    for e in u.history:
        negs = ', '.join(e.negations) if e.negations else 'none'
        deps = ', '.join(e.preconditions) if e.preconditions else 'none'
        print(f"  [{e.tick}] {e.event_id}")
        print(f"       depends on: {deps}")
        print(f"       negates:    {negs}")

    # ── Detect ────────────────────────────────────────────────
    print("\n── Paradox Detection ──\n")
    graph = CausalGraph.from_history(u.history, ghost_event_ids=u.ghost_event_ids)
    paradoxes = graph.detect_paradoxes()
    for px in paradoxes:
        print(f"  🔴 [{px.ptype.value.upper()}] {px.description}")

    # ── Novikov ───────────────────────────────────────────────
    print("\n── Novikov Resolution Search ──\n")
    solver = NovikovSolver(graph)
    resolutions = solver.all_resolutions()
    print(f"  Found {len(resolutions)} consistent resolution(s):")
    for i, r in enumerate(resolutions):
        print(f"    {i+1}. Remove: {r.removed_events}")

    # ── Branch! ───────────────────────────────────────────────
    print("\n── Timeline Forest ──\n")
    forest = TimelineForest.from_universe(u)
    print(f"  Branches created: {forest.branch_count}")
    print(f"  Reality fractured: {forest.is_fractured}")
    print(f"  Active timeline: {forest.active_id}")
    print()

    for tid, tl in forest.timelines.items():
        marker = "→" if tid == forest.active_id else " "
        print(f"  {marker} [{tid}] — {tl.branch_reason}")
        print(f"       Events: {tl.events}")
        print()

    # ── Navigate ──────────────────────────────────────────────
    print("── Navigating Between Histories ──\n")
    for tid in forest.timelines:
        forest.switch_to(tid)
        print(f"  Switching to [{tid}]...")
        print(f"    Events: {forest.active.events}")

    # ── Fracture Spectrum ─────────────────────────────────────
    print("\n── Causal Fracture Spectrum ──\n")
    spectrum = analyze(u.history, u.ghost_event_ids)
    print(phase_report(spectrum))

    print("\n💡 The universe cannot decide between X and Y.")
    print("  Instead of choosing, it BRANCHES.")
    print("  Each branch is internally consistent.")
    print("  Each branch denies the other's existence.")
    print("  This is the Multiple History resolution")
    print("  to time travel paradoxes.\n")


if __name__ == '__main__':
    demo()
