"""End-to-end smoke tests exercising the real CLI entry points as subprocesses."""

import json
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestSearchE2E:
    """Subprocess-based tests for the search CLI."""

    def test_search_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "results.jsonl"
            result = subprocess.run(
                [
                    "breaking-proofs", "search",
                    "--max-alpha", "4",
                    "--max-n", "16",
                    "--output", str(out),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, f"stderr: {result.stderr}"

    def test_search_produces_valid_jsonl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "results.jsonl"
            subprocess.run(
                [
                    "breaking-proofs", "search",
                    "--max-alpha", "4",
                    "--max-n", "16",
                    "--output", str(out),
                ],
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )
            assert out.exists()
            lines = [l for l in out.read_text().splitlines() if l.strip()]
            assert len(lines) > 0

            expected_fields = {"params", "incidence_count", "has_correlated_agreement", "run_id"}
            for line in lines:
                record = json.loads(line)
                if "error" not in record:
                    missing = expected_fields - record.keys()
                    assert not missing, f"Missing fields {missing} in {record}"


class TestReportE2E:
    """Subprocess-based tests for the report CLI."""

    @pytest.fixture()
    def search_log(self, tmp_path):
        out = tmp_path / "search.jsonl"
        subprocess.run(
            [
                "breaking-proofs", "search",
                "--max-alpha", "4",
                "--max-n", "16",
                "--output", str(out),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        return out

    def test_report_exits_zero(self, search_log):
        result = subprocess.run(
            ["breaking-proofs", "report", "--log", str(search_log)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"

    def test_report_contains_expected_sections(self, search_log):
        result = subprocess.run(
            ["breaking-proofs", "report", "--log", str(search_log)],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        report = result.stdout
        assert "# Search Analysis Report" in report
        assert "Parameters Explored" in report
