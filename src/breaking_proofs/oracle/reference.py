"""Pure-Python reference oracle — zero external dependencies.

Uses only int and pow(base, exp, mod). Deliberately naive and
line-by-line auditable. This is the trust anchor for cross-checking
the galois-based oracle.
"""

from itertools import product


def ref_prime_factors(n: int) -> set[int]:
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


def ref_find_primitive_root(p: int) -> int:
    """Find the smallest primitive root mod p (brute force)."""
    if p == 2:
        return 1
    phi = p - 1
    factors = ref_prime_factors(phi)
    for g in range(2, p):
        if all(pow(g, phi // q, p) != 1 for q in factors):
            return g
    raise RuntimeError(f"no primitive root found for p={p}")


def ref_find_primitive_root_of_unity(p: int, n: int) -> int:
    """Find a primitive n-th root of unity in F_p."""
    if (p - 1) % n != 0:
        raise ValueError(f"p-1={p - 1} is not divisible by n={n}")
    g = ref_find_primitive_root(p)
    omega = pow(g, (p - 1) // n, p)
    for q in ref_prime_factors(n):
        if pow(omega, n // q, p) == 1:
            raise RuntimeError(f"omega={omega} is not a primitive {n}-th root of unity")
    return omega


def ref_build_domain(p: int, n: int) -> list[int]:
    omega = ref_find_primitive_root_of_unity(p, n)
    domain = []
    val = 1
    for _ in range(n):
        domain.append(val)
        val = (val * omega) % p
    return domain


def ref_encode(coeffs: list[int], domain: list[int], p: int) -> list[int]:
    codeword = []
    for x in domain:
        val = 0
        x_pow = 1
        for c in coeffs:
            val = (val + c * x_pow) % p
            x_pow = (x_pow * x) % p
        codeword.append(val)
    return codeword


def ref_enumerate_codebook(p: int, k: int, domain: list[int]) -> list[list[int]]:
    codebook = []
    for coeffs in product(range(p), repeat=k):
        cw = ref_encode(list(coeffs), domain, p)
        codebook.append(cw)
    return codebook


def ref_hamming_distance(w: list[int], c: list[int], p: int) -> int:
    return sum(1 for a, b in zip(w, c, strict=True) if (a - b) % p != 0)


def ref_min_distance(w: list[int], codebook: list[list[int]], p: int) -> int:
    best = len(w) + 1
    for c in codebook:
        d = ref_hamming_distance(w, c, p)
        if d < best:
            best = d
            if d == 0:
                break
    return best


def ref_incidence_count(
    f: list[int],
    g: list[int],
    codebook: list[list[int]],
    p: int,
    delta_n: int,
) -> int:
    count = 0
    for z in range(p):
        w = [(fi + z * gi) % p for fi, gi in zip(f, g, strict=True)]
        d = ref_min_distance(w, codebook, p)
        if d <= delta_n:
            count += 1
    return count


def ref_has_correlated_agreement(
    f: list[int],
    g: list[int],
    codebook: list[list[int]],
    p: int,
    delta_n: int,
) -> bool:
    n = len(f)
    required = n - delta_n
    for vf in codebook:
        for vg in codebook:
            agree = sum(
                1
                for i in range(n)
                if (f[i] - vf[i]) % p == 0 and (g[i] - vg[i]) % p == 0
            )
            if agree >= required:
                return True
    return False
