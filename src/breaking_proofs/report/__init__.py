"""Report package: analysis, formatting, and soundcalc significance checking."""

from breaking_proofs.report.analysis import (
    RateSummary,
    SearchAnalysis,
    SearchHit,
    analyze_search_log,
)
from breaking_proofs.report.formatter import format_report
from breaking_proofs.report.soundcalc_check import (
    Regime,
    SignificanceResult,
    classify_hit,
    classify_regime,
)

__all__ = [
    "SearchAnalysis",
    "SearchHit",
    "RateSummary",
    "analyze_search_log",
    "format_report",
    "Regime",
    "SignificanceResult",
    "classify_hit",
    "classify_regime",
]
