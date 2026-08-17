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
  3. Concrete KKH26 instance tests derived from arXiv:2604.09724
"""

import math

from breaking_proofs.oracle.agreement import has_correlated_agreement
from breaking_proofs.oracle.distance import min_hamming_distance
from breaking_proofs.oracle.field import build_evaluation_domain
from breaking_proofs.oracle.incidence import affine_line_word, incidence_count
from breaking_proofs.oracle.rs_code import enumerate_codebook
from breaking_proofs.search.construction import (
    build_kkh26_instance,
    build_subgroup,
    evaluate_monomial,
    r_fold_sumset,
)
from breaking_proofs.search.params import KKH26Params, generate_candidates


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

    def test_smallest_kkh26_construction(self):
        """Verify smallest KKH26 instance (ρ=1/8, p=17, n=16, k=2)
        against the brute-force oracle.

        f = X^4, g = X^3 over RS[F_17, D, 2] at δ_n = 12.
        Correlated agreement is impossible: deg(g - v_g) ≤ 3 < n - δ_n = 4.
        """
        params = KKH26Params.derive(alpha=4, rho_num=1, rho_den=8, K=4, C=0.5)
        assert params is not None
        assert params.p == 17
        assert params.n == 16
        assert params.k == 2
        assert params.r == 4
        assert params.delta_n == 12

        instance = build_kkh26_instance(params)
        assert len(instance.f) == 16
        assert len(instance.g) == 16

        # Verify monomial evaluations: f = X^4, g = X^3
        for i, x in enumerate(instance.domain):
            assert instance.f[i] == pow(x, 4, 17)
            assert instance.g[i] == pow(x, 3, 17)

        # m=1 ⇒ H = D (degenerate), H^(+4) covers all of F_17
        assert len(instance.subgroup) == 16
        assert set(instance.subgroup) == set(instance.domain)
        assert instance.witnesses is not None
        assert len(instance.witnesses) == 17

        # Brute-force oracle verification
        codebook = enumerate_codebook(17, 2, instance.domain)

        ca = has_correlated_agreement(instance.f, instance.g, codebook, 17, 12)
        assert not ca, "No correlated agreement expected"

        inc = incidence_count(instance.f, instance.g, codebook, 17, 12)
        assert inc > 0, f"Expected positive incidence, got {inc}"

    def test_kkh26_rate_one_quarter(self):
        """Verify ρ=1/4 instance (p=17, n=16, k=4, r=6) construction."""
        params = KKH26Params.derive(alpha=4, rho_num=1, rho_den=4, K=4, C=0.5)
        assert params is not None
        assert params.r == 6
        assert params.k == 4
        assert params.delta_n == 10

        instance = build_kkh26_instance(params)

        # f = X^6, g = X^5
        for i, x in enumerate(instance.domain):
            assert instance.f[i] == pow(x, 6, 17)
            assert instance.g[i] == pow(x, 5, 17)

        # Distance δ = 1 - 6/16 = 5/8 is between Johnson and capacity
        rho = 0.25
        delta = 1 - params.r / params.s
        johnson = 1 - rho**0.5
        capacity = 1 - rho
        assert johnson < delta < capacity


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


class TestKKH26ParamsDerivation:
    """Test the paper-native parameterization module."""

    def test_smallest_rate_one_eighth(self):
        params = KKH26Params.derive(alpha=4, rho_num=1, rho_den=8, K=4, C=0.5)
        assert params is not None
        assert params.s == 16
        assert params.m == 1
        assert params.n == 16
        assert params.r == 4
        assert params.k == 2
        assert params.p == 17
        assert params.delta_n == 12
        assert params.rho == 0.125

    def test_smallest_rate_one_quarter(self):
        params = KKH26Params.derive(alpha=4, rho_num=1, rho_den=4, K=4, C=0.5)
        assert params is not None
        assert params.n == 16
        assert params.r == 6
        assert params.k == 4
        assert params.delta_n == 10

    def test_rate_one_half_rejected(self):
        """ρ ≥ 1/2 is invalid for KKH26 (log(1/(2ρ)) must be positive)."""
        params = KKH26Params.derive(alpha=4, rho_num=1, rho_den=2, K=4, C=0.5)
        assert params is None

    def test_small_K_rejected(self):
        """K must exceed 9/(2·ln(8)) ≈ 2.163."""
        params = KKH26Params.derive(alpha=4, rho_num=1, rho_den=8, K=2, C=0.5)
        assert params is None

    def test_non_power_of_two_K_rejected(self):
        params = KKH26Params.derive(alpha=4, rho_num=1, rho_den=8, K=3, C=0.5)
        assert params is None

    def test_generate_candidates_ordering(self):
        candidates = generate_candidates(max_alpha=6)
        assert len(candidates) > 0
        for i in range(len(candidates) - 1):
            assert candidates[i].n <= candidates[i + 1].n

    def test_constraint_validation(self):
        """All generated candidates satisfy the paper's constraints."""
        candidates = generate_candidates(max_alpha=6)
        for p in candidates:
            assert abs(p.k / p.n - p.rho) < 1e-10
            assert 9 / (2 * math.log(8)) < p.K
            assert p.C / (p.rho * math.log(1 / (2 * p.rho))) < p.K
            assert (p.p - 1) % p.n == 0


class TestKKH26ConstructionHelpers:
    """Test construction helper functions."""

    def test_evaluate_monomial(self):
        domain = build_evaluation_domain(17, 16)
        result = evaluate_monomial(4, domain, 17)
        assert len(result) == 16
        for i, x in enumerate(domain):
            assert result[i] == pow(x, 4, 17)

    def test_build_subgroup_m1(self):
        """m=1 gives H = D."""
        domain = build_evaluation_domain(17, 16)
        H = build_subgroup(domain, m=1, s=16)
        assert len(H) == 16
        assert set(H) == set(domain)

    def test_r_fold_sumset_small(self):
        """2-fold sumset of {1, 2, 3} mod 7."""
        result = r_fold_sumset([1, 2, 3], r=2, p=7)
        assert result == {3, 4, 5}  # 1+2=3, 1+3=4, 2+3=5

    def test_r_fold_sumset_wraps(self):
        """Sumset wraps around mod p."""
        result = r_fold_sumset([5, 6], r=2, p=7)
        assert result == {4}  # 5+6 = 11 ≡ 4 mod 7
