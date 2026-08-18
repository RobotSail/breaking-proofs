"""KKH26 counterexample construction.

Monomial codewords f = X^(r·m), g = X^((r-1)·m) evaluated over
D = ⟨ω⟩ of order n in F_p. Sub-subgroup H = ⟨ω^m⟩ of order s.

Reference: arXiv:2604.09724 (Kambiré exposition of KKH ePrint 2026/782)
"""

from dataclasses import dataclass
from itertools import combinations
from math import comb

from breaking_proofs.logging import get_logger
from breaking_proofs.oracle.field import build_evaluation_domain
from breaking_proofs.search.params import KKH26Params

logger = get_logger(__name__)

MAX_SUMSET_COMBINATIONS = 10_000_000


def evaluate_monomial(degree: int, domain: list[int], p: int) -> list[int]:
    """Evaluate the monomial X^degree at each point of domain, mod p."""
    return [pow(x, degree, p) for x in domain]


def build_subgroup(domain: list[int], m: int, s: int) -> list[int]:
    """Extract H = ⟨ω^m⟩ from D = ⟨ω⟩: every m-th element, order s."""
    return [domain[i * m] for i in range(s)]


def r_fold_sumset(elements: list[int], r: int, p: int) -> set[int]:
    """Compute {h₁ + h₂ + … + hᵣ mod p : hᵢ ∈ elements, all distinct}."""
    return {sum(combo) % p for combo in combinations(elements, r)}


@dataclass
class KKH26Instance:
    """A concrete KKH26 counterexample instance."""

    params: KKH26Params
    domain: list[int]
    f: list[int]
    g: list[int]
    subgroup: list[int]
    witnesses: set[int] | None


def build_kkh26_instance(
    params: KKH26Params,
    compute_witnesses: bool = True,
) -> KKH26Instance:
    """Build a KKH26 instance from derived parameters."""
    domain = build_evaluation_domain(params.p, params.n)

    f_degree = params.r * params.m
    g_degree = (params.r - 1) * params.m

    f = evaluate_monomial(f_degree, domain, params.p)
    g = evaluate_monomial(g_degree, domain, params.p)

    subgroup = build_subgroup(domain, params.m, params.s)

    witnesses = None
    if compute_witnesses and comb(params.s, params.r) <= MAX_SUMSET_COMBINATIONS:
        witnesses = r_fold_sumset(subgroup, params.r, params.p)

    logger.info(
        "built_kkh26_instance",
        p=params.p,
        n=params.n,
        k=params.k,
        f_degree=f_degree,
        g_degree=g_degree,
        witness_count=len(witnesses) if witnesses is not None else "skipped",
    )

    return KKH26Instance(
        params=params,
        domain=domain,
        f=f,
        g=g,
        subgroup=subgroup,
        witnesses=witnesses,
    )
