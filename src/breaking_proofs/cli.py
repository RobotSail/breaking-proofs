"""CLI entry point for breaking-proofs."""

import json

import click

from breaking_proofs.logging import get_logger

logger = get_logger(__name__)


@click.group()
def main():
    """Breaking-proofs: exact-arithmetic RS proximity oracle."""


@main.command()
@click.option("--prime", "-p", type=int, required=True, help="Prime field size")
@click.option("--n", type=int, required=True, help="Evaluation domain size (subgroup order)")
@click.option("--k", type=int, required=True, help="Code dimension (degree < k)")
@click.option("--f", "f_str", type=str, required=True, help="Comma-separated word f")
@click.option("--g", "g_str", type=str, required=True, help="Comma-separated word g")
@click.option("--delta-n", type=int, required=True, help="Absolute distance threshold")
def check(prime: int, n: int, k: int, f_str: str, g_str: str, delta_n: int):
    """Run the proximity oracle on a single (f, g) pair."""
    from breaking_proofs.oracle.agreement import has_correlated_agreement
    from breaking_proofs.oracle.field import build_evaluation_domain
    from breaking_proofs.oracle.incidence import incidence_count
    from breaking_proofs.oracle.rs_code import enumerate_codebook

    f = [int(x) for x in f_str.split(",")]
    g = [int(x) for x in g_str.split(",")]

    domain = build_evaluation_domain(prime, n)
    codebook = enumerate_codebook(prime, k, domain)
    inc = incidence_count(f, g, codebook, prime, delta_n)
    ca = has_correlated_agreement(f, g, codebook, prime, delta_n)

    result = {
        "prime": prime,
        "n": n,
        "k": k,
        "delta_n": delta_n,
        "incidence_count": inc,
        "correlated_agreement": ca,
    }
    click.echo(json.dumps(result, indent=2))


@main.command()
@click.option("--rate", type=float, default=None, help="Target rate rho (e.g. 0.125 for 1/8)")
@click.option("--max-n", type=int, default=64, help="Maximum code length n")
@click.option("--max-alpha", type=int, default=8, help="Maximum subgroup exponent alpha")
@click.option("--workers", type=int, default=None, help="Pool size (default: cpu_count)")
@click.option("--output", type=str, default="results/search-log.jsonl", help="JSONL output path")
@click.option("--C", "c_val", type=float, default=0.5, help="Free constant C")
def search(
    rate: float | None, max_n: int, max_alpha: int,
    workers: int | None, output: str, c_val: float,
):
    """Run the parallel search harness over the KKH26 parameter space."""
    from breaking_proofs.search.harness import run_search

    rates = None
    if rate is not None:
        if rate >= 0.5 or rate <= 0:
            raise click.BadParameter("Rate must be in (0, 0.5)", param_hint="--rate")
        den = round(1 / rate)
        rates = [(1, den)]

    results = run_search(
        max_alpha=max_alpha,
        rates=rates,
        workers=workers,
        output_path=output,
        C=c_val,
    )

    filtered = [r for r in results if r.get("params", {}).get("n", 0) <= max_n]

    click.echo(f"\nCompleted {len(results)} evaluations ({len(filtered)} with n <= {max_n})")
    for r in filtered:
        if "error" in r:
            click.echo(f"  {r['params_id']}: ERROR - {r['error']}")
        else:
            click.echo(
                f"  {r['params_id']}: incidence={r['incidence_count']}, "
                f"CA={r['has_correlated_agreement']}, "
                f"runtime={r['runtime_ms']}ms"
            )


@main.command(name="reproduce-kkh26")
@click.option("--alpha", type=int, required=True, help="Subgroup exponent alpha")
@click.option("--rho-num", type=int, default=1, help="Rate numerator")
@click.option("--rho-den", type=int, required=True, help="Rate denominator (power of 2)")
@click.option("--K", "k_val", type=int, default=4, help="Paper parameter K (power of 2)")
@click.option("--C", "c_val", type=float, default=0.5, help="Free constant C")
def reproduce_kkh26(alpha: int, rho_num: int, rho_den: int, k_val: int, c_val: float):
    """Verify a single KKH26 construction instance against the oracle."""
    from breaking_proofs.search.params import KKH26Params
    from breaking_proofs.search.worker import evaluate_params

    params = KKH26Params.derive(alpha, rho_num, rho_den, k_val, c_val)
    if params is None:
        raise click.ClickException(
            f"Invalid parameters: alpha={alpha}, rho={rho_num}/{rho_den}, K={k_val}, C={c_val}"
        )

    click.echo(f"KKH26 instance: p={params.p}, n={params.n}, k={params.k}, "
               f"r={params.r}, delta_n={params.delta_n}")
    click.echo(f"Rate rho = {params.rho}, distance delta = {params.delta_n}/{params.n} "
               f"= {params.delta_n/params.n:.4f}")

    result = evaluate_params(params)

    if "error" in result:
        raise click.ClickException(f"Evaluation failed: {result['error']}")

    click.echo(json.dumps(result, indent=2))

    if result["has_correlated_agreement"] is False and result["incidence_count"] > 0:
        click.echo("\nCOUNTEREXAMPLE CONFIRMED: high incidence without correlated agreement")
    elif result["has_correlated_agreement"] is True:
        click.echo("\nCorrelated agreement detected (not a counterexample at these parameters)")
    elif result["has_correlated_agreement"] is None:
        click.echo(f"\nIncidence count: {result['incidence_count']} "
                   "(correlated agreement check skipped - instance too large for brute force)")


if __name__ == "__main__":
    main()
