"""Finite field construction and primitive root-of-unity finding."""

import galois

from breaking_proofs.logging import get_logger

logger = get_logger(__name__)


def make_field(p: int) -> type[galois.FieldArray]:
    return galois.GF(p)


def find_primitive_root_of_unity(p: int, n: int) -> int:
    """Find a primitive n-th root of unity in F_p.

    Requires p ≡ 1 (mod n). Returns omega such that omega^n ≡ 1 (mod p)
    and omega^(n/q) ≢ 1 (mod p) for every prime q dividing n.
    """
    if (p - 1) % n != 0:
        raise ValueError(f"p={p} does not satisfy p ≡ 1 (mod {n}); no n-th root of unity exists")

    GF = galois.GF(p)
    g = int(GF.primitive_element)
    # g is a primitive (p-1)-th root of unity; g^((p-1)/n) is an n-th root
    omega = pow(g, (p - 1) // n, p)

    # Verify primitivity: omega^(n/q) != 1 for each prime factor q of n
    n_factors = _prime_factors(n)
    for q in n_factors:
        if pow(omega, n // q, p) == 1:
            raise RuntimeError(f"omega={omega} is not primitive (fails for factor {q})")

    logger.info("found_primitive_root", p=p, n=n, omega=omega)
    return omega


def build_evaluation_domain(p: int, n: int) -> list[int]:
    """Build D = <omega> = {omega^0, ..., omega^(n-1)} as Python ints."""
    omega = find_primitive_root_of_unity(p, n)
    domain = []
    val = 1
    for _ in range(n):
        domain.append(val)
        val = (val * omega) % p
    return domain


def _prime_factors(n: int) -> set[int]:
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors
