"""Property-based tests: galois oracle == reference oracle on all outputs."""

from hypothesis import given, settings
from hypothesis import strategies as st

from breaking_proofs.oracle.distance import min_hamming_distance
from breaking_proofs.oracle.field import build_evaluation_domain
from breaking_proofs.oracle.incidence import incidence_count
from breaking_proofs.oracle.reference import (
    ref_build_domain,
    ref_enumerate_codebook,
    ref_incidence_count,
    ref_min_distance,
)
from breaking_proofs.oracle.rs_code import enumerate_codebook

SMALL_PRIMES_WITH_ROOTS = [
    (5, 4),   # F_5, domain = F_5^x, n=4
    (7, 2),   # F_7, n=2
    (7, 3),   # F_7, n=3
    (7, 6),   # F_7, n=6
    (11, 2),  # F_11, n=2
    (11, 5),  # F_11, n=5
    (13, 4),  # F_13, n=4
]


@st.composite
def field_and_code(draw):
    """Generate a valid (p, n, k) triple with random words f, g."""
    p, n = draw(st.sampled_from(SMALL_PRIMES_WITH_ROOTS))
    k = draw(st.integers(min_value=1, max_value=n))
    f = [draw(st.integers(min_value=0, max_value=p - 1)) for _ in range(n)]
    g = [draw(st.integers(min_value=0, max_value=p - 1)) for _ in range(n)]
    return p, n, k, f, g


class TestDomainParity:
    @given(data=st.data())
    @settings(max_examples=20, deadline=30000)
    def test_domains_match(self, data):
        p, n = data.draw(st.sampled_from(SMALL_PRIMES_WITH_ROOTS))
        galois_domain = build_evaluation_domain(p, n)
        ref_domain = ref_build_domain(p, n)
        assert set(galois_domain) == set(ref_domain)
        assert len(galois_domain) == len(ref_domain) == n


class TestCodebookParity:
    @given(data=st.data())
    @settings(max_examples=10, deadline=60000)
    def test_codebooks_match(self, data):
        p, n = data.draw(st.sampled_from([(5, 4), (7, 2), (7, 3)]))
        k = data.draw(st.integers(min_value=1, max_value=min(n, 3)))
        galois_domain = build_evaluation_domain(p, n)
        ref_domain = ref_build_domain(p, n)

        galois_cb = enumerate_codebook(p, k, galois_domain)
        ref_cb = ref_enumerate_codebook(p, k, ref_domain)

        galois_set = {tuple(cw) for cw in galois_cb}
        ref_set = {tuple(cw) for cw in ref_cb}
        assert galois_set == ref_set


class TestDistanceParity:
    @given(params=field_and_code())
    @settings(max_examples=15, deadline=60000)
    def test_min_distance_matches(self, params):
        p, n, k, f, _ = params
        if p**k > 5000:
            return  # skip large codebooks

        galois_domain = build_evaluation_domain(p, n)
        ref_domain = ref_build_domain(p, n)

        galois_cb = enumerate_codebook(p, k, galois_domain)
        ref_cb = ref_enumerate_codebook(p, k, ref_domain)

        d_galois = min_hamming_distance(f, galois_cb, p)
        d_ref = ref_min_distance(f, ref_cb, p)
        assert d_galois == d_ref


class TestIncidenceParity:
    @given(params=field_and_code())
    @settings(max_examples=10, deadline=120000)
    def test_incidence_count_matches(self, params):
        p, n, k, f, g = params
        if p**k > 1000 or p > 11:
            return  # skip expensive cases

        delta_n = n // 2

        galois_domain = build_evaluation_domain(p, n)
        ref_domain = ref_build_domain(p, n)

        galois_cb = enumerate_codebook(p, k, galois_domain)
        ref_cb = ref_enumerate_codebook(p, k, ref_domain)

        inc_galois = incidence_count(f, g, galois_cb, p, delta_n)
        inc_ref = ref_incidence_count(f, g, ref_cb, p, delta_n)
        assert inc_galois == inc_ref
