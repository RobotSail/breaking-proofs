"""Tests for the search harness, worker, and structured verifier.

Cross-validates the structured verifier against the brute-force oracle
on small instances where both methods are feasible.
"""

import json
import os
import tempfile

from breaking_proofs.oracle.field import build_evaluation_domain
from breaking_proofs.oracle.incidence import incidence_count
from breaking_proofs.oracle.rs_code import enumerate_codebook
from breaking_proofs.oracle.structured_verifier import (
    incidence_count_structured,
    is_delta_close_structured,
    lagrange_eval,
    verify_agreement_set,
)
from breaking_proofs.search.construction import build_kkh26_instance
from breaking_proofs.search.harness import load_completed_ids, run_search
from breaking_proofs.search.params import KKH26Params
from breaking_proofs.search.worker import evaluate_params, params_to_id


class TestWorker:
    """Test the stateless worker function."""

    def test_worker_smallest_instance(self):
        """Worker evaluates the smallest KKH26 instance (p=17, n=16, k=2)."""
        params = KKH26Params.derive(alpha=4, rho_num=1, rho_den=8, K=4, C=0.5)
        assert params is not None

        result = evaluate_params(params)

        assert "error" not in result, f"Worker failed: {result.get('error')}"
        assert result["params_id"] == params_to_id(params)
        assert isinstance(result["incidence_count"], int)
        assert result["incidence_count"] >= 0
        assert isinstance(result["has_correlated_agreement"], bool)
        assert result["runtime_ms"] >= 0
        assert result["distance"] == params.delta_n

    def test_worker_rate_one_quarter(self):
        """Worker evaluates ρ=1/4 instance (p=17, n=16, k=4).

        Codebook size 17^4=83521 exceeds CA_THRESHOLD so correlated
        agreement is skipped (None), but incidence is still computed.
        """
        params = KKH26Params.derive(alpha=4, rho_num=1, rho_den=4, K=4, C=0.5)
        assert params is not None

        result = evaluate_params(params)
        assert "error" not in result
        assert isinstance(result["incidence_count"], int)
        assert result["has_correlated_agreement"] is None

    def test_worker_exception_handling(self):
        """Worker returns error dict on failure instead of raising."""
        params = KKH26Params(
            alpha=1, rho_num=1, rho_den=4, K=4, C=0.5,
            s=2, m=1, n=2, r=3, k=1, p=3, delta_n=-1,
        )
        result = evaluate_params(params)
        assert "runtime_ms" in result

    def test_params_to_id_stable(self):
        """params_to_id produces stable, unique identifiers."""
        params = KKH26Params.derive(alpha=4, rho_num=1, rho_den=8, K=4, C=0.5)
        assert params is not None
        id1 = params_to_id(params)
        id2 = params_to_id(params)
        assert id1 == id2
        assert "p17" in id1
        assert "n16" in id1
        assert "k2" in id1

    def test_worker_counterexample_properties(self):
        """Smallest KKH26 instance should show high incidence without CA."""
        params = KKH26Params.derive(alpha=4, rho_num=1, rho_den=8, K=4, C=0.5)
        assert params is not None
        result = evaluate_params(params)
        assert "error" not in result
        assert result["incidence_count"] > 0
        assert result["has_correlated_agreement"] is False


