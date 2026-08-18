"""Generate Markdown reports from SearchAnalysis."""

import math

from breaking_proofs.report.analysis import SearchAnalysis
from breaking_proofs.report.soundcalc_check import classify_hit


def format_report(analysis: SearchAnalysis) -> str:
    """Format SearchAnalysis as a Markdown report."""
    lines: list[str] = []

    lines.append("# Search Analysis Report\n")

    # --- Parameters explored ---
    lines.append("## Parameters Explored\n")
    pe = analysis.parameters_explored
    lines.append(f"- **Total parameters evaluated:** {pe.get('total_params', 0)}")
    rates = pe.get("rates", [])
    if rates:
        lines.append(f"- **Rates (ρ):** {', '.join(f'{r:.4f}' for r in rates)}")
    n_range = pe.get("n_range", [])
    if n_range:
        lines.append(f"- **Code length range (n):** {n_range[0]}–{n_range[1]}")
    p_range = pe.get("p_range", [])
    if p_range:
        lines.append(f"- **Field size range (p):** {p_range[0]}–{p_range[1]}")
    lines.append(f"- **Errors:** {analysis.error_count}\n")

    # --- Per-rate table ---
    lines.append("## Hit Rate by Regime\n")
    lines.append(
        "| Rate (ρ) | Evaluations | With Incidence | No CA "
        "| Best θ | Baseline θ | UDR Bound | JBR Bound |"
    )
    lines.append("|---------|-------------|----------------|-------|"
                 "--------|------------|-----------|-----------|")
    for rs in analysis.rate_summaries:
        udr = (1 - rs.rho) / 2
        jbr = 1 - math.sqrt(rs.rho)
        best = f"{rs.best_theta:.4f}" if rs.best_theta is not None else "—"
        base = f"{rs.baseline_theta:.4f}" if rs.baseline_theta is not None else "—"
        lines.append(
            f"| {rs.rho:.4f} | {rs.total_evaluations} | {rs.hits_with_incidence} "
            f"| {rs.hits_no_correlated_agreement} | {best} | {base} "
            f"| {udr:.4f} | {jbr:.4f} |"
        )
    lines.append("")

    # --- Best counterexample ---
    lines.append("## Best Counterexample Found\n")
    best_overall = None
    for rs in analysis.rate_summaries:
        if rs.best_hit is not None and (
            best_overall is None or rs.best_hit.theta > best_overall.theta
        ):
            best_overall = rs.best_hit

    if best_overall:
        sig = classify_hit(best_overall.theta, best_overall.rho)
        lines.append(f"- **Params ID:** `{best_overall.params_id}`")
        lines.append(f"- **Rate (ρ):** {best_overall.rho:.4f}")
        lines.append(f"- **Proximity (θ):** {best_overall.theta:.4f}")
        lines.append(f"- **Incidence count:** {best_overall.incidence_count}")
        lines.append(f"- **Correlated agreement:** {best_overall.has_correlated_agreement}")
        lines.append(f"- **Regime:** {sig.regime.value.upper()}")
        flag = "YES" if sig.is_significant else "no"
        lines.append(f"- **Soundcalc significant:** {flag}")
    else:
        lines.append("No hits with incidence found.")
    lines.append("")

    # --- KKH26 comparison ---
    lines.append("## KKH26 Baseline Comparison\n")
    any_comparison = False
    for rs in analysis.rate_summaries:
        if rs.baseline_theta is not None and rs.best_theta is not None:
            delta = rs.best_theta - rs.baseline_theta
            sign = "+" if delta > 0 else ""
            lines.append(
                f"- **ρ = {rs.rho:.4f}:** baseline θ = {rs.baseline_theta:.4f}, "
                f"best θ = {rs.best_theta:.4f} ({sign}{delta:.4f})"
            )
            any_comparison = True
    if not any_comparison:
        lines.append("No baseline comparisons available.")
    lines.append("")

    # --- Interesting hits table ---
    if analysis.interesting_hits:
        lines.append("## Interesting Hits\n")
        lines.append("| Params ID | ρ | θ | Incidence | CA | Regime |")
        lines.append("|-----------|------|------|-----------|------|--------|")
        for hit in analysis.interesting_hits[:20]:
            sig = classify_hit(hit.theta, hit.rho)
            ca_val = hit.has_correlated_agreement
            ca = str(ca_val) if ca_val is not None else "—"
            lines.append(
                f"| `{hit.params_id}` | {hit.rho:.4f} | {hit.theta:.4f} "
                f"| {hit.incidence_count} | {ca} | {sig.regime.value.upper()} |"
            )
        lines.append("")

    # --- Soundcalc significance summary ---
    lines.append("## Soundcalc Significance\n")
    sig_hits = [
        h for h in analysis.interesting_hits
        if classify_hit(h.theta, h.rho).is_significant
    ]
    if sig_hits:
        lines.append(
            f"**{len(sig_hits)} hit(s) fall in the proximity gap "
            f"(JBR regime) or beyond.**"
        )
        lines.append("These results may tighten soundcalc's reported bounds.")
    else:
        lines.append(
            "No hits fall in the proximity gap. "
            "All results are within the unique decoding radius."
        )
    lines.append("")

    return "\n".join(lines)
