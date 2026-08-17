"""F_5 verification of the RS proximity oracle.

RS[F_5, F_5^x, 2]:
  - Field: F_5 = {0,1,2,3,4}
  - Evaluation domain: D = F_5^x = {1,2,3,4} (multiplicative group, order 4)
  - Dimension k=2: polynomials a_0 + a_1*x with a_0, a_1 in F_5
  - Rate: rho = k/n = 2/4 = 1/2
  - Codebook: 5^2 = 25 codewords
"""

import pytest

from breaking_proofs.oracle.agreement import has_correlated_agreement
from breaking_proofs.oracle.distance import min_hamming_distance
from breaking_proofs.oracle.field import build_evaluation_domain
from breaking_proofs.oracle.incidence import incidence_count
from breaking_proofs.oracle.rs_code import encode_polynomial, enumerate_codebook


@pytest.fixture
def f5_setup():
    """Set up the RS[F_5, F_5^x, 2] code."""
    p = 5
    n = 4
    k = 2
    domain = build_evaluation_domain(p, n)
    codebook = enumerate_codebook(p, k, domain)
    return p, n, k, domain, codebook


class TestCodebookStructure:
    def test_codebook_size(self, f5_setup):
        p, n, k, domain, codebook = f5_setup
        assert len(codebook) == p**k  # 25 codewords

    def test_codeword_length(self, f5_setup):
        p, n, k, domain, codebook = f5_setup
        for cw in codebook:
            assert len(cw) == n

    def test_zero_polynomial(self, f5_setup):
        p, n, k, domain, codebook = f5_setup
        zero_cw = encode_polynomial([0, 0], domain, p)
        assert zero_cw == [0, 0, 0, 0]
        assert zero_cw in codebook

    def test_constant_polynomial(self, f5_setup):
        p, n, k, domain, codebook = f5_setup
        const_cw = encode_polynomial([3, 0], domain, p)
        assert const_cw == [3, 3, 3, 3]

    def test_identity_polynomial(self, f5_setup):
        """f(x) = x evaluates to the domain elements."""
        p, n, k, domain, codebook = f5_setup
        id_cw = encode_polynomial([0, 1], domain, p)
        assert id_cw == domain

    def test_codewords_are_distinct(self, f5_setup):
        p, n, k, domain, codebook = f5_setup
        cw_tuples = [tuple(cw) for cw in codebook]
        assert len(set(cw_tuples)) == len(cw_tuples)


class TestDistances:
    def test_codeword_has_zero_distance(self, f5_setup):
        p, n, k, domain, codebook = f5_setup
        for cw in codebook:
            assert min_hamming_distance(cw, codebook, p) == 0

    def test_minimum_distance_of_code(self, f5_setup):
        """RS[F_5, F_5^x, 2] has minimum distance n - k + 1 = 4 - 2 + 1 = 3."""
        p, n, k, domain, codebook = f5_setup
        min_d = n + 1
        for i, c1 in enumerate(codebook):
            for j, c2 in enumerate(codebook):
                if i == j:
                    continue
                from breaking_proofs.oracle.distance import hamming_weight

                d = hamming_weight(c1, c2, p)
                if d < min_d:
                    min_d = d
        assert min_d == n - k + 1  # = 3

    def test_specific_word_distance(self, f5_setup):
        """A word that differs from the closest codeword in exactly 1 position."""
        p, n, k, domain, codebook = f5_setup
        cw = encode_polynomial([1, 1], domain, p)  # f(x) = 1 + x
        # Flip one position
        modified = list(cw)
        modified[0] = (modified[0] + 1) % p
        d = min_hamming_distance(modified, codebook, p)
        assert d == 1


class TestDeltaStarReproduction:
    """Verify MCA properties of RS[F₅, F₅ˣ, 2].

    Compute ε_MCA(C, δ) = max over non-CA (f,g) of |{z : Δ(f+zg, C) ≤ δn}|/p.

    Key findings for RS[F₅, F₅ˣ, 2]:
    - At delta_n=0 (δ=0): ε_MCA = 0 (no non-codeword pair has exact codewords on line)
    - At delta_n=1 (δ=1/4): non-codeword pairs (f,g) can achieve high incidence without CA
    - At delta_n=2 (δ=1/2 = capacity): CA holds for all pairs with any incidence

    Codeword pairs always have CA (RS is linear, so f+zg is always a codeword).
    Counterexamples require non-codeword words.
    """

    def test_codeword_lines_always_have_full_incidence(self, f5_setup):
        """For codeword pairs (f,g), every f+zg is a codeword (RS linearity)."""
        p, n, k, domain, codebook = f5_setup
        for f_coeffs in [(a, b) for a in range(p) for b in range(p)]:
            f = encode_polynomial(list(f_coeffs), domain, p)
            for g_coeffs in [(a, b) for a in range(p) for b in range(p)]:
                g = encode_polynomial(list(g_coeffs), domain, p)
                if all(gi == 0 for gi in g):
                    continue
                inc = incidence_count(f, g, codebook, p, 0)
                assert inc == p, "Codeword line should have all p points as codewords"

    def test_known_counterexample_no_ca(self, f5_setup):
        """f=[0,0,0,1], g=[0,0,1,1] has high incidence at delta_n=1 without CA.

        This non-codeword pair demonstrates that MCA can fail even at delta=1/4
        for RS[F_5, F_5^x, 2]. Verified by exhaustive search over F_5^4 x F_5^4.
        """
        p, n, k, domain, codebook = f5_setup
        f = [0, 0, 0, 1]
        g = [0, 0, 1, 1]

        inc = incidence_count(f, g, codebook, p, 1)
        ca = has_correlated_agreement(f, g, codebook, p, 1)

        assert inc >= 2, f"Expected high incidence, got {inc}"
        assert not ca, "Expected no correlated agreement for this non-codeword pair"

    def test_ca_holds_at_delta_half_capacity(self, f5_setup):
        """At delta_n=2 (δ=1/2 = capacity for rate 1/2), CA should hold
        for any pair with incidence > 0, since almost any word is close."""
        p, n, k, domain, codebook = f5_setup
        f = [0, 0, 0, 1]
        g = [0, 0, 1, 1]

        inc = incidence_count(f, g, codebook, p, 2)
        ca = has_correlated_agreement(f, g, codebook, p, 2)

        assert inc == p, "At capacity, all points should be close"
        assert ca, "At capacity, CA should hold"

    def test_all_codewords_are_close_to_themselves(self, f5_setup):
        p, n, k, domain, codebook = f5_setup
        for cw in codebook:
            assert min_hamming_distance(cw, codebook, p) == 0

    def test_incidence_monotone_in_delta(self, f5_setup):
        """Incidence count should be non-decreasing as delta_n increases."""
        p, n, k, domain, codebook = f5_setup
        f = encode_polynomial([1, 2], domain, p)
        g = encode_polynomial([3, 1], domain, p)

        prev_inc = 0
        for delta_n in range(n + 1):
            inc = incidence_count(f, g, codebook, p, delta_n)
            assert inc >= prev_inc
            prev_inc = inc

        assert incidence_count(f, g, codebook, p, n) == p

    def test_incidence_monotone_non_codeword(self, f5_setup):
        """Monotonicity also holds for non-codeword pairs."""
        p, n, k, domain, codebook = f5_setup
        f = [0, 0, 0, 1]
        g = [0, 0, 1, 1]

        prev_inc = 0
        for delta_n in range(n + 1):
            inc = incidence_count(f, g, codebook, p, delta_n)
            assert inc >= prev_inc
            prev_inc = inc
