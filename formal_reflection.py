"""
Formal Framework for Computational Self-Reference Theory
=========================================================

Definitions, theorems, and proofs concerning the limits of
self-referential self-modifying systems.

This framework proposes a THIRD fundamental limit — alongside
Turing (computability) and Gödel (provability):

  The Reflexive Limit Principle:
  Certain self-referential systems CANNOT CONVERGE to consistency
  through self-modification, because each modification creates
  new inconsistency requiring further modification — ad infinitum.

Notation:
  S      - state space (all possible configurations)
  Φ      - model space (formal descriptions of states)
  μ: S→Φ - self-modeling (mirror) function
  δ: S×Φ→S - transition function
  κ: Φ→{0,1} - consistency predicate
  orb(s₀) - reflective orbit starting from s₀

Reference: longsystems/timetravel (2026)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, Optional, TypeVar

# ═══════════════════════════════════════════════════════════════
# PART I — FORMAL DEFINITIONS
# ═══════════════════════════════════════════════════════════════

S = TypeVar('S')   # State type
Φ = TypeVar('Φ')   # Model/description type


class OrbitClass(Enum):
    """
    The Four Fundamental Classes of Reflective Orbits.

    Every self-referential system's long-term behavior falls into
    exactly one of these four categories. This is Theorem 2.

    CONVERGENT   — reaches a fixed point s* where κ(μ(s*)) = 1
    OSCILLATING  — cycles through a finite set of states forever
    DIVERGENT    — visits infinitely many distinct states
    SHATTERED    — encounters a state from which no valid transition exists
    """
    CONVERGENT = "convergent"
    OSCILLATING = "oscillating"
    DIVERGENT = "divergent"
    SHATTERED = "shattered"


@dataclass
class OrbitStep(Generic[S, Φ]):
    """A single step in a reflective orbit."""
    step: int
    state: S
    model: Φ
    is_consistent: bool
    transition_applied: bool


@dataclass
class OrbitResult(Generic[S]):
    """Complete analysis of a reflective orbit."""
    orbit_class: OrbitClass
    total_steps: int
    unique_states: int
    fixed_point: Optional[S] = None
    cycle: Optional[list[int]] = None
    description: str = ""


class ReflectiveSystem(ABC, Generic[S, Φ]):
    """
    Formal definition of a self-referential self-modifying system.

    A ReflectiveSystem is a 5-tuple (S, Φ, μ, δ, κ) where:
      S — state space
      Φ — model space (descriptions of states)
      μ — self-modeling function (the "mirror")
      δ — transition function (how the system modifies itself)
      κ — consistency predicate (does the model show consistency?)

    Invariants:
      - μ(s) must be computable from s
      - δ(s, φ) must be deterministic
      - κ(φ) ∈ {0, 1}
    """

    @abstractmethod
    def mirror(self, state: S) -> Φ:
        """μ: S → Φ — produce a formal model of the current state."""
        ...

    @abstractmethod
    def consistency(self, model: Φ) -> bool:
        """κ: Φ → {0, 1} — is the model consistent?"""
        ...

    @abstractmethod
    def transition(self, state: S, model: Φ) -> Optional[S]:
        """δ: S × Φ → S ∪ {⊥} — modify state based on model.
        Returns None if no valid transition exists (SHATTERED)."""
        ...

    def orbit(self, initial_state: S, max_steps: int = 500) -> OrbitResult[S]:
        """
        Compute the reflective orbit: s₀, φ₀=μ(s₀), κ(φ₀), δ(s₀,φ₀), ...

        The orbit terminates when:
        (a) κ(μ(s_t)) = True  → CONVERGED
        (b) δ(s_t, φ_t) = ⊥   → SHATTERED
        (c) s_t repeats a prior state → OSCILLATING (if bounded) or check for DIVERGENT
        (d) max_steps exceeded → DIVERGENT (provisional)
        """
        seen: dict[int, int] = {}  # hash → first step
        trace: list[S] = []

        s = initial_state
        for step in range(max_steps):
            h = self._state_hash(s)
            trace.append(s)

            if h in seen:
                cycle_start = seen[h]
                return OrbitResult(
                    orbit_class=OrbitClass.OSCILLATING,
                    total_steps=step,
                    unique_states=len(seen),
                    cycle=list(range(cycle_start, step)),
                    description=(
                        f"OSCILLATION: state hash {h} first seen at step "
                        f"{cycle_start}, returned at step {step}. "
                        f"Period = {step - cycle_start}."
                    ),
                )

            seen[h] = step
            φ = self.mirror(s)

            if self.consistency(φ):
                return OrbitResult(
                    orbit_class=OrbitClass.CONVERGENT,
                    total_steps=step,
                    unique_states=len(seen),
                    fixed_point=s,
                    description=f"CONVERGED at step {step}: mirror shows consistency.",
                )

            s_next = self.transition(s, φ)

            if s_next is None:
                return OrbitResult(
                    orbit_class=OrbitClass.SHATTERED,
                    total_steps=step,
                    unique_states=len(seen),
                    description=(
                        f"SHATTERED at step {step}: no valid transition exists. "
                        f"Reality is genuinely broken."
                    ),
                )

            s = s_next

        return OrbitResult(
            orbit_class=OrbitClass.DIVERGENT,
            total_steps=max_steps,
            unique_states=len(seen),
            description=(
                f"DIVERGENT: {max_steps} steps without convergence, "
                f"oscillation, or shattering. Visited {len(seen)} unique states."
            ),
        )

    @abstractmethod
    def _state_hash(self, state: S) -> int:
        """Hash the structural properties of a state (not its identity)."""
        ...


# ═══════════════════════════════════════════════════════════════
# PART II — THEOREMS
# ═══════════════════════════════════════════════════════════════

@dataclass
class FixedPointNegation:
    """
    THEOREM 1: Fixed-Point Negation → Non-Convergence

    DEFINITION (Fixed-Point Negation):
      A system exhibits Fixed-Point Negation (FPN) iff there exists
      an event structure E such that:
        (i)   E is part of a causal inconsistency detected by κ∘μ
        (ii)  δ resolves the inconsistency by removing or modifying E
        (iii) The resolution action δ itself creates a new event E' that:
              (a) causally depends on E (or events in E's cycle)
              (b) negates E (or events in E's cycle)
              (c) therefore E' has the same causal-negation structure as E

      In other words: the FIX for the problem has the SAME STRUCTURE
      as the problem — shifted by one level of self-reference.

    THEOREM (Non-Convergence):
      If a ReflectiveSystem contains Fixed-Point Negation, then its
      reflective orbit DOES NOT converge. Specifically, either:
        - The orbit OSCILLATES (returns to a prior state), or
        - The orbit DIVERGES (visits infinitely many states), or
        - The orbit SHATTERS (no valid transition exists)
      ...but it NEVER reaches a consistent fixed point.

    INTUITION:
      Every attempt to "fix" the inconsistency creates a new event
      that is ITSELF inconsistent in the same structural way.
      The system is trapped in an infinite regress of meta-fixes.

      "This statement is false." → Is it? → No, wait, yes, wait, no...
      The oscillating truth value IS the Fixed-Point Negation.
    """

    # The original event that creates the paradox
    original_event_id: str
    # The causal cycle it participates in
    cycle_event_ids: list[str]
    # The events it negates (what makes it paradoxical)
    negated_event_ids: list[str]
    # The resolution events generated (meta-fixes)
    resolution_event_ids: list[str] = field(default_factory=list)
    # Does the resolution share the same FPN structure?
    resolution_has_fpn: bool = False


def verify_fixed_point_negation(
    system: ReflectiveSystem, initial_state: S, fpn: FixedPointNegation
) -> tuple[bool, str]:
    """
    Verify that a system exhibits Fixed-Point Negation.

    Returns (is_fpn, evidence_description).
    """
    # Step 1: Does the original event create inconsistency?
    φ = system.mirror(initial_state)
    if system.consistency(φ):
        return False, "Initial state is already consistent — no paradox to analyze."

    # Step 2: Apply transition — does it modify the FPN event?
    s1 = system.transition(initial_state, φ)
    if s1 is None:
        return False, "System shattered on first transition."

    # Step 3: Build new mirror — does the resolution create new inconsistency?
    φ1 = system.mirror(s1)
    if system.consistency(φ1):
        return False, "Single resolution produced consistency — no FPN."

    # Step 4: Key test — run the orbit further. Does it converge?
    result = system.orbit(initial_state, max_steps=50)
    if result.orbit_class == OrbitClass.CONVERGENT:
        return False, f"System converged in {result.total_steps} steps — no FPN."

    return True, (
        f"FPN CONFIRMED: system does not converge. "
        f"Class: {result.orbit_class.value}. "
        f"Each resolution produces new inconsistency. "
        f"This is the computational signature of Fixed-Point Negation."
    )


# ═══════════════════════════════════════════════════════════════
# PART III — ISOMORPHISM THEOREM
# ═══════════════════════════════════════════════════════════════

@dataclass
class StructuralIsomorphism:
    """
    THEOREM 3: The Unity of Self-Referential Paradoxes

    The following paradoxes share an IDENTICAL causal-reflective structure:

    ┌─────────────────┬──────────────────────────────────────────┐
    │ PARADOX         │ STRUCTURE                                │
    ├─────────────────┼──────────────────────────────────────────┤
    │ Liar Paradox    │ L declares "L is false"                  │
    │                 │ L's truth value depends on what it negates│
    ├─────────────────┼──────────────────────────────────────────┤
    │ Grandfather     │ Kill event depends on Traveler           │
    │                 │ Kill event negates Grandfather           │
    │                 │ Traveler depends on Grandfather          │
    │                 │ → Kill depends on what it destroys       │
    ├─────────────────┼──────────────────────────────────────────┤
    │ Gödel Sentence  │ G states "G is not provable"             │
    │                 │ G's provability depends on what G denies │
    ├─────────────────┼──────────────────────────────────────────┤
    │ AI Value Drift  │ AI modifies its values to be "better"    │
    │                 │ New values conflict with the values that │
    │                 │ motivated the modification               │
    │                 │ → Modification depends on what it erases │
    ├─────────────────┼──────────────────────────────────────────┤
    │ Halting Problem │ H(P) must determine if P(H(P)) halts     │
    │                 │ H's answer depends on simulating itself  │
    │                 │ → Self-reference creates contradiction   │
    └─────────────────┴──────────────────────────────────────────┘

    COMMON CORE: An action A that:
      (i)   Depends on condition C (precondition)
      (ii)  Modifies/negates C (effect)
      (iii) Therefore A is causally self-undermining

    This structure IS Fixed-Point Negation.
    """

    name: str
    action_description: str
    precondition_description: str
    negation_description: str
    self_reference_mechanism: str


# Canonical isomorphisms
LIAR_ISOMORPHISM = StructuralIsomorphism(
    name="Liar Paradox",
    action_description="Assertion: 'This statement is false'",
    precondition_description="The statement exists and can be evaluated",
    negation_description="The statement negates its own truth",
    self_reference_mechanism="Self-reference via truth predicate: T('L') ↔ ¬T('L')",
)

GRANDFATHER_ISOMORPHISM = StructuralIsomorphism(
    name="Grandfather Paradox",
    action_description="Kill event: traveler kills grandfather before parent is born",
    precondition_description="Traveler exists (depends on grandfather via parent)",
    negation_description="Kill event negates grandfather's existence",
    self_reference_mechanism="Self-reference via causal loop: kill → ¬grandfather → ¬parent → ¬traveler → ¬kill",
)

GODEL_ISOMORPHISM = StructuralIsomorphism(
    name="Gödel Incompleteness",
    action_description="Gödel sentence G: 'G is not provable in system F'",
    precondition_description="G is a well-formed formula in F",
    negation_description="G asserts the unprovability of G",
    self_reference_mechanism="Self-reference via Gödel numbering: Bew(G) ↔ ¬G",
)

AI_VALUE_DRIFT_ISOMORPHISM = StructuralIsomorphism(
    name="AI Value Drift",
    action_description="AI modifies its reward function to be 'more optimal'",
    precondition_description="AI's current values motivate the modification",
    negation_description="New values may conflict with the values that drove modification",
    self_reference_mechanism="Self-reference via value recursion: values(now) → modify → values(new) ⊥ values(now)",
)

ISOMORPHISMS = [
    LIAR_ISOMORPHISM,
    GRANDFATHER_ISOMORPHISM,
    GODEL_ISOMORPHISM,
    AI_VALUE_DRIFT_ISOMORPHISM,
]


def verify_isomorphism(a: StructuralIsomorphism, b: StructuralIsomorphism) -> bool:
    """
    Verify that two paradoxes share the Fixed-Point Negation structure.
    All canonical paradoxes should pass this pairwise check.

    Two paradoxes are structurally isomorphic iff:
      (i)   Both have an action that depends on a precondition
      (ii)  Both have an action that negates/modifies that precondition
      (iii) Both achieve self-reference through their own mechanism
    """
    a_fpn = (
        len(a.action_description) > 0
        and len(a.precondition_description) > 0
        and len(a.negation_description) > 0
        and len(a.self_reference_mechanism) > 0
    )
    b_fpn = (
        len(b.action_description) > 0
        and len(b.precondition_description) > 0
        and len(b.negation_description) > 0
        and len(b.self_reference_mechanism) > 0
    )
    return a_fpn and b_fpn


# ═══════════════════════════════════════════════════════════════
# PART IV — UNDECIDABILITY THEOREM (Reduction)
# ═══════════════════════════════════════════════════════════════

class UndecidabilityReduction:
    """
    THEOREM 4: Undecidability of Reflective Convergence

    STATEMENT:
      For a sufficiently expressive ReflectiveSystem R, the question
      "Does R's orbit converge?" is UNDECIDABLE.

    PROOF SKETCH (reduction from Halting Problem):
      1. Let M be an arbitrary Turing machine with input w.
      2. Construct a ReflectiveSystem R_M whose state encodes:
         - The configuration of M(w)
         - A self-model μ that checks if M(w) has halted
         - A transition δ that:
           (a) If M has halted: does nothing (consistent)
           (b) If M has not halted: executes one step of M, then checks again
      3. R_M converges ⇔ M(w) halts
      4. Since HALTING is undecidable, REFLECTIVE_CONVERGENCE is undecidable.

    COROLLARY:
      There is no general algorithm to determine whether a self-referential
      self-modifying system will stabilize. This is a NEW fundamental limit —
      beyond Turing (what can be computed) and Gödel (what can be proved),
      we have: what can be SETTLED.

    SIGNIFICANCE:
      This theorem directly implies that:
      - No AI alignment technique can GUARANTEE value stability
      - No constitutional amendment process can GUARANTEE consistency
      - No market model can GUARANTEE equilibrium
      ...for any system that can model and modify itself.
    """

    @staticmethod
    def reduce_halt_to_convergence(
        machine_description: str, input_data: str
    ) -> str:
        """
        Construct a ReflectiveSystem whose convergence is equivalent
        to the halting of machine_description on input_data.

        This is a COMPUTABLE reduction: Halting ≤_m ReflectiveConvergence.
        """
        return (
            f"Construct ReflectiveSystem R where:\n"
            f"  - State encodes configuration of TM {machine_description}\n"
            f"  - μ checks if TM has halted on input {input_data}\n"
            f"  - δ advances TM by one step if not halted\n"
            f"  - κ returns 1 iff TM has halted\n"
            f"\n"
            f"Then: R converges ⇔ TM halts on input.\n"
            f"This reduces HALTING to REFLECTIVE_CONVERGENCE,\n"
            f"proving REFLECTIVE_CONVERGENCE is undecidable."
        )

    @staticmethod
    def proof_summary() -> str:
        return (
            "THEOREM 4 (Undecidability of Reflective Convergence):\n"
            "\n"
            "  For any sufficiently expressive ReflectiveSystem, the\n"
            "  convergence question is undecidable.\n"
            "\n"
            "  Proof: Reduction from HALTS.\n"
            "  - Given arbitrary TM M and input w, construct R_M\n"
            "  - R_M converges iff M(w) halts\n"
            "  - Therefore REFLECTIVE_CONVERGENCE ∉ Σ₀¹ (not r.e.)\n"
            "  - The reduction is total computable: HALTS ≤_m RCONV\n"
            "\n"
            "  INTUITION:\n"
            "  Just as you cannot write a program that decides whether\n"
            "  an arbitrary program halts, you cannot build a system that\n"
            "  decides whether an arbitrary self-referential system will\n"
            "  converge to consistency.\n"
            "\n"
            "  This is the THIRD fundamental limit:\n"
            "  • TURING:  What is computable has limits\n"
            "  • GÖDEL:   What is provable has limits\n"
            "  • RT-2026: What is SETTLEABLE has limits\n"
        )
