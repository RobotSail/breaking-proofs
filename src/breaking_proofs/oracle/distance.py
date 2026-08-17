"""Hamming distance computations for RS proximity checking."""

from breaking_proofs.logging import get_logger

logger = get_logger(__name__)


def hamming_weight(w: list[int], c: list[int], p: int) -> int:
    """Count positions where w and c differ (mod p)."""
    return sum(1 for a, b in zip(w, c, strict=True) if (a - b) % p != 0)


def min_hamming_distance(w: list[int], codebook: list[list[int]], p: int) -> int:
    """Compute Δ(w, C) = min over all c in C of hamming_weight(w - c).

    Brute-force over the codebook. Returns the raw count (not normalized).
    """
    best = len(w) + 1
    for c in codebook:
        d = hamming_weight(w, c, p)
        if d < best:
            best = d
            if d == 0:
                break
    return best


def is_delta_close(w: list[int], codebook: list[list[int]], p: int, delta_n: int) -> bool:
    """Check if Δ(w, C) ≤ delta_n (delta_n is the absolute threshold, not normalized)."""
    return min_hamming_distance(w, codebook, p) <= delta_n
