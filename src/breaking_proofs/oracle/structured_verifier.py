"""Structured RS proximity verification via Lagrange interpolation.

Provides O(n^2 * k) verification as an alternative to brute-force codebook
enumeration (O(p^k * n)). The brute-force oracle in incidence.py remains
the trust anchor for small-field cross-checks (Sacred Rule 1).
"""

from itertools import combinations
from math import comb

import galois
import numpy as np

from breaking_proofs.logging import get_logger
from breaking_proofs.oracle.incidence import affine_line_word

logger = get_logger(__name__)

MAX_SUBSET_TRIALS = 2000

_gf_cache: dict[int, type] = {}


def _get_gf(p: int) -> type:
    """Return (cached) galois.GF(p) class."""
    if p not in _gf_cache:
        _gf_cache[p] = galois.GF(p)
    return _gf_cache[p]


def batch_mod_inverse(xs: list[int], p: int) -> list[int]:
    """Compute modular inverses of all xs mod p using Montgomery's trick.

    Instead of k independent pow(x, p-2, p) calls, uses 1 inversion +
    3(k-1) multiplications: accumulate running products forward, invert
    the final product, walk backward to recover individual inverses.
    """
    k = len(xs)
    if k == 0:
        return []
    if k == 1:
        return [pow(xs[0], p - 2, p)]

    prefix = [0] * k
    prefix[0] = xs[0] % p
    for i in range(1, k):
        prefix[i] = (prefix[i - 1] * (xs[i] % p)) % p

    inv_all = pow(prefix[-1], p - 2, p)

    result = [0] * k
    for i in range(k - 1, 0, -1):
        result[i] = (inv_all * prefix[i - 1]) % p
        inv_all = (inv_all * (xs[i] % p)) % p
    result[0] = inv_all

    return result


def lagrange_eval(xs: list[int], ys: list[int], x: int, p: int) -> int:
    """Evaluate the Lagrange interpolating polynomial at x mod p.

    Given k points (xs[i], ys[i]), returns Q(x) where Q is the unique
    polynomial of degree < k passing through all points.

    Uses batch_mod_inverse (Montgomery's trick) to compute all k
    denominator inversions with a single modular exponentiation.
    All arithmetic is exact integer mod p.
    """
    k = len(xs)
    denoms = [1] * k
    numers = [0] * k
    for i in range(k):
        numer = ys[i]
        denom = 1
        for j in range(k):
            if j != i:
                numer = (numer * ((x - xs[j]) % p)) % p
                denom = (denom * ((xs[i] - xs[j]) % p)) % p
        numers[i] = numer
        denoms[i] = denom

    inv_denoms = batch_mod_inverse(denoms, p)

    result = 0
    for i in range(k):
        result = (result + (numers[i] * inv_denoms[i]) % p) % p
    return result


def _count_agreement_from_subset(
    word: list[int],
    domain: list[int],
    indices: tuple[int, ...] | list[int],
    p: int,
) -> int:
    """Interpolate from subset indices and count agreement on full domain.

    Uses galois.lagrange_poly for vectorized evaluation at all domain
    points in a single call, replacing the per-point Python loop.
    """
    GF = _get_gf(p)
    xs = GF([domain[i] for i in indices])
    ys = GF([word[i] for i in indices])
    poly = galois.lagrange_poly(xs, ys)

    domain_gf = GF(domain)
    evals = poly(domain_gf)

    word_gf = GF(word)
    return int(np.sum(evals == word_gf))


def verify_agreement_set(
    word: list[int],
    domain: list[int],
    agreement_indices: list[int],
    p: int,
    k: int,
) -> tuple[bool, int]:
    """Verify claimed agreement positions via Lagrange interpolation.

    Given positions where word is claimed to agree with a codeword,
    picks k of them, interpolates the unique degree < k polynomial,
    and checks total agreement across all n domain points.

    Returns (interpolation_consistent, total_agreement_count).
    """
    n = len(domain)
    if len(agreement_indices) < k:
        return False, 0

    subset = agreement_indices[:k]
    agreement = _count_agreement_from_subset(word, domain, subset, p)

    logger.info(
        "verified_agreement_set",
        n=n,
        k=k,
        claimed_size=len(agreement_indices),
        actual_agreement=agreement,
    )
    return agreement >= len(agreement_indices), agreement


def is_delta_close_structured(
    word: list[int],
    domain: list[int],
    p: int,
    k: int,
    delta_n: int,
) -> tuple[bool, int]:
    """Check if word is within Hamming distance delta_n of RS[F_p, D, k].

    Uses Lagrange interpolation on candidate k-subsets of domain points
    instead of codebook enumeration. For small C(n, k), tries all subsets
    (exhaustive, guaranteed correct). For large C(n, k), uses sliding
    windows and strided subsets (heuristic, may have false negatives).

    Returns (is_close, best_agreement_count).
    """
    n = len(domain)
    required = n - delta_n
    if k <= 0 or required <= 0:
        return True, n

    best = 0
    total_subsets = comb(n, k)

    if total_subsets <= MAX_SUBSET_TRIALS:
        for subset in combinations(range(n), k):
            agreement = _count_agreement_from_subset(word, domain, subset, p)
            if agreement > best:
                best = agreement
            if best >= required:
                return True, best
    else:
        for start in range(n):
            subset = tuple((start + i) % n for i in range(k))
            agreement = _count_agreement_from_subset(word, domain, subset, p)
            if agreement > best:
                best = agreement
            if best >= required:
                return True, best

        stride = max(1, n // k)
        for offset in range(min(stride, n)):
            subset = tuple((offset + i * stride) % n for i in range(k))
            if len(set(subset)) == k:
                agreement = _count_agreement_from_subset(word, domain, subset, p)
                if agreement > best:
                    best = agreement
                if best >= required:
                    return True, best

    return best >= required, best


def incidence_count_structured(
    f: list[int],
    g: list[int],
    domain: list[int],
    p: int,
    k: int,
    delta_n: int,
) -> int:
    """Count |{z in F_p : delta(f + z*g, RS[F_p, D, k]) <= delta_n}|.

    Uses Lagrange interpolation instead of codebook enumeration.
    O(p * n^2 * k) instead of O(p * p^k * n).
    """
    count = 0
    for z in range(p):
        w = affine_line_word(f, g, z, p)
        is_close, _ = is_delta_close_structured(w, domain, p, k, delta_n)
        if is_close:
            count += 1

    logger.info(
        "incidence_count_structured",
        p=p,
        n=len(domain),
        k=k,
        delta_n=delta_n,
        count=count,
    )
    return count
