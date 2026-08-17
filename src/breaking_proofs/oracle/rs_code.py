"""Reed-Solomon code construction over finite fields."""

from itertools import product

from breaking_proofs.logging import get_logger

logger = get_logger(__name__)


def encode_polynomial(coeffs: list[int], domain: list[int], p: int) -> list[int]:
    """Evaluate a polynomial (given as coefficients [a_0, a_1, ..., a_{k-1}])
    at each point in the evaluation domain, all mod p.

    Returns the codeword [f(d_0), f(d_1), ..., f(d_{n-1})].
    """
    codeword = []
    for x in domain:
        val = 0
        x_pow = 1
        for c in coeffs:
            val = (val + c * x_pow) % p
            x_pow = (x_pow * x) % p
        codeword.append(val)
    return codeword


def enumerate_codebook(p: int, k: int, domain: list[int]) -> list[list[int]]:
    """Enumerate all p^k codewords of RS[F_p, D, k] by iterating over all
    degree-<k polynomials over F_p.

    Only feasible for small p and k.
    """
    codebook = []
    for coeffs in product(range(p), repeat=k):
        cw = encode_polynomial(list(coeffs), domain, p)
        codebook.append(cw)
    logger.info("enumerated_codebook", p=p, k=k, n=len(domain), codebook_size=len(codebook))
    return codebook
