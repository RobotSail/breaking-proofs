"""Correlated agreement checking for RS codes."""

from breaking_proofs.logging import get_logger

logger = get_logger(__name__)


def has_correlated_agreement(
    f: list[int],
    g: list[int],
    codebook: list[list[int]],
    p: int,
    delta_n: int,
) -> bool:
    """Check whether (f, g) have δ-correlated agreement with code C.

    Correlated agreement holds if there exist codewords v_f, v_g in C
    and a subdomain D' ⊆ D with |D'| ≥ n - delta_n such that
    f agrees with v_f on D' AND g agrees with v_g on D' simultaneously.

    For small codes, brute-force: try all pairs (v_f, v_g) and check
    if their joint agreement set with (f, g) is large enough.

    delta_n is the absolute distance threshold (max disagreements allowed).
    """
    n = len(f)
    required_agreement = n - delta_n

    for vf in codebook:
        for vg in codebook:
            agreement_count = sum(
                1
                for i in range(n)
                if (f[i] - vf[i]) % p == 0 and (g[i] - vg[i]) % p == 0
            )
            if agreement_count >= required_agreement:
                logger.info(
                    "correlated_agreement_found",
                    n=n,
                    delta_n=delta_n,
                    agreement=agreement_count,
                )
                return True
    return False
