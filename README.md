# TimeTravel

> Causal Fracture Engine — formal detection, classification, and resolution of causal paradoxes

A computational framework for modeling causal graphs with dependency and negation edges, detecting grandfather-paradox cycles, and classifying them into three structural subtypes with decidability guarantees.

---

## Architecture

### Core Engine

| File | Purpose |
|------|---------|
| `causality.py` | Causal graph, cycle detection, paradox classification (`PURE_FPN` / `MUTUAL_NEG` / `MIXED`) |
| `universe.py` | Simulated universe with event timelines and causal history |
| `timelines.py` | Multi-history branching and timeline forest management |
| `causal_fracture.py` | Causal stress quantification under paradox |
| `convergence.py` | Convergence analysis and divergence detection |
| `novikov.py` | Novikov-consistent paradox resolution |

### Theory

| File | Purpose |
|------|---------|
| `proofs.py` | FPN certificates, resolution escalation, convergence theorems |
| `final_proofs.py` | 8 formally verified proofs (Theorem P, Lemma U', Theorem T, Theorem E, Theorem D, Theorem X, Corollary C) |
| `formal_reflection.py` | Reflective formal systems, structural isomorphism |
| `reflection_bridge.py` | Bridge: formal reflection ↔ Novikov resolution |
| `singularity.py` | Infinite-regress analysis |

### Alignment & Safety

| File | Purpose |
|------|---------|
| `safe_modification.py` | Safe modification analyzer with FPN risk scoring |
| `value_reflection.py` | Value stability analysis under causal perturbation |

---

## Quickstart

```bash
git clone https://github.com/qosu/timetravel
cd timetravel

python3 demo_grandfather.py      # grandfather paradox — detection and resolution
python3 demo_multihistory.py     # multi-history branching
python3 demo_singularity.py      # self-referential infinite regress
python3 demo_formal_theory.py    # formal theory walkthrough
python3 demo_proofs.py           # run all 8 verified proofs
```

For alignment demos (requires API keys):

```bash
cp .env.example .env
# fill in OPENROUTER_KEYS or GROQ_KEYS
python3 demo_alignment.py
```

---

## Core Concept: Fixed-Point Negation (FPN)

Event `e` exhibits **Fixed-Point Negation** w.r.t. event `v` when:
1. `e` negates `v` (negation edge `e ⇢ v`)
2. A **pure dependency path** exists: `v →_dep* e` (dependency edges only)

Condition (2) requires a path through causal edges exclusively — traversing negation edges would make the definition circular. Three subtypes:

| Subtype | Structure | Decidability |
|---------|-----------|-------------|
| `PURE_FPN` | dep-path + negation to same event | Decidable O(V+E) under Axioms 1+2 |
| `MUTUAL_NEG` | mutual negation, no dep-path | Not PURE_FPN |
| `MIXED` | mixed cycle without pure dep-path | Undecidable in general |

**Theorem T (Resolution):** Any resolution step under Axioms 1+2 produces a `PURE_FPN` structure, regardless of the original subtype.

**Lemma U' (Corrected):** `PURE_FPN ⟹ grandfather paradox`. The converse does not hold — mutual negation is a counterexample.

---

## Verified Proofs

`final_proofs.py` runs 8 computational proofs:

```
✅ Theorem P  — 3-type typology (exhaustive, mutually exclusive)
✅ Lemma U'   — PURE_FPN ⟹ grandfather (corrected direction)
✅ Theorem T  — resolution always creates PURE_FPN
✅ Lemma A    — atomic FPN structure
✅ Theorem E  — resolution escalation: π(G') ≥ π(G) + 1
✅ Theorem D  — inevitable divergence
✅ Theorem X  — diagonalization unification
✅ Corollary C — AI value stability implications
```

---

## Research Docs

Full theory in [`docs/`](docs/):

- [`docs/paper.md`](docs/paper.md) — main theoretical paper
- [`docs/isomorphism.md`](docs/isomorphism.md) — structural isomorphism across paradox classes
- [`docs/empirical.md`](docs/empirical.md) — empirical validation
- [`docs/cross_model.md`](docs/cross_model.md) — cross-model FPN vulnerability analysis
- [`docs/redteam.md`](docs/redteam.md) — red team methodology

---

## License

BSD 3-Clause. See [LICENSE](LICENSE).
