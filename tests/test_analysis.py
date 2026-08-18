"""Tests for JSONL analysis aggregation and interesting-hit flagging."""

import json

from breaking_proofs.report.analysis import (
    analyze_search_log,
    parse_jsonl,
)


def _make_record(
    params_id="p5_n4_k2_a1_K4",
    alpha=1, rho_num=1, rho_den=4, K=4,
    n=4, k=2, p=5, delta_n=2,
    incidence_count=3, has_correlated_agreement=False,
    runtime_ms=1.5, run_id=None, error=None,
):
    rec = {
        "params_id": params_id,
        "params": {
            "alpha": alpha, "rho_num": rho_num, "rho_den": rho_den,
            "K": K, "C": 0.5, "s": 2, "m": 1,
            "n": n, "k": k, "p": p, "delta_n": delta_n, "r": 3,
        },
        "incidence_count": incidence_count,
        "has_correlated_agreement": has_correlated_agreement,
        "distance": delta_n,
        "runtime_ms": runtime_ms,
    }
    if run_id:
        rec["run_id"] = run_id
    if error:
        rec["error"] = error
    return rec


def _write_jsonl(tmp_path, records):
    path = tmp_path / "search-log.jsonl"
    with path.open("w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
    return path


class TestParseJsonl:
    def test_parses_valid_records(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(params_id="a"),
            _make_record(params_id="b"),
        ])
        hits, errors = parse_jsonl(path)
        assert len(hits) == 2
        assert errors == 0

    def test_counts_error_records(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(params_id="a"),
            _make_record(params_id="err", error="boom"),
        ])
        hits, errors = parse_jsonl(path)
        assert len(hits) == 1
        assert errors == 1

    def test_handles_malformed_json(self, tmp_path):
        path = tmp_path / "bad.jsonl"
        path.write_text('{"valid": true}\nnot json\n')
        hits, errors = parse_jsonl(path)
        assert errors >= 1

    def test_filters_by_run_id(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(params_id="a", run_id="abc123"),
            _make_record(params_id="b", run_id="def456"),
        ])
        hits, _ = parse_jsonl(path, run_id="abc123")
        assert len(hits) == 1
        assert hits[0].params_id == "a"

    def test_computes_rho_and_theta(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(rho_num=1, rho_den=4, n=8, delta_n=3),
        ])
        hits, _ = parse_jsonl(path)
        assert hits[0].rho == 0.25
        assert hits[0].theta == 3 / 8

    def test_skips_blank_lines(self, tmp_path):
        path = tmp_path / "sparse.jsonl"
        rec = json.dumps(_make_record())
        path.write_text(f"{rec}\n\n{rec}\n")
        hits, _ = parse_jsonl(path)
        assert len(hits) == 2


class TestAnalyzeSearchLog:
    def test_basic_aggregation(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(params_id="a", rho_num=1, rho_den=4, incidence_count=5),
            _make_record(params_id="b", rho_num=1, rho_den=4, incidence_count=0,
                         has_correlated_agreement=None),
            _make_record(params_id="c", rho_num=1, rho_den=8, incidence_count=2),
        ])
        analysis = analyze_search_log(path)

        assert analysis.total_records == 3
        assert analysis.error_count == 0
        assert len(analysis.rate_summaries) == 2

        quarter = next(rs for rs in analysis.rate_summaries if abs(rs.rho - 0.25) < 1e-6)
        assert quarter.total_evaluations == 2
        assert quarter.hits_with_incidence == 1

    def test_interesting_hits_include_incidence(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(params_id="a", incidence_count=5),
            _make_record(params_id="b", incidence_count=0,
                         has_correlated_agreement=None),
        ])
        analysis = analyze_search_log(path)
        ids = [h.params_id for h in analysis.interesting_hits]
        assert "a" in ids
        assert "b" not in ids

    def test_interesting_hits_include_no_ca(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(params_id="a", incidence_count=0,
                         has_correlated_agreement=False),
        ])
        analysis = analyze_search_log(path)
        ids = [h.params_id for h in analysis.interesting_hits]
        assert "a" in ids

    def test_interesting_hits_sorted_by_theta(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(params_id="shallow", n=8, delta_n=1,
                         incidence_count=1, alpha=1),
            _make_record(params_id="deep", n=8, delta_n=5,
                         incidence_count=1, alpha=2),
        ])
        analysis = analyze_search_log(path)
        assert analysis.interesting_hits[0].params_id == "deep"

    def test_parameters_explored(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(n=4, p=5),
            _make_record(params_id="b", n=16, p=17),
        ])
        analysis = analyze_search_log(path)
        pe = analysis.parameters_explored
        assert pe["n_range"] == [4, 16]
        assert pe["p_range"] == [5, 17]
        assert pe["total_params"] == 2

    def test_run_id_filtering(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(params_id="a", run_id="run1", incidence_count=1),
            _make_record(params_id="b", run_id="run2", incidence_count=1),
        ])
        analysis = analyze_search_log(path, run_id="run1")
        assert analysis.parameters_explored["total_params"] == 1

    def test_error_count_in_total(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(params_id="ok", incidence_count=1),
            _make_record(params_id="err", error="fail"),
        ])
        analysis = analyze_search_log(path)
        assert analysis.total_records == 2
        assert analysis.error_count == 1

    def test_no_duplicate_interesting_hits(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(params_id="a", incidence_count=5,
                         has_correlated_agreement=False),
        ])
        analysis = analyze_search_log(path)
        assert len([h for h in analysis.interesting_hits if h.params_id == "a"]) == 1

    def test_baseline_theta_uses_smallest_alpha(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(params_id="small", alpha=1, n=8, delta_n=2,
                         incidence_count=1),
            _make_record(params_id="big", alpha=3, n=8, delta_n=5,
                         incidence_count=1),
        ])
        analysis = analyze_search_log(path)
        rs = analysis.rate_summaries[0]
        assert rs.baseline_theta == 2 / 8
