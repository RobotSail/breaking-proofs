"""KKH26 paper-native parameterization and search space generation.

Parameterizes the KKH26 counterexample construction in the paper's native
variables (alpha, rho, K, C) and derives RS code parameters (p, n, k).

Reference: arXiv:2604.09724 (Kambiré exposition of KKH ePrint 2026/782)
"""

import math
from dataclasses import dataclass

from breaking_proofs.logging import get_logger

logger = get_logger(__name__)


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def find_prime_for_domain(n: int) -> int:
    """Find smallest prime p with p ≡ 1 (mod n)."""
    p = n + 1
    while not _is_prime(p):
        p += n
    return p


@dataclass(frozen=True)
class KKH26Params:
    """Full parameter set for a KKH26 construction instance.

    Paper-native inputs: alpha, rho_num, rho_den, K, C.
    Derived: s, m, n, r, k, p, delta_n.
    """

    alpha: int
    rho_num: int
    rho_den: int
    K: int
    C: float
    s: int
    m: int
    n: int
    r: int
    k: int
    p: int
    delta_n: int

    @property
    def rho(self) -> float:
        return self.rho_num / self.rho_den

    @staticmethod
    def derive(
        alpha: int,
        rho_num: int,
        rho_den: int,
        K: int,
        C: float,
    ) -> "KKH26Params | None":
        """Derive full parameters from paper-native inputs. Returns None if invalid."""
        if alpha < 1 or rho_num < 1 or rho_den < 1 or K < 1 or C <= 0:
            return None
        if K & (K - 1) != 0:
            return None
        if rho_den & (rho_den - 1) != 0:
            return None

        rho = rho_num / rho_den
        if rho >= 0.5:
            return None

        bound_log = C / (rho * math.log(1 / (2 * rho)))
        bound_const = 9 / (2 * math.log(8))
        if bound_log >= K or bound_const >= K:
            return None

        s = 1 << alpha
        if s % K != 0:
            return None
        beta = s // K - alpha
        if beta < 0:
            return None
        m = 1 << beta

        n = s * m
        rs_product = rho_num * s
        if rs_product % rho_den != 0:
            return None
        r = rs_product // rho_den + 2
        k = (r - 2) * m
        if k <= 0 or k >= n:
            return None

        p = find_prime_for_domain(n)
        delta_n = n - r * m
        if delta_n < 0:
            return None

        logger.info(
            "derived_kkh26_params",
            alpha=alpha,
            rho=f"{rho_num}/{rho_den}",
            K=K,
            s=s,
            m=m,
            n=n,
            r=r,
            k=k,
            p=p,
            delta_n=delta_n,
        )

        return KKH26Params(
            alpha=alpha,
            rho_num=rho_num,
            rho_den=rho_den,
            K=K,
            C=C,
            s=s,
            m=m,
            n=n,
            r=r,
            k=k,
            p=p,
            delta_n=delta_n,
        )


def generate_candidates(
    max_alpha: int = 8,
    rates: list[tuple[int, int]] | None = None,
    C: float = 0.5,
) -> list[KKH26Params]:
    """Generate valid KKH26 parameter tuples, smallest instances first.

    Args:
        max_alpha: Maximum subgroup exponent to try.
        rates: List of (numerator, denominator) for dyadic rates.
        C: Free constant controlling list size.

    Returns:
        Sorted list of valid parameter tuples (by code length n, then k).
    """
    if rates is None:
        rates = [(1, 4), (1, 8), (1, 16)]

    results: list[KKH26Params] = []
    seen: set[tuple[int, int, int]] = set()

    for alpha in range(1, max_alpha + 1):
        for rho_num, rho_den in rates:
            for k_exp in range(2, 2 * alpha + 1):
                K = 1 << k_exp
                params = KKH26Params.derive(alpha, rho_num, rho_den, K, C)
                if params is not None:
                    key = (params.p, params.n, params.k)
                    if key not in seen:
                        seen.add(key)
                        results.append(params)

    results.sort(key=lambda p: (p.n, p.k, p.p))
    return results
