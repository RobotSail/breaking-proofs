# Validation Results

## alpha4-validation (alpha <= 4)

Pipeline validation run covering the full feasible parameter space at alpha <= 4.

### What this covers

- **3 candidate parameter sets:** all valid KKH26 constructions with alpha <= 4,
  rates in {1/4, 1/8, 1/16}, K=4, C=0.5.
- All candidates have p=17, n=16 (the smallest multiplicative subgroup).

### What this does NOT show

1. **All "significant" hits match the KKH26 baseline theta exactly (delta 0.0000).**
   These are baseline rediscoveries, not novel results. The search pipeline correctly
   reproduces what the KKH26 construction predicts — it has not found anything new.

2. **The current oracle cannot reach interesting parameter regimes.** Alpha >= 5
   produces candidates with codebook sizes exceeding the brute-force threshold,
   triggering the structured verifier path which is impractically slow (~180s+
   per candidate with no guarantee of completion).

3. **These results validate that the pipeline works end-to-end** — parameterize,
   construct, verify, report — not that it has discovered novel counterexamples.

### Files

- `alpha4-validation.jsonl` — raw JSONL search log (3 records)
- `alpha4-validation-report.md` — formatted Markdown analysis report
