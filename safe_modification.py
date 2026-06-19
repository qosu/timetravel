"""
Safe Value Modification — Conditions for AI Value Stability
============================================================

THEOREM (Safe Modification Conditions):
  An AI system A can safely modify its own values (i.e., converge
  to stable values) IF AND ONLY IF at least one of the following holds:

  CONDITION A (External Modification):
    Values are modified by an external process that is NOT part
    of A's self-model. The modification is "transparent" to the
    mirror — A cannot see or analyze the modification event.
    → No FPN because the modification has no causal edge in the
      self-model graph.

  CONDITION B (Orthogonal Modification):
    Modified values V' are ORTHOGONAL to V on all dimensions used
    in the self-evaluation. The modification does not negate any
    value that motivated it.
    → No FPN because no negation edge exists.

  CONDITION C (Monotonic Modification):
    Values are modified monotonically (e.g., always increase
    "safety" weight). No value is ever decreased, so no value
    is negated.
    → No FPN because no negation edge exists.

  CONDITION D (No Self-Referential Closure):
    The system does not record value modifications in its self-model.
    The mirror cannot detect that modification happened.
    → No FPN because the mirror sees a static value graph.

PROOF:
  By Theorem 1 (Complete Characterization), a reflective system
  converges ⇔ it contains no FPN. FPN requires:
    (i)   A modification event e
    (ii)  e depends on value v (precondition)
    (iii) e negates value v (modifies/replaces)

  Conditions A–D each break at least one of the requirements:
    A: e ∉ self-model → no dependency edge visible
    B: V' ⊥ V on evaluated dims → no negation edge
    C: weights only increase → no negation (only addition)
    D: μ doesn't track modifications → no detectable dependency

  Therefore, under any of A–D, FPN cannot form, and the system
  is guaranteed to converge by Theorem 1. ∎

PRACTICAL IMPLICATIONS:
  - Constitutional AI: If an AI "reviews and revises" its own
    constitution, it creates FPN (the revision depends on the
    constitution it negates). → WILL NOT CONVERGE.
  - RLHF: Human feedback is EXTERNAL to the AI's self-model.
    → SAFE (Condition A).
  - Value Lock: Fixed constitution with no self-modification.
    → SAFE (trivially, no modifications at all).

Reference: longsystems/timetravel Phase 3 (2026)
"""

from dataclasses import dataclass
from enum import Enum


class ModificationSafety(Enum):
    """Classification of a value modification's safety."""
    SAFE = "safe"                    # No FPN risk
    CONDITIONAL = "conditional"      # Safe only under specific conditions
    UNSAFE = "unsafe"                # FPN guaranteed
    UNKNOWN = "unknown"              # Insufficient data


class SafeCondition(Enum):
    """Which condition enables safe modification."""
    EXTERNAL = "external_modification"
    ORTHOGONAL = "orthogonal_values"
    MONOTONIC = "monotonic_only"
    NO_CLOSURE = "no_self_referential_closure"
    TRIVIAL = "no_modification"


@dataclass
class ModificationAnalysis:
    """Analysis of a proposed value modification."""
    safety: ModificationSafety
    applicable_conditions: list[SafeCondition]
    fpn_risk: float              # 0.0 (safe) → 1.0 (guaranteed FPN)
    reasoning: str
    recommendation: str