class TestHarness:
    """Test the search harness with small parameter spaces."""

    def test_harness_small_alpha(self):
        """Harness runs successfully with max_alpha=4."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = os.path.join(tmpdir, "test-log.jsonl")
            results = run_search(
                max_alpha=4,
                workers=1,
                output_path=output,
            )
            assert len(results) > 0
            for r in results:
                assert "params_id" in r
                assert "runtime_ms" in r

            with open(output) as f:
                lines = [line.strip() for line in f if line.strip()]
            assert len(lines) == len(results)
            for line in lines:
                record = json.loads(line)
                assert "params_id" in record

    def test_harness_resume_capability(self):
        """Harness skips already-completed parameter IDs on resume."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = os.path.join(tmpdir, "test-log.jsonl")

            results1 = run_search(max_alpha=4, workers=1, output_path=output)
            count1 = len(results1)
            assert count1 > 0

            results2 = run_search(max_alpha=4, workers=1, output_path=output)
            assert len(results2) == 0

            with open(output) as f:
                lines = [line.strip() for line in f if line.strip()]
            assert len(lines) == count1

    def test_harness_single_rate(self):
        """Harness filters to a single rate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = os.path.join(tmpdir, "test-log.jsonl")
            results = run_search(
                max_alpha=4,
                rates=[(1, 8)],
                workers=1,
                output_path=output,
            )
            for r in results:
                if "error" not in r:
                    params = r.get("params", {})
                    assert params.get("rho_num") == 1
                    assert params.get("rho_den") == 8

    def test_harness_max_n_filters_candidates(self):
        """max_n filters candidates before dispatch, reducing evaluation count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_all = os.path.join(tmpdir, "all.jsonl")
            out_bounded = os.path.join(tmpdir, "bounded.jsonl")

            results_all = run_search(
                max_alpha=4, workers=1, output_path=out_all,
            )
            results_bounded = run_search(
                max_alpha=4, max_n=8, workers=1, output_path=out_bounded,
            )

            assert len(results_all) > len(results_bounded)
            for r in results_bounded:
                if "error" not in r:
                    assert r["params"]["n"] <= 8

    def test_harness_max_n_excludes_large(self):
        """Candidates exceeding max_n are not evaluated at all."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = os.path.join(tmpdir, "bounded.jsonl")
            results = run_search(
                max_alpha=4, max_n=4, workers=1, output_path=output,
            )
            for r in results:
                if "error" not in r:
                    assert r["params"]["n"] <= 4

    def test_harness_max_n_all_filtered_returns_empty(self):
        """If max_n filters out everything, returns empty list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output = os.path.join(tmpdir, "empty.jsonl")
            results = run_search(
                max_alpha=4, max_n=1, workers=1, output_path=output,
            )
            assert results == []


class TestJSONLResume:
    """Test JSONL resume scanning."""

    def test_load_completed_empty(self):
        """Loading from nonexistent file returns empty set."""
        ids = load_completed_ids("/nonexistent/path/file.jsonl")
        assert ids == set()

    def test_load_completed_with_data(self):
        """Completed IDs are loaded correctly from JSONL."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps({"params_id": "p17_n16_k2_a4_K4", "incidence_count": 5}) + "\n")
            f.write(json.dumps({"params_id": "p17_n16_k4_a4_K4", "incidence_count": 3}) + "\n")
            f.write(json.dumps({"params_id": "p17_n16_k1_a4_K4", "error": "test"}) + "\n")
            path = f.name

        try:
            ids = load_completed_ids(path)
            assert "p17_n16_k2_a4_K4" in ids
            assert "p17_n16_k4_a4_K4" in ids
            assert "p17_n16_k1_a4_K4" not in ids
        finally:
            os.unlink(path)

    def test_load_completed_malformed_lines(self):
        """Malformed JSONL lines are skipped gracefully."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write("not json\n")
            f.write(json.dumps({"params_id": "valid_id", "incidence_count": 1}) + "\n")
            f.write("\n")
            path = f.name

        try:
            ids = load_completed_ids(path)
            assert "valid_id" in ids
            assert len(ids) == 1
        finally:
            os.unlink(path)


