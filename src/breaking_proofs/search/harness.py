"""ProcessPoolExecutor-based parallel search harness.

Resume-capable: scans existing JSONL for completed parameter IDs at startup.
Uses submit() + as_completed() for incremental persistence and per-future
exception handling.
"""

import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from uuid import uuid4

import structlog

from breaking_proofs.logging import get_logger
from breaking_proofs.search.params import generate_candidates
from breaking_proofs.search.worker import evaluate_params, params_to_id

logger = get_logger(__name__)

DEFAULT_OUTPUT = "results/search-log.jsonl"


def load_completed_ids(output_path: str) -> set[str]:
    """Scan existing JSONL for completed parameter IDs."""
    completed: set[str] = set()
    path = Path(output_path)
    if not path.exists():
        return completed
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                pid = record.get("params_id")
                if pid and "error" not in record:
                    completed.add(pid)
            except json.JSONDecodeError:
                continue
    logger.info("loaded_completed_ids", count=len(completed), path=output_path)
    return completed


BRUTE_FORCE_THRESHOLD = 1_000_000


def run_search(
    max_alpha: int = 8,
    max_n: int | None = None,
    rates: list[tuple[int, int]] | None = None,
    workers: int | None = None,
    output_path: str = DEFAULT_OUTPUT,
    C: float = 0.5,
) -> list[dict]:
    """Run the parallel search harness over the KKH26 parameter space.

    Args:
        max_alpha: Maximum subgroup exponent.
        max_n: Maximum code length n; candidates with n > max_n are
            filtered out before worker dispatch.
        rates: List of (numerator, denominator) dyadic rates.
        workers: Pool size (defaults to os.cpu_count()).
        output_path: JSONL output file path.
        C: Free constant for KKH26 construction.

    Returns:
        List of result dicts from all completed evaluations this run.
    """
    run_id = uuid4().hex[:12]
    structlog.contextvars.bind_contextvars(run_id=run_id)

    if workers is None:
        workers = os.cpu_count() or 1

    candidates = generate_candidates(max_alpha=max_alpha, rates=rates, C=C)
    logger.info("generated_candidates", count=len(candidates), max_alpha=max_alpha)

    if max_n is not None:
        before = len(candidates)
        candidates = [c for c in candidates if c.n <= max_n]
        logger.info(
            "max_n_filter",
            max_n=max_n,
            before=before,
            after=len(candidates),
            filtered_out=before - len(candidates),
        )
        if not candidates:
            logger.warning(
                "max_n_filtered_all",
                max_n=max_n,
                message="All candidates exceed max_n — nothing to evaluate",
            )
            return []

    for c in candidates:
        codebook_size = c.p ** c.k
        if codebook_size > BRUTE_FORCE_THRESHOLD:
            logger.warning(
                "large_codebook",
                params_id=f"p{c.p}_n{c.n}_k{c.k}",
                codebook_size=codebook_size,
                message="Exceeds brute-force threshold; structured verifier will be used",
            )

    completed = load_completed_ids(output_path)
    pending = [p for p in candidates if params_to_id(p) not in completed]
    logger.info(
        "search_plan",
        total=len(candidates),
        already_done=len(completed),
        pending=len(pending),
    )

    if not pending:
        logger.info("search_complete", message="all candidates already evaluated")
        return []

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    start = time.perf_counter()

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for params in pending:
            future = executor.submit(evaluate_params, params)
            futures[future] = params

        for done_count, future in enumerate(as_completed(futures), 1):
            params = futures[future]
            pid = params_to_id(params)

            try:
                result = future.result()
            except Exception as e:
                logger.error("future_error", params_id=pid, error=str(e))
                result = {
                    "params_id": pid,
                    "error": str(e),
                    "runtime_ms": 0,
                }

            result["run_id"] = run_id
            results.append(result)

            with out_path.open("a") as f:
                f.write(json.dumps(result) + "\n")

            elapsed = time.perf_counter() - start
            logger.info(
                "search_progress",
                completed=done_count,
                total=len(pending),
                elapsed_s=round(elapsed, 1),
                params_id=pid,
            )

    elapsed_total = time.perf_counter() - start
    logger.info(
        "search_finished",
        evaluated=len(results),
        elapsed_s=round(elapsed_total, 1),
        output=output_path,
    )
    return results
