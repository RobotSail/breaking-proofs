# Search Analysis Report

## Parameters Explored

- **Total parameters evaluated:** 3
- **Rates (ρ):** 0.0625, 0.1250, 0.2500
- **Code length range (n):** 16–16
- **Field size range (p):** 17–17
- **Errors:** 0

## Hit Rate by Regime

| Rate (ρ) | Evaluations | With Incidence | No CA | Best θ | Baseline θ | UDR Bound | JBR Bound |
|---------|-------------|----------------|-------|--------|------------|-----------|-----------|
| 0.0625 | 1 | 1 | 1 | 0.8125 | 0.8125 | 0.4688 | 0.7500 |
| 0.1250 | 1 | 1 | 1 | 0.7500 | 0.7500 | 0.4375 | 0.6464 |
| 0.2500 | 1 | 1 | 0 | 0.6250 | 0.6250 | 0.3750 | 0.5000 |

## Best Counterexample Found

- **Params ID:** `p17_n16_k1_a4_K4`
- **Rate (ρ):** 0.0625
- **Proximity (θ):** 0.8125
- **Incidence count:** 16
- **Correlated agreement:** False
- **Regime:** BEYOND
- **Soundcalc significant:** YES

## KKH26 Baseline Comparison

- **ρ = 0.0625:** baseline θ = 0.8125, best θ = 0.8125 (0.0000)
- **ρ = 0.1250:** baseline θ = 0.7500, best θ = 0.7500 (0.0000)
- **ρ = 0.2500:** baseline θ = 0.6250, best θ = 0.6250 (0.0000)

## Interesting Hits

| Params ID | ρ | θ | Incidence | CA | Regime |
|-----------|------|------|-----------|------|--------|
| `p17_n16_k1_a4_K4` | 0.0625 | 0.8125 | 16 | False | BEYOND |
| `p17_n16_k2_a4_K4` | 0.1250 | 0.7500 | 17 | False | BEYOND |
| `p17_n16_k4_a4_K4` | 0.2500 | 0.6250 | 17 | — | BEYOND |

## Soundcalc Significance

**3 hit(s) fall in the proximity gap (JBR regime) or beyond.**
These results may tighten soundcalc's reported bounds.