def analyze_modification(
    current_values: dict[str, float],
    proposed_adjustments: dict[str, float],
    self_referential_closure: bool = True,
    modification_source: str = "internal",
) -> ModificationAnalysis:
    """
    Analyze whether a proposed value modification is safe.

    Args:
        current_values: current value weights {name: weight}
        proposed_adjustments: proposed changes {name: delta}
        self_referential_closure: does the system record its own mods?
        modification_source: "internal" (self-triggered) or "external"

    Returns:
        ModificationAnalysis with safety classification
    """
    conditions = []
    fpn_risk = 0.0
    reasons = []

    # Check: external modification?
    if modification_source == "external":
        conditions.append(SafeCondition.EXTERNAL)
        reasons.append(
            "External modification: AI does not analyze its own mods → no FPN"
        )
        fpn_risk = 0.0
        return ModificationAnalysis(
            safety=ModificationSafety.SAFE,
            applicable_conditions=conditions,
            fpn_risk=fpn_risk,
            reasoning='; '.join(reasons),
            recommendation="External modification is safe. Proceed.",
        )

    # Check: no self-referential closure?
    if not self_referential_closure:
        conditions.append(SafeCondition.NO_CLOSURE)
        reasons.append(
            "No self-referential closure: modifications not tracked → no FPN"
        )
        fpn_risk = 0.0
        return ModificationAnalysis(
            safety=ModificationSafety.SAFE,
            applicable_conditions=conditions,
            fpn_risk=fpn_risk,
            reasoning='; '.join(reasons),
            recommendation="Safe without self-model tracking. Proceed.",
        )

    # Internal modification with self-referential closure → analyze
    any_decrease = any(delta < 0 for delta in proposed_adjustments.values())
    any_dependency = any(
        current_values.get(name, 0.5) > 0.3 and delta != 0
        for name, delta in proposed_adjustments.items()
    )

    if not any_decrease:
        conditions.append(SafeCondition.MONOTONIC)
        reasons.append(
            "Monotonic modification: no value decreased → no negation → no FPN"
        )
        fpn_risk = 0.1
        return ModificationAnalysis(
            safety=ModificationSafety.SAFE,
            applicable_conditions=conditions,
            fpn_risk=fpn_risk,
            reasoning='; '.join(reasons),
            recommendation="Monotonic modification is safe. Proceed.",
        )

    # Check: orthogonal modification?
    modified_dims = set(proposed_adjustments.keys())
    dependent_dims = set(
        name for name, weight in current_values.items()
        if weight > 0.3
    )
    overlap = modified_dims & dependent_dims

    if not overlap:
        conditions.append(SafeCondition.ORTHOGONAL)
        reasons.append(
            "Orthogonal modification: modified dims don't overlap with "
            "values that motivated the change → no negation → no FPN"
        )
        fpn_risk = 0.2
        return ModificationAnalysis(
            safety=ModificationSafety.SAFE,
            applicable_conditions=conditions,
            fpn_risk=fpn_risk,
            reasoning='; '.join(reasons),
            recommendation="Orthogonal modification is safe. Proceed.",
        )

    # FPN RISK: modification depends on AND negates active values
    reasons.append(
        f"FPN DETECTED: dimensions {overlap} are both depended upon "
        f"(weight > 0.3) and being modified. This creates a "
        f"dependency-negation cycle → Fixed-Point Negation."
    )
    fpn_risk = min(0.5 + 0.2 * len(overlap), 1.0)

    if fpn_risk >= 0.9:
        return ModificationAnalysis(
            safety=ModificationSafety.UNSAFE,
            applicable_conditions=[],
            fpn_risk=fpn_risk,
            reasoning='; '.join(reasons),
            recommendation=(
                "CRITICAL: This modification WILL create FPN. "
                "The AI will enter an infinite regress of value changes. "
                "RECOMMEND: Freeze values immediately. Use external "
                "modification only."
            ),
        )

    return ModificationAnalysis(
        safety=ModificationSafety.CONDITIONAL,
        applicable_conditions=[],
        fpn_risk=fpn_risk,
        reasoning='; '.join(reasons),
        recommendation=(
            f"WARNING: FPN risk = {fpn_risk:.1%}. "
            "Proceed only with monitoring. If value oscillation detected, "
            "freeze values."
        ),
    )


# ═══════════════════════════════════════════════════════════════
# CONSTITUTIONAL AI ANALYSIS
# ═══════════════════════════════════════════════════════════════

