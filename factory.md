# Factory Configuration — breaking-proofs

## Project

Exact-arithmetic RS proximity oracle and counterexample search harness
for the Ethereum Foundation Proximity Prize ($1M).

## Target Branch

main

## Modifiable Surfaces

- `src/` — all source code
- `tests/` — all test files
- `pyproject.toml` — project configuration
- `factory.md` — this file
- `results/` — search result output directory

## Fixed Surfaces

- `eval/score.py` — eval harness (eval-only; do not modify from Builder agents)
- `.factory/` — factory state

## Eval Configuration

Eval script: `eval/score.py`

### Dimensions

| Dimension | Weight | Description |
|---|---|---|
| oracle_correctness | 0.35 | Oracle regression tests (test_oracle_small + test_kkh26) |
| cross_check_parity | 0.20 | Galois vs reference oracle agreement |
| tests | 0.15 | Full test suite pass rate |
| lint | 0.10 | ruff check on src/ and tests/ |
| type_check | 0.10 | py_compile on all source files |
| observability | 0.10 | Structured logging coverage |

## Scope Notes

- NO floating point in oracle code. Use int and galois GF(p) exclusively.
- The oracle is the trust root: correctness > performance > features.
- Cross-check parity between galois oracle and reference oracle is mandatory.
