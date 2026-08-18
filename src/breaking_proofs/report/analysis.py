"""Read JSONL search logs, aggregate by rate/regime, flag interesting hits."""

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SearchHit:
    params_id: str
    rho: float
    theta: float
    n: int
    k: int
    p: int
    delta_n: int
    incidence_count: int
    has_correlated_agreement: bool | None
    runtime_ms: float
    run_id: str | None = None
    alpha: int = 0
    K_param: int = 0


@dataclass
class RateSummary:
    rho: float
    total_evaluations: int
    hits_with_incidence: int
    hits_no_correlated_agreement: int
    best_theta: float | None
    best_hit: SearchHit | None
    baseline_theta: float | None


@dataclass
class SearchAnalysis:
    total_records: int
    error_count: int
    rate_summaries: list[RateSummary]
    interesting_hits: list[SearchHit]
    parameters_explored: dict = field(default_factory=dict)


def parse_jsonl(path: Path, run_id: str | None = None) -> tuple[list[SearchHit], int]:
    """Parse JSONL file into SearchHit list. Returns (hits, error_count)."""
    hits: list[SearchHit] = []
    errors = 0

    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                errors += 1
                continue

            if "error" in record:
                errors += 1
                continue

            if run_id and record.get("run_id") != run_id:
                continue

            params = record.get("params", {})
            rho_num = params.get("rho_num", 1)
            rho_den = params.get("rho_den", 1)
            n = params.get("n", 1)
            delta_n = params.get("delta_n", 0)

            rho = rho_num / rho_den if rho_den else 0.0
            theta = delta_n / n if n else 0.0

            hits.append(SearchHit(
                params_id=record.get("params_id", ""),
                rho=rho,
                theta=theta,
                n=n,
                k=params.get("k", 0),
                p=params.get("p", 0),
                delta_n=delta_n,
                incidence_count=record.get("incidence_count", 0),
                has_correlated_agreement=record.get("has_correlated_agreement"),
                runtime_ms=record.get("runtime_ms", 0.0),
                run_id=record.get("run_id"),
                alpha=params.get("alpha", 0),
                K_param=params.get("K", 0),
            ))

    return hits, errors


def _baseline_theta(hits: list[SearchHit], rho: float) -> float | None:
    """KKH26 baseline theta at a given rate: theta from smallest alpha."""
    rate_hits = [h for h in hits if abs(h.rho - rho) < 1e-9]
    if not rate_hits:
        return None
    return min(rate_hits, key=lambda h: (h.alpha, h.n)).theta


def _is_interesting(hit: SearchHit, baseline: float | None) -> bool:
    """Flag a hit as interesting per the three criteria."""
    if hit.incidence_count > 0:
        return True
    if hit.has_correlated_agreement is False:
        return True
    return baseline is not None and hit.theta > baseline


def analyze_search_log(path: Path, run_id: str | None = None) -> SearchAnalysis:
    """Read JSONL search log and produce aggregated analysis."""
    hits, error_count = parse_jsonl(path, run_id)

    rates: dict[float, list[SearchHit]] = {}
    for hit in hits:
        rho_key = round(hit.rho, 6)
        rates.setdefault(rho_key, []).append(hit)

    rate_summaries: list[RateSummary] = []
    interesting: list[SearchHit] = []
    seen_interesting: set[str] = set()

    for rho in sorted(rates):
        rate_hits = rates[rho]
        baseline = _baseline_theta(hits, rho)

        with_incidence = [h for h in rate_hits if h.incidence_count > 0]
        no_ca = [h for h in rate_hits if h.has_correlated_agreement is False]

        best_hit = max(with_incidence, key=lambda h: h.theta) if with_incidence else None
        best_theta = best_hit.theta if best_hit else None

        rate_summaries.append(RateSummary(
            rho=rho,
            total_evaluations=len(rate_hits),
            hits_with_incidence=len(with_incidence),
            hits_no_correlated_agreement=len(no_ca),
            best_theta=best_theta,
            best_hit=best_hit,
            baseline_theta=baseline,
        ))

        for hit in rate_hits:
            if _is_interesting(hit, baseline) and hit.params_id not in seen_interesting:
                interesting.append(hit)
                seen_interesting.add(hit.params_id)

    interesting.sort(key=lambda h: h.theta, reverse=True)

    all_n = [h.n for h in hits]
    all_p = [h.p for h in hits]

    parameters_explored = {
        "rates": sorted(rates.keys()),
        "n_range": [min(all_n), max(all_n)] if all_n else [],
        "p_range": [min(all_p), max(all_p)] if all_p else [],
        "total_params": len(hits),
    }

    return SearchAnalysis(
        total_records=len(hits) + error_count,
        error_count=error_count,
        rate_summaries=rate_summaries,
        interesting_hits=interesting,
        parameters_explored=parameters_explored,
    )
