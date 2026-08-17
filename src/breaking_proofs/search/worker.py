"""Stateless search worker for ProcessPoolExecutor.

Top-level function for picklability. Takes a KKH26Params tuple,
builds the instance via construction.py, verifies against the oracle,
and returns a result dict.
"""

import time
from dataclasses import asdict

from breaking_proofs.logging import get_logger
from breaking_proofs.oracle.agreement import has_correlated_agreement
from breaking_proofs.oracle.incidence import incidence_count
from breaking_proofs.oracle.rs_code import enumerate_codebook
from breaking_proofs.oracle.structured_verifier import incidence_count_structured
from breaking_proofs.search.construction import build_kkh26_instance
from breaking_proofs.search.params import KKH26Params

logger = get_logger(__name__)

BRUTE_FORCE_THRESHOLD = 1_000_000
# CA is O(codebook^2 * n); keep this low to avoid quadratic blowup
CA_THRESHOLD = 10_000


def params_to_id(params: KKH26Params) -> str:
    """Generate a stable string ID for a parameter set."""
    return f"p{params.p}_n{params.n}_k{params.k}_a{params.alpha}_K{params.K}"


def evaluate_params(params: KKH26Params) -> dict:
    """Evaluate a single KKH26 parameter set against the oracle.

    Chooses brute-force or structured verification based on codebook size.
    Returns a result dict with oracle outputs and timing.
    """
    pid = params_to_id(params)
    logger.info("worker_start", params_id=pid, p=params.p, n=params.n, k=params.k)
    start = time.perf_counter()

    try:
        instance = build_kkh26_instance(params, compute_witnesses=True)
        codebook_size = params.p ** params.k

        if codebook_size <= BRUTE_FORCE_THRESHOLD:
            codebook = enumerate_codebook(params.p, params.k, instance.domain)
            inc = incidence_count(
                instance.f, instance.g, codebook, params.p, params.delta_n
            )
            if codebook_size <= CA_THRESHOLD:
                ca = has_correlated_agreement(
                    instance.f, instance.g, codebook, params.p, params.delta_n
                )
            else:
                ca = None
        else:
            inc = incidence_count_structured(
                instance.f,
                instance.g,
                instance.domain,
                params.p,
                params.k,
                params.delta_n,
            )
            ca = None

        elapsed_ms = (time.perf_counter() - start) * 1000
        result = {
            "params_id": pid,
            "params": asdict(params),
            "incidence_count": inc,
            "has_correlated_agreement": ca,
            "distance": params.delta_n,
            "witness_count": len(instance.witnesses) if instance.witnesses else None,
            "runtime_ms": round(elapsed_ms, 2),
        }
        logger.info(
            "worker_complete", params_id=pid,
            incidence_count=inc, runtime_ms=round(elapsed_ms, 2),
        )
        return result

    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.error("worker_error", params_id=pid, error=str(e))
        return {
            "params_id": pid,
            "params": asdict(params),
            "error": str(e),
            "runtime_ms": round(elapsed_ms, 2),
        }