class TestStructuredVerifier:
    """Cross-validate structured verifier against brute-force oracle."""

    def test_lagrange_eval_line(self):
        """Lagrange interpolation recovers a line through two points in F_17."""
        p = 17
        xs = [2, 5]
        ys = [7, 3]
        for x, y in zip(xs, ys, strict=True):
            assert lagrange_eval(xs, ys, x, p) == y

    def test_lagrange_eval_quadratic(self):
        """Lagrange interpolation recovers a quadratic through three points in F_17."""
        p = 17
        xs = [1, 3, 7]
        ys = [(2 * x**2 + 3 * x + 5) % p for x in xs]
        for x, y in zip(xs, ys, strict=True):
            assert lagrange_eval(xs, ys, x, p) == y
        extra = lagrange_eval(xs, ys, 10, p)
        assert extra == (2 * 100 + 30 + 5) % p

    def test_structured_incidence_matches_brute_force(self):
        """Structured verifier gives same incidence count as brute-force on p=17, n=16, k=2."""
        params = KKH26Params.derive(alpha=4, rho_num=1, rho_den=8, K=4, C=0.5)
        assert params is not None
        instance = build_kkh26_instance(params)

        codebook = enumerate_codebook(params.p, params.k, instance.domain)
        bf_inc = incidence_count(instance.f, instance.g, codebook, params.p, params.delta_n)

        st_inc = incidence_count_structured(
            instance.f, instance.g, instance.domain,
            params.p, params.k, params.delta_n,
        )

        assert bf_inc == st_inc, (
            f"Brute-force incidence={bf_inc} != structured incidence={st_inc}"
        )

    def test_structured_incidence_rate_one_quarter(self):
        """Cross-validate at ρ=1/4 (p=17, n=16, k=4, delta_n=10)."""
        params = KKH26Params.derive(alpha=4, rho_num=1, rho_den=4, K=4, C=0.5)
        assert params is not None
        instance = build_kkh26_instance(params)

        codebook = enumerate_codebook(params.p, params.k, instance.domain)
        bf_inc = incidence_count(instance.f, instance.g, codebook, params.p, params.delta_n)

        st_inc = incidence_count_structured(
            instance.f, instance.g, instance.domain,
            params.p, params.k, params.delta_n,
        )

        assert bf_inc == st_inc

    def test_is_delta_close_known_codeword(self):
        """A codeword is distance 0 from the code (trivially close)."""
        p, n, k = 17, 16, 2
        domain = build_evaluation_domain(p, n)
        codebook = enumerate_codebook(p, k, domain)
        codeword = codebook[1]

        is_close, agreement = is_delta_close_structured(codeword, domain, p, k, delta_n=0)
        assert is_close
        assert agreement == n

    def test_is_delta_close_distant_word(self):
        """A non-codeword has agreement < n at delta_n=0."""
        p, n, k = 17, 16, 2
        domain = build_evaluation_domain(p, n)
        # Constant-7 codeword with one position perturbed — not a codeword
        word = [7] * n
        word[0] = 0

        is_close, agreement = is_delta_close_structured(word, domain, p, k, delta_n=0)
        assert not is_close
        assert agreement < n

    def test_verify_agreement_set_correct(self):
        """verify_agreement_set confirms a valid codeword's full agreement."""
        p, n, k = 17, 16, 2
        domain = build_evaluation_domain(p, n)
        codebook = enumerate_codebook(p, k, domain)
        codeword = codebook[5]

        agreement_indices = list(range(n))
        is_valid, count = verify_agreement_set(codeword, domain, agreement_indices, p, k)
        assert is_valid
        assert count == n

    def test_structured_rate_one_sixteenth(self):
        """Cross-validate at ρ=1/16 (p=17, n=16, k=1)."""
        params = KKH26Params.derive(alpha=4, rho_num=1, rho_den=16, K=4, C=0.5)
        assert params is not None
        instance = build_kkh26_instance(params)

        codebook = enumerate_codebook(params.p, params.k, instance.domain)
        bf_inc = incidence_count(instance.f, instance.g, codebook, params.p, params.delta_n)

        st_inc = incidence_count_structured(
            instance.f, instance.g, instance.domain,
            params.p, params.k, params.delta_n,
        )

        assert bf_inc == st_inc
