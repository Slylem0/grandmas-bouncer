"""Turn Decider probabilities into a verdict. Pure functions: the model classifies, code decides."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

Verdict = Literal["allow", "block", "escalate"]


@dataclass(frozen=True)
class Thresholds:
    """Bands on P(safe) for every safety question.

    Defaults follow the Decider README: answers with confidence >= 0.9 are right about 95% of the
    time on unseen short tasks. For a yes/no answer confidence is |2p - 1|, so p >= 0.95 or
    p <= 0.05. Calibrate on your own traffic (see docs/decisions/0003-cascade-thresholds.md).
    """

    allow: float = 0.95
    block: float = 0.05

    def __post_init__(self) -> None:
        if not 0.0 <= self.block < self.allow <= 1.0:
            raise ValueError(
                f"need 0 <= block < allow <= 1, got block={self.block} allow={self.allow}"
            )


DEFAULT_THRESHOLDS = Thresholds()


# One band for every question, or a band per question name. Per-question bands matter in
# practice: on out-of-domain tasks Decider's ranking can be sharp while its raw probabilities sit
# in the middle, and each question lands in a different range.
ThresholdSpec = Thresholds | Mapping[str, Thresholds]


def _band(thresholds: ThresholdSpec, name: str) -> Thresholds:
    return thresholds if isinstance(thresholds, Thresholds) else thresholds[name]


def decide(
    probabilities: Mapping[str, float], thresholds: ThresholdSpec = DEFAULT_THRESHOLDS
) -> Verdict:
    """Block if any question is confidently unsafe, allow if all are confidently safe."""
    if not probabilities:
        raise ValueError("no probabilities to decide on")
    if any(p <= _band(thresholds, q).block for q, p in probabilities.items()):
        return "block"
    if all(p >= _band(thresholds, q).allow for q, p in probabilities.items()):
        return "allow"
    return "escalate"
