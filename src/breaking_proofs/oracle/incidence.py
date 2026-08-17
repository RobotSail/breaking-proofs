"""Core proximity oracle: incidence counting over affine lines."""

from breaking_proofs.logging import get_logger
from breaking_proofs.oracle.distance import min_hamming_distance
from breaking_proofs.oracle.rs_code import enumerate_codebook

logger = get_logger(__name__)


def affine_line_word(f: list[int], g: list[int], z: int, p: int) -> list[int]:
    """Compute the word f + z*g (mod p), coordinate-wise."""
    return [(fi + z * gi) % p for fi, gi in zip(f, g, strict=True)]


def incidence_count(
    f: list[int],
    g: list[int],
    codebook: list[list[int]],
    p: int,
    delta_n: int,
) -> int:
    """Count |{z in F_p : Δ(f + z*g, C) ≤ delta_n}|.

    Iterates over all z in {0, 1, ..., p-1}, computes f + z*g,
    and checks proximity to the code via brute-force distance computation.

    delta_n is the absolute distance threshold (integer, not normalized).
    All arithmetic is exact integer mod p. No floating point.
    """
    count = 0
    for z in range(p):
        w = affine_line_word(f, g, z, p)
        d = min_hamming_distance(w, codebook, p)
        if d <= delta_n:
            count += 1
    logger.info("incidence_count", p=p, n=len(f), delta_n=delta_n, count=count)
    return count


def incidence_count_from_params(
    p: int,
    n: int,
    k: int,
    f: list[int],
    g: list[int],
    delta_n: int,
    domain: list[int] | None = None,
    codebook: list[list[int]] | None = None,
) -> int:
    """Convenience wrapper: build domain/codebook if not provided, then count incidence."""
    if domain is None:
        from breaking_proofs.oracle.field import build_evaluation_domain

        domain = build_evaluation_domain(p, n)
    if codebook is None:
        codebook = enumerate_codebook(p, k, domain)
    return incidence_count(f, g, codebook, p, delta_n)
