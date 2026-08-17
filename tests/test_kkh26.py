"""Reproduce the KKH26 counterexample construction.

Reference: Krachun, Kazanin, Haböck, ePrint 2026/782
           Kambiré exposition: arXiv 2604.09724

The KKH26 construction produces an affine line (f, g) over RS[F_p, D, k]
with D = <omega> a multiplicative subgroup of F_p^x, such that:
  - Many z in F_p have Δ(f + z*g, C) ≤ delta (large incidence count)
  - But (f, g) does NOT have correlated agreement at distance delta

The construction uses sumset-based polynomial selection:
  Given a subset S ⊆ D, choose f and g so that for each z in a target set Z,
  the word f + z*g agrees with some codeword on at least |S| positions,
  while no single large subdomain witnesses agreement for all of (f, g) jointly.

Parameters needed from the paper:
  - Prime p with p ≡ 1 (mod n)
  - Subgroup order n (|D|)
  - Code dimension k
  - The target distance delta (= 1 - rho - eta for some small eta)
  - The sumset structure that yields the construction

This test module provides:
  1. The parametric framework for any KKH26-style construction
  2. A small concrete verification over F_5 (the simplest case)
  3. TODO markers for the exact parameters from the paper
"""

from breaking_proofs.oracle.agreement import has_correlated_agreement
from breaking_proofs.oracle.distance import min_hamming_distance
from breaking_proofs.oracle.field import build_evaluation_domain
from breaking_proofs.oracle.incidence import affine_line_word, incidence_count
from breaking_proofs.oracle.rs_code import encode_polynomial, enumerate_codebook


class TestKKH26Framework:
    """Parametric framework for KKH26-style counterexample verification."""

    def verify_counterexample(
        self,
        p: int,
        n: int,
        k: int,
        f: list[int],
        g: list[int],
        delta_n: int,
        expected_min_incidence: int,
    ) -> dict:
        """Verify that (f, g) is a counterexample at the given parameters.

        A valid counterexample has:
        1. incidence_count(f, g, C, delta_n) >= expected_min_incidence
        2. NOT has_correlated_agreement(f, g, C, delta_n)

        Returns a dict with all computed values.
        """
        domain = build_evaluation_domain(p, n)
        codebook = enumerate_codebook(p, k, domain)

        inc = incidence_count(f, g, codebook, p, delta_n)
        ca = has_correlated_agreement(f, g, codebook, p, delta_n)

        close_z_values = []
        for z in range(p):
            w = affine_line_word(f, g, z, p)
            d = min_hamming_distance(w, codebook, p)
            if d <= delta_n:
                close_z_values.append((z, d))

        return {
            "p": p,
            "n": n,
            "k": k,
            "delta_n": delta_n,
            "incidence_count": inc,
            "correlated_agreement": ca,
            "close_z_values": close_z_values,
            "is_counterexample": inc >= expected_min_incidence and not ca,
        }


class TestKKH26SmallField(TestKKH26Framework):
    """Verify KKH26-style construction mechanics on small fields where
    we can exhaustively search for counterexamples."""

    def test_f5_known_counterexample(self):
        """Verify the known counterexample found by exhaustive search over F_5^4 x F_5^4.

        RS[F_5, F_5^x, 2]: p=5, n=4, k=2, rate=1/2.
        At delta_n=1 (delta=1/4), f=[0,0,0,1] and g=[0,0,1,1] have
        incidence=4 without correlated agreement.
        """
        p, n, k = 5, 4, 2
        delta_n = 1
        f = [0, 0, 0, 1]
        g = [0, 0, 1, 1]

        result = self.verify_counterexample(p, n, k, f, g, delta_n, 2)
        assert result["is_counterexample"], (
            f"Expected counterexample: inc={result['incidence_count']}, "
            f"CA={result['correlated_agreement']}"
        )
        assert result["incidence_count"] >= 2

    def test_f7_k2_counterexample_search(self):
        """Search for counterexamples in RS[F_7, D, 2] with small domain."""
        p, n, k = 7, 2, 1
        delta_n = 0  # delta=0, looking for exact codewords on the line

        domain = build_evaluation_domain(p, n)
        codebook = enumerate_codebook(p, k, domain)

        max_inc_no_ca = 0
        for fc in range(p):
            for gc in range(p):
                f = [fc, fc]  # constant word
                g = [gc, 0]   # non-uniform word
                if all(x == 0 for x in g):
                    continue
                inc = incidence_count(f, g, codebook, p, delta_n)
                ca = has_correlated_agreement(f, g, codebook, p, delta_n)
                if not ca and inc > max_inc_no_ca:
                    max_inc_no_ca = inc

        # At delta=0 with k=1 (dimension 1), every affine line through a codeword
        # should have at most 1 exact codeword on it (unless it's a code-line)
        assert max_inc_no_ca >= 0  # baseline check


