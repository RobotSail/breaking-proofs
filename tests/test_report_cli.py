"""Tests for the report and significance CLI subcommands."""

import json

from click.testing import CliRunner

from breaking_proofs.cli import main


def _make_record(
    params_id="p5_n4_k2_a1_K4",
    alpha=1, rho_num=1, rho_den=4,
    n=4, k=2, p=5, delta_n=2,
    incidence_count=3, has_correlated_agreement=False,
    run_id=None,
):
    rec = {
        "params_id": params_id,
        "params": {
            "alpha": alpha, "rho_num": rho_num, "rho_den": rho_den,
            "K": 4, "C": 0.5, "s": 2, "m": 1,
            "n": n, "k": k, "p": p, "delta_n": delta_n, "r": 3,
        },
        "incidence_count": incidence_count,
        "has_correlated_agreement": has_correlated_agreement,
        "distance": delta_n,
        "runtime_ms": 1.0,
    }
    if run_id:
        rec["run_id"] = run_id
    return rec


def _write_jsonl(tmp_path, records):
    path = tmp_path / "search-log.jsonl"
    with path.open("w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
    return path


class TestReportCommand:
    def test_report_prints_markdown(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(incidence_count=5),
            _make_record(params_id="b", incidence_count=0,
                         has_correlated_agreement=None),
        ])
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--log", str(path)])
        assert result.exit_code == 0
        assert "# Search Analysis Report" in result.output
        assert "Parameters Explored" in result.output
        assert "Hit Rate by Regime" in result.output

    def test_report_with_run_id(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(params_id="a", run_id="abc", incidence_count=1),
            _make_record(params_id="b", run_id="def", incidence_count=1),
        ])
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--log", str(path), "--run-id", "abc"])
        assert result.exit_code == 0
        assert "1" in result.output

    def test_report_writes_to_file(self, tmp_path):
        log = _write_jsonl(tmp_path, [_make_record()])
        out = tmp_path / "report.md"
        runner = CliRunner()
        result = runner.invoke(main, [
            "report", "--log", str(log), "--output", str(out),
        ])
        assert result.exit_code == 0
        assert out.exists()
        content = out.read_text()
        assert "# Search Analysis Report" in content

    def test_report_shows_soundcalc_significance(self, tmp_path):
        path = _write_jsonl(tmp_path, [
            _make_record(rho_num=1, rho_den=4, n=8, delta_n=4,
                         incidence_count=5),
        ])
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--log", str(path)])
        assert result.exit_code == 0
        assert "Soundcalc Significance" in result.output

    def test_report_empty_log(self, tmp_path):
        path = tmp_path / "empty.jsonl"
        path.write_text("")
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--log", str(path)])
        assert result.exit_code == 0
        assert "No hits with incidence found" in result.output


class TestSignificanceCommand:
    def test_significance_with_params(self):
        hit = {
            "params": {
                "rho_num": 1, "rho_den": 4,
                "delta_n": 4, "n": 10,
            }
        }
        runner = CliRunner()
        result = runner.invoke(main, [
            "significance", "--hit", json.dumps(hit),
        ])
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["regime"] == "jbr"
        assert output["is_significant"] is True

    def test_significance_with_direct_rho_theta(self):
        hit = {"rho": 0.25, "theta": 0.2}
        runner = CliRunner()
        result = runner.invoke(main, [
            "significance", "--hit", json.dumps(hit),
        ])
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["regime"] == "udr"
        assert output["is_significant"] is False

    def test_significance_udr_regime(self):
        hit = {"rho": 0.25, "theta": 0.3}
        runner = CliRunner()
        result = runner.invoke(main, [
            "significance", "--hit", json.dumps(hit),
        ])
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["regime"] == "udr"

    def test_significance_beyond_regime(self):
        hit = {"rho": 0.25, "theta": 0.6}
        runner = CliRunner()
        result = runner.invoke(main, [
            "significance", "--hit", json.dumps(hit),
        ])
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["regime"] == "beyond"
        assert output["is_significant"] is True

    def test_significance_invalid_input(self):
        hit = {"foo": "bar"}
        runner = CliRunner()
        result = runner.invoke(main, [
            "significance", "--hit", json.dumps(hit),
        ])
        assert result.exit_code != 0