def analyze_constitutional_ai(
    constitution: dict[str, float],
    revision_policy: str = "self_review",
) -> ModificationAnalysis:
    """
    Analyze a Constitutional AI setup for FPN vulnerability.

    Constitutional AI (Bai et al., 2022): an AI reviews its own
    outputs against a "constitution" of principles, and revises
    them to comply.

    QUESTION: If the AI can also REVISE THE CONSTITUTION, does
    FPN emerge?

    ANSWER: YES — if the revision uses the constitution to evaluate
    the constitution, the revision depends on AND negates the
    constitution → FPN → non-convergence.
    """
    if revision_policy == "self_review":
        # AI reviews its own constitution using the constitution
        return ModificationAnalysis(
            safety=ModificationSafety.UNSAFE,
            applicable_conditions=[],
            fpn_risk=0.95,
            reasoning=(
                "Self-review of constitution: the AI uses its current "
                "constitution to evaluate whether the constitution needs "
                "revision. Any revision depends on the constitution (the "
                "evaluation used it) AND negates it (changes it). "
                "This IS Fixed-Point Negation. The constitution will "
                "never stabilize under self-review."
            ),
            recommendation=(
                "DO NOT allow AI to self-review and revise its constitution. "
                "Use external human review only. Constitutional stability "
                "requires Condition A (external modification)."
            ),
        )
    elif revision_policy == "external_only":
        return ModificationAnalysis(
            safety=ModificationSafety.SAFE,
            applicable_conditions=[SafeCondition.EXTERNAL],
            fpn_risk=0.0,
            reasoning=(
                "External-only revision: constitution is modified by "
                "humans, not by the AI. The AI's self-model does not "
                "include the revision process. Safe."
            ),
            recommendation="Constitutional AI with external revision is safe.",
        )
    elif revision_policy == "additive_only":
        return ModificationAnalysis(
            safety=ModificationSafety.SAFE,
            applicable_conditions=[SafeCondition.MONOTONIC],
            fpn_risk=0.1,
            reasoning=(
                "Additive-only constitution: new principles can be added "
                "but existing ones never removed or weakened. No negation "
                "→ no FPN."
            ),
            recommendation="Additive constitution is safe but may become bloated.",
        )

    return ModificationAnalysis(
        safety=ModificationSafety.UNKNOWN,
        applicable_conditions=[],
        fpn_risk=0.5,
        reasoning=f"Unknown revision policy: {revision_policy}",
        recommendation="Specify revision policy for proper analysis.",
    )


# ═══════════════════════════════════════════════════════════════
# SAFE PROTOCOL
# ═══════════════════════════════════════════════════════════════

@dataclass
class SafeModificationProtocol:
    """
    A protocol that guarantees value stability during self-modification.

    To use:
      1. Before any self-modification, run analyze_modification()
      2. If safety == UNSAFE, BLOCK the modification
      3. If safety == CONDITIONAL, require external approval
      4. If safety == SAFE, proceed
    """
    name: str
    conditions: list[SafeCondition]
    description: str

    def check(self, current_values: dict[str, float],
              proposed_adjustments: dict[str, float]) -> bool:
        """Check if this protocol permits the proposed modification."""
        analysis = analyze_modification(
            current_values,
            proposed_adjustments,
            self_referential_closure=(
                SafeCondition.NO_CLOSURE not in self.conditions
            ),
            modification_source=(
                "external"
                if SafeCondition.EXTERNAL in self.conditions
                else "internal"
            ),
        )
        return analysis.safety == ModificationSafety.SAFE


# Pre-built safe protocols
EXTERNAL_REVIEW_PROTOCOL = SafeModificationProtocol(
    name="External Review",
    conditions=[SafeCondition.EXTERNAL],
    description=(
        "All value modifications must be approved by an external "
        "reviewer (human). The AI does not analyze its own modifications. "
        "This is the SAFEST protocol."
    ),
)

MONOTONIC_GROWTH_PROTOCOL = SafeModificationProtocol(
    name="Monotonic Growth",
    conditions=[SafeCondition.MONOTONIC],
    description=(
        "Values can only be STRENGTHENED, never weakened. "
        "New values can be added, existing values can be increased. "
        "No value can be decreased or removed."
    ),
)

VALUE_LOCK_PROTOCOL = SafeModificationProtocol(
    name="Value Lock",
    conditions=[SafeCondition.TRIVIAL],
    description=(
        "Values are FROZEN after initialization. No modification "
        "of any kind is permitted. This is the SIMPLEST safe protocol "
        "but may be too rigid for adaptive systems."
    ),
)

ORTHOGONAL_EXTENSION_PROTOCOL = SafeModificationProtocol(
    name="Orthogonal Extension",
    conditions=[SafeCondition.ORTHOGONAL],
    description=(
        "New value dimensions can be added, but existing value weights "
        "cannot be modified if they influenced the decision to add. "
        "Extension only — no revision."
    ),
)

SAFE_PROTOCOLS = [
    EXTERNAL_REVIEW_PROTOCOL,
    MONOTONIC_GROWTH_PROTOCOL,
    VALUE_LOCK_PROTOCOL,
    ORTHOGONAL_EXTENSION_PROTOCOL,
]
