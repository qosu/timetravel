# TimeTravel

**Causal Fracture Engine — Novikov Self-Consistency in Simulated Universes**

A formal computational framework implementing Novikov self-consistency
principles from general relativity. Paradoxes that would violate causality
are detected, classified, and resolved through timeline iteration.

---

## Core Engine (6 files)

| File | Purpose |
|------|---------|
| `universe.py` | Simulated universe with event timelines and causal structure |
| `causality.py` | Causal dependency graph, cycle detection, paradox classification |
| `timelines.py` | Multi-history generation and timeline forest management |
| `causal_fracture.py` | Fracture spectrum — quantifies causal stress when paradoxes occur |
| `convergence.py` | Self-consistency convergence analysis and divergence detection |
| `novikov.py` | Paradox resolution via Novikov principle with combinatorial solver |

## Formal Theory Modules

| File | Purpose |
|------|---------|
| `proofs.py` | Theorem proofs covering FPN, resolution escalation, convergence |
| `final_proofs.py` | Diagonalization unification — 6 pairwise isomorphisms |
| `formal_reflection.py` | Reflective formal system for self-referential analysis |
| `reflection_bridge.py` | Bridge between formal reflection and Novikov resolution |
| `singularity.py` | Reflective universe with infinite regress analysis |

## Alignment & Safety Modules

| File | Purpose |
|------|---------|
| `safe_modification.py` | Safe modification analyzer with FPN risk scoring |
| `value_reflection.py` | Value reflection under causal perturbation |
| `demo_alignment.py` | AI alignment demo — value stability under paradox |

## Demos

```bash
python3 demo_grandfather.py       # Grandfather paradox — classic time travel
python3 demo_singularity.py       # Self-referential infinite regress
python3 demo_multihistory.py      # Multi-history branching and resolution
python3 demo_formal_theory.py     # Formal theory visualization
python3 demo_proofs.py            # Theorem proof walkthrough
python3 demo_alignment.py         # AI value stability experiment
```

## Research Papers

- `RT2026_PAPER.md` — Main paper: Causal Fracture in Computational Time Travel
- `RT2026_EMPIRICAL.md` — Empirical validation results
- `RT2026_ISOMORPHISM.md` — Diagonalization and isomorphism proofs
- `RT2026_QUANTUM.md` — Quantum extension of the framework
- `RT2026_CROSS_MODEL.md` — Cross-model FPN vulnerability analysis
- `RT2026_REDTEAM.md` — Red team attack methodology

## Quick Start

```bash
# Run the grandfather paradox demo
python3 demo_grandfather.py

# Run all demos
for demo in demo_*.py; do echo "=== $demo ===" && python3 "$demo"; done
```

## Configuration

```bash
cp .env.example .env
# Edit .env with your API keys (only needed for alignment demos)
```

## License

BSD 3-Clause with additional terms for commercial use.
See [LICENSE](LICENSE) for full details.
