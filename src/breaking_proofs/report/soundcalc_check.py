"""Local reimplementation of UDR/JBR proximity-gap thresholds.

Hard-codes stable regime boundaries from soundcalc:
  UDR: theta <= (1 - rho) / 2
  JBR: (1 - rho) / 2 < theta < 1 - sqrt(rho)
"""

import math
from dataclasses import dataclass
from enum import Enum


class Regime(Enum):
    UDR = "udr"
    JBR = "jbr"
    BEYOND = "beyond"


@dataclass(frozen=True)
class SignificanceResult:
    regime: Regime
    rho: float
    theta: float
    current_bound: float
    measured_value: float
    is_significant: bool
    udr_bound: float
    jbr_bound: float


def udr_bound(rho: float) -> float:
    return (1 - rho) / 2


def jbr_bound(rho: float) -> float:
    return 1 - math.sqrt(rho)


def classify_regime(theta: float, rho: float) -> Regime:
    """Classify a (theta, rho) point into UDR, JBR, or BEYOND."""
    if theta <= udr_bound(rho):
        return Regime.UDR
    elif theta < jbr_bound(rho):
        return Regime.JBR
    else:
        return Regime.BEYOND


def classify_hit(theta: float, rho: float) -> SignificanceResult:
    """Classify a single search hit and determine significance.

    A hit is significant when theta exceeds the unique decoding radius,
    placing it in (or beyond) the proximity gap.
    """
    udr = udr_bound(rho)
    jbr = jbr_bound(rho)
    regime = classify_regime(theta, rho)

    if regime == Regime.UDR:
        current_bound = udr
        is_significant = False
    elif regime == Regime.JBR:
        current_bound = udr
        is_significant = True
    else:
        current_bound = jbr
        is_significant = True

    return SignificanceResult(
        regime=regime,
        rho=rho,
        theta=theta,
        current_bound=current_bound,
        measured_value=theta,
        is_significant=is_significant,
        udr_bound=udr,
        jbr_bound=jbr,
    )
