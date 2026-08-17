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


if __name__ == "__main__":
    main()