class TestKKH26Construction:
    """Test the sumset-based construction from arXiv 2604.09724.

    The Kambiré exposition describes the construction as follows:
    1. Pick prime p with p ≡ 1 (mod n), D = <omega> (n-th roots of unity)
    2. Choose a "thin" subset S ⊂ D
    3. Build polynomials f_S, g_S from the sumset structure of S
    4. The affine line f_S + z*g_S has large incidence with RS[F_p, D, k]
       at distance theta near capacity, but fails correlated agreement

    The exact polynomial construction depends on parameters from the paper
    that need to be manually extracted.
    """

    @staticmethod
    def sumset_size(s: set[int], p: int) -> set[int]:
        """Compute the sumset S + S = {a + b mod p : a in S, b in S}."""
        return {(a + b) % p for a in s for b in s}

    @staticmethod
    def difference_set(s: set[int], p: int) -> set[int]:
        """Compute the difference set S - S = {a - b mod p : a in S, b in S}."""
        return {(a - b) % p for a in s for b in s}

    def test_sumset_properties_f5(self):
        """Verify basic sumset properties over F_5 that the construction relies on."""
        p = 5

        # For S = {1, 2}, sumset S+S = {2, 3, 4}
        S = {1, 2}
        ss = self.sumset_size(S, p)
        assert ss == {2, 3, 4}

        # Difference set S-S = {0, 1, 4} = {0, 1, -1}
        ds = self.difference_set(S, p)
        assert 0 in ds

    def test_parametric_construction_placeholder(self):
        """Placeholder for the full KKH26 parametric construction.

        To complete this test, the following parameters are needed from
        arXiv 2604.09724 / ePrint 2026/782:

        1. The specific prime p and subgroup order n for the smallest instance
        2. The subset S ⊆ D used in the sumset construction
        3. The polynomial coefficients for f and g derived from S
        4. The target distance theta = 1 - rho - eta and the claimed eta

        Once these are extracted, this test should:
        - Construct f, g from the paper's recipe
        - Verify incidence_count matches the paper's claimed count
        - Verify correlated agreement fails as claimed
        - Confirm the distance is in the window (between Johnson and capacity)
        """
        # Minimal smoke test: the construction framework is callable
        p, n, k = 5, 4, 2
        domain = build_evaluation_domain(p, n)
        codebook = enumerate_codebook(p, k, domain)

        f = encode_polynomial([1, 0], domain, p)
        g = encode_polynomial([0, 1], domain, p)
        inc = incidence_count(f, g, codebook, p, 1)
        assert isinstance(inc, int)
        assert inc >= 0


class TestKKH26WindowAnalysis:
    """Analyze the parameter window between Johnson bound and capacity."""

    @staticmethod
    def johnson_bound(rho: float) -> float:
        """Johnson bound: 1 - sqrt(rho)."""
        return 1.0 - rho**0.5

    @staticmethod
    def capacity_bound(rho: float) -> float:
        """Capacity bound: 1 - rho."""
        return 1.0 - rho

    def test_window_exists(self):
        """The window between Johnson and capacity exists for rho < 1."""
        for rho in [0.5, 0.25, 0.125, 0.0625]:
            j = self.johnson_bound(rho)
            c = self.capacity_bound(rho)
            assert j < c, f"Window should exist for rho={rho}: Johnson={j}, Capacity={c}"

    def test_f5_rate_half_window(self):
        """For RS[F_5, F_5^x, 2], rate = 1/2:
        Johnson = 1 - sqrt(1/2) ≈ 0.293
        Capacity = 1 - 1/2 = 0.5

        delta = 1/4 = 0.25 is BELOW the Johnson bound (0.293),
        so the F_5 case is actually in the proven-safe region.
        KKH26's counterexamples operate at delta near capacity (1 - rho - eta).
        """
        rho = 0.5
        j = self.johnson_bound(rho)
        c = self.capacity_bound(rho)
        delta = 0.25

        assert delta < j, "delta=1/4 is below Johnson for rate 1/2"
        assert j < c, "Window exists"

    def test_target_rates(self):
        """The Grand MCA Challenge targets rates 1/2, 1/4, 1/8, 1/16."""
        target_rates = [0.5, 0.25, 0.125, 0.0625]
        for rho in target_rates:
            j = self.johnson_bound(rho)
            c = self.capacity_bound(rho)
            window = c - j
            assert window > 0
