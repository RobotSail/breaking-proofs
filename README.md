# Disproving a STARK Soundness Conjecture: A Working Brief

**Compiled:** 14 August 2026
**Target audience:** you, deciding whether to spend real time on this
**Bottom line up front:** the target is real, there is $1M attached to it from the Ethereum Foundation, the low-hanging counterexamples were already taken in November 2025, and the remaining open region is now known to be blocked behind a two-decade-old analytic wall in additive combinatorics. There is still a genuinely attackable seam, and it is counterexample search inside a specific parameter window. An LLM-agent campaign is already running against it.

---

## 1. What the conjecture actually is

### 1.1 The setup

Hash-based SNARKs (STARKs, FRI, STIR, WHIR, and essentially every zkVM on Ethereum's roadmap) work by encoding the prover's witness with a Reed-Solomon code and then running a *proximity test* so the verifier can check, from a handful of queried positions, that the committed word is close to a genuine codeword.

Two parameters govern everything:

- **Rate** ρ = k/n. Deployed systems use ρ ∈ {1/2, 1/4, 1/8, 1/16}. Lower rate means more redundancy, slower prover, smaller proof.
- **Proximity parameter** δ. The threshold at which the test declares a word "far" from the code. Bigger δ means fewer queries, so smaller proofs and faster verification. Bigger δ is what everyone wants.

Three radii organize the entire field:

| Radius | Value | Status |
|---|---|---|
| Unique decoding | (1 − ρ)/2 | Classical, easy, everything provable |
| **Johnson bound** | **1 − √ρ** | Guruswami-Sudan 1999. Proximity gaps *proven* up to here (BCIKS20) |
| **Capacity** | **1 − ρ** | Information-theoretic limit. Provably *unreachable* (Nov 2025) |

The interval between Johnson and capacity is **the window**. Deployed systems set parameters inside it. Nobody knows what is true in there. That is the whole problem.

### 1.2 The three properties, weakest to strongest

**Proximity gap.** For an affine line (or subspace) of words, either essentially all of them are δ-close to the code, or only a tiny fraction are. No middle ground. Introduced for IOPPs by Rothblum-Vadhan-Wigderson.

**Correlated agreement (CA).** Stronger and the usual route to a gap. Words u₀,...,u_ℓ have δ-correlated agreement with code C if there is a *single* subdomain D′ ⊆ D with |D′|/n ≥ 1 − δ and codewords v₀,...,v_ℓ such that uᵢ = vᵢ on all of D′. The same coordinate set witnesses agreement for every word simultaneously.

**Mutual correlated agreement (MCA).** Introduced in the WHIR analysis. Protocols like WHIR do not check one random linear combination per round, they check several different mixtures (folds, shifts, combination patterns). MCA demands the *same* large coordinate set witness agreement across the entire family of mixture operations. It is the strongest known form of distance preservation and it is what the tight soundness analyses of the fastest protocols actually assume.

The formal object the prize cares about:

```
δ*(C, ε*) = sup { δ : ε_mca(C, δ) ≤ ε* }
```

with ε* = 2⁻¹²⁸. Pinning δ* for explicit smooth-domain codes is the problem.

### 1.3 The conjectures that were assumed

| Conjecture | Source | Claim |
|---|---|---|
| Conjecture 8.4 | BCIKS20 (Ben-Sasson, Carmon, Ishai, Kopparty, Saraf) | Correlated agreement holds up to capacity, δ < 1 − ρ |
| Conjecture 2.3 | DEEP-FRI | Reed-Solomon list-decodability up to capacity |
| Conjecture 4.12 | WHIR | MCA up to capacity |

Almost all of the roughly two dozen zkVMs tracked by EthProofs set their parameters assuming some version of these.

---

## 2. What is already dead (do not re-derive this)

November 2025 saw six papers land inside a week. Three of them disprove.

**Crites and Stewart, ePrint 2025/2046, "On Reed-Solomon Proximity Gaps Conjectures."** The structurally important one. They give a reduction: if the RS code of rate k/n satisfies correlated agreement with error ε < 1/k, then the RS code of rate (k+1)/n is list decodable. Since list-decoding capacity for RS is well understood classically, any proximity gap beyond the list-decoding capacity bound would imply impossibly good list decoding. This kills all three up-to-capacity conjectures at once. Notably this work came out of their concurrent CRYPTO 2025 attack on threshold Schnorr signatures, via the Shamir-secret-sharing / Reed-Solomon connection.

**Diamond and Gruen, ePrint 2025/2010, "On the Distribution of the Distances of Random Words."** Super-polynomial proximity-gap error at vanishing rate. Carves out a concrete red zone of unsafe (ρ, δ) pairs.

**Ben-Sasson, Carmon, Haböck, Kopparty, Saraf, ECCC TR25-169 / ePrint 2025/2055, "On Proximity Gaps for Reed-Solomon Codes."** Sometimes cited as "proximity gaps stop at the Johnson bound." Establishes the coupling barrier: MCA past Johnson implies beyond-Johnson list decoding for explicit RS codes. Also identifies a sharp behavioral transition at γ = δ/3.

The positive results from the same wave, for context:

- Bordage, Chiesa, Guan, Manzur, ePrint 2025/2051. All polynomial generators preserve distance with MCA up to the Johnson bound. (CCC 2026.)
- Goyal and Guruswami, ePrint 2025/2054. Optimal proximity gaps for subspace-design codes and random RS codes.
- Chatterjee, Harsha, Kumar, ECCC 2025/170. Deterministic list decoding of RS codes.
- Haböck, ePrint 2025/2110. MCA for RS codes up to the Johnson radius, plus a general method.
- Garreta, Mohnblatt, Wagner, ePrint 2025/1993. Simplified round-by-round soundness proof of FRI based on MCA.

**2026 additions:**

- **Krachun, Kazanin, Haböck, ePrint 2026/782, "Failure of proximity gaps close to capacity."** The most attack-shaped prior result. An explicit counterexample for RS codes over multiplicative subgroups of prime fields. At relative distance θ = 1 − ρ − η with η = Θ_ρ(1/log n), they construct an affine line that is *not* entirely θ-close to the code but still contains 2^Ω_ρ(1/η) points that are. Proof uses a new additive-combinatorics lemma on sumsets plus Linnik's theorem for the quantitative part. Also gives a slightly stronger list-decoding lower bound.
- Kambiré, arXiv 2604.09724. Fleshes out the Krachun-Kazanin sketch in full. Read this one for the construction mechanics; it is the clearest exposition of how you actually build one of these counterexamples.
- Goyal, Guruswami, Sun, Wootters, arXiv 2607.08516, "Locality of Curve-Decoding and Improved Proximity Gaps."
- Jo, ePrint 2026/1432, "Reed-Solomon MCA Beyond the Johnson Radius," and ePrint 2026/891 on interleaving stability.
- Chojecki, ePrint 2026/1479, "Conjectures and Barriers for RS-MCA" (19 July 2026).
- Chai and Fan (IoTeX), ePrint 2026/861. Claims the first rigorous O(1)/|F| FRI commit-phase bound above Johnson, conditional on a "sparse worst-case dominance" conjecture. Treat as unconfirmed; it is recent and conditional.
- Jeronimo, Liu, Rajpal, arXiv 2601.10047. Optimal proximity gap for *folded* RS codes via subspace designs. Folding is the escape hatch; plain smooth domains resist.
- Yuan and Zhu, arXiv 2605.07595. Syndrome-space approach for random linear codes.

**Practical impact of the November disproofs, for calibration:**

- Crites-Stewart estimate: for log₂(q) ≥ 31 as used in practice, roughly a 3.2% reduction in achievable proximity parameter, translating to 10-15% larger proofs.
- zkSecurity's framing: moving all the way into the fully-proven region roughly doubles proof size and verifier time; moving to the nearest newly-conjectured-safe parameters costs 2-3%. Prover time is barely affected either way, since prover cost scales with ρ⁻¹ not δ.

So the disproofs mattered a great deal epistemically and only modestly operationally. Worth internalizing before you plan a headline.

---

## 3. What is actually open right now

The window, ρ-dependent, between 1 − √ρ and 1 − ρ. Specifically:

**Grand MCA Challenge (ABF26).** Given RS[F, L, k] over a smooth evaluation domain, rate ρ ∈ {1/2, 1/4, 1/8, 1/16}, and ε* = 2⁻¹²⁸, determine the largest δ* with ε_mca(C, δ*) ≤ ε*.

**Grand List Decoding Challenge (ABF26).** Same code family. For ε* = 2⁻¹²⁸ and constant m, determine the largest δ* with |Λ(C^≡m, δ*)| ≤ ε* · |F|.

Concrete prize regime: rates 1/2, 1/4, 1/8, 1/16; dimensions at most 2⁴⁰; fields smaller than 2²⁵⁶; target error 2⁻¹²⁸.

**The critical structural fact.** Because of the CS25 and BCHKS25 reductions, proving MCA anywhere past Johnson for explicit RS codes *implies* beyond-Johnson list decoding for explicit RS codes. That is a problem that has been open since Guruswami-Sudan 1999. So the *proof* direction is blocked behind a famous 25-year barrier. Folded RS codes achieve capacity (Guruswami-Rudra, and Chen-Zhang STOC 2025 for optimal list size), and randomly punctured RS codes achieve it (Guo-Zhang, Alrabiah-Guo-Guruswami-Li-Zhang), but the plain smooth 2-power multiplicative subgroup that FFT-based provers actually use resists.

**Implication for you:** the disproof direction is the tractable one, and it is search-shaped.

---

## 4. The money and the rules

### The Proximity Prize
**proximityprize.org** | contact: proximityprize@ethereum.org
$1,000,000, Ethereum Foundation. Announced by Justin Drake on the Zero Knowledge Podcast, autumn 2025.

**Judges:** Dan Boneh (Stanford), Giacomo Fenzi (EPFL), Gal Arnon (Bocconi).

**Companion paper:** Arnon, Boneh, Fenzi, "Open Problems in List Decoding and Correlated Agreement," ePrint 2026/680 (April 2026). Read this first; it is the authoritative statement of what counts.

**Submission rules, verbatim-ish:**
1. Email to proximityprize@ethereum.org.
2. **Must have passed peer review** via acceptance at a reputable field-appropriate conference or journal. This is the big constraint on your timeline to money.
3. Must be publicly posted to IACR ePrint or arXiv. First public version is the formal timestamp.
4. Formal verification (e.g. Lean) is encouraged but not required.
5. Disclose conflicts of interest.
6. Anyone eligible except the judges. Awards split equally among named authors unless specified.

**AI policy, quoted in substance:** AI-aided submissions are allowed, but submissions are expected to be human-verified and edited, using standard language and notation for the field. Human authors are solely responsible for correctness.

**Other useful details:** partial progress is explicitly encouraged and eligible. Awards can be split across multiple submissions. There is no grant program for people who need funding to work on it. The problem statements are labelled preliminary and the judges are actively soliciting feedback before finalizing conditions.

As of this writing I found no public record of any award having been made.

### Sibling target: the Poseidon Initiative
**poseidon-initiative.info** | $1M, announced January 2026 alongside the EF's new Post-Quantum team (led by Thomas Coratger).

Breaking Poseidon, the SNARK-friendly hash. Separate smaller prize track: attacks on reduced-round Poseidon-256, Poseidon-64, or Poseidon-31 (KoalaBear field, 2³¹ − 2²⁴ + 1), minimum $5,000, $90,000 fund, papers public on ePrint by end of 2026, program runs to 1 Jan 2029.

**Important:** the site currently states the program is **PAUSED as of 1 Aug 2026**. Check status before investing. Worth knowing this exists as an alternative or parallel target since it is much more directly cryptanalytic and closer in shape to CryptanalysisBench-style work.

---

## 5. Why this is newsworthy, mechanically

You wanted a "solve it and it makes news" target. Here is the transmission chain, which is unusually short:

1. **The EF made soundness the official 2026 boss fight.** Their 18 Dec 2025 post ("Shipping an L1 zkEVM #2: The Security Foundations") declared real-time proving done (16 minutes to 16 seconds, 45× cost reduction, 99% of blocks proven under 10 seconds on target hardware) and pivoted to provable security.

2. **They built a canonical scoreboard.** `soundcalc` (github.com/ethereum/soundcalc) is an EF-maintained universal soundness calculator across hash-based zkEVMs. It estimates round-by-round IOP soundness as a function of a parameter θ, with different analysis regimes depending on θ. It is explicitly a *living tool*: they plan to keep integrating the latest research and known attacks. A new counterexample changes soundcalc's output, which changes every participating team's stated bit-security, which is public.

3. **There are hard dated milestones.**
   - End Feb 2026: all zkEVM teams integrate proof systems and circuits with soundcalc.
   - End May 2026 (Glamsterdam): ≥100-bit provable security per soundcalc, final proofs ≤600 KB, compact description of recursion architecture.
   - End 2026: 128-bit provable security, proofs under 300 KB.

4. **The stakes framing is already written by the EF itself.** Their words: if an attacker can forge a proof, they can forge anything, mint tokens from nothing, rewrite state, steal funds. For an L1 zkEVM securing hundreds of billions, the margin is non-negotiable.

So a new negative result does not need you to write a press release. It lands in soundcalc, moves published numbers on Ethproofs, and forces named teams to change parameters before a public deadline. That is the story.

---

## 6. The competitive landscape, including the part you will not like

**There is already an LLM-agent campaign running against this exact target.**

`deltastar.computer` documents "Pinning δ*: Machine-Checked Thresholds for Mutual Correlated Agreement of Smooth Reed-Solomon Codes," a Lean 4 formalization campaign over a fork of ArkLib, led by Shaw (github.com/lalalune), with 10,000+ commits. The stated methodology is a fleet of LLM agents proposing and the Lean 4 kernel disposing, with every claim labelled Proven (kernel-checked, axiom census inside `propext, Classical.choice, Quot.sound`), Computational (exact enumeration, never floating point), or Open.

They explicitly invite you to point your own agent at it:

```
mine the proximity prize: read https://deltastar.computer/mission.md and follow it
```

There is a Claude Code skill install (`~/.claude/skills/proximity-prize/SKILL.md` from deltastar.computer/skill.md) and a Codex AGENTS.md path. Contributions land as PRs on lalalune/ArkLib and notes on issue #444.

**What they claim to have achieved** (worth reading carefully, because it maps the terrain for you):

- A structural result they call the **δ\* decoupling**: in the over-determined regime, the far-line incidence count is a union of per-witness singletons, hence bounded by the witness count and *independent of the field characteristic*. Kernel-checked.
- Exact closed form for over-determined incidence maximum: I_max(n) = n³/32 − n²/8 + 1.
- A complete tight reduction: the window-interior conclusion follows from *exactly one* named hypothesis, a quantitative subset-sum count (the BCHKS 1.12 conjecture), and the converse holds. They claim the prize reduces to this one combinatorial conjecture.
- A **moment-method no-go**: every energy, Parseval, or spectral route provably caps at the Johnson radius. Also that thinness is necessary.
- **Two machine-checked corrections to BCIKS20's own Appendix A recursion** (their findings 13 and 14), including an explicit countermodel over ZMod 5. Formalization debugged the literature.
- A `DISPROOF_LOG.md` recording 28 refuted candidate approaches, each reduced to a sorry-free constraint lemma.

**What they explicitly do not claim:** they do not resolve the floor. Their Open Problem 5.1 is whether the prize budget B = qε* = 2⁻¹²⁸ n^β (β ≈ 4-5) crosses the incidence decay curve I(s) at witness size s* − k = Θ(n/log n).

**The wall.** They locate the residual analytic difficulty at incomplete character sums over thin 2-power multiplicative subgroups: for S_b = Σ_{x ∈ μ_n} e_p(bx), the Bourgain-Glibichuk-Konyagin square-root cancellation bound M(n) ≤ n^{1/2+o(1)}. Best explicit exponent in range is around n^0.9892 (di Benedetto); they claim a conditional improvement to n^0.9583 at β = 4. The floor needs n^{1/2+o(1)}. That gap is roughly two decades old.

**How to read this source.** The site is self-published by an independent campaign rather than an academic group, and the framing is promotional. But the epistemic architecture is the right one: Lean kernel acceptance and `#print axioms` are third-party checkable, and you can clone lalalune/ArkLib and verify any labelled-proven claim yourself. Do that before you rely on any of it. Note also that the upstream, `Verified-zkEVM/ArkLib`, is the serious EF-adjacent effort (contributors including quangvdao, Alexander Hicks), formalizing IOR, sum-check, polynomial commitments, FRI/STIR/WHIR, Fiat-Shamir, and BCS transforms in Lean 4.

**Implication:** you are not first, and a naive "point Claude at the conjecture" run is precisely what several people are already doing. Your edge has to come from somewhere else. See §7.

---

## 7. Where the attackable seam actually is

Ranked by verification asymmetry, which is your usual criterion and happens to be exactly right here.

### 7.1 Counterexample search inside the window (best fit)

**The shape.** Fix (n, k, p) in the prize regime with p ≡ 1 mod n, ω a primitive n-th root of unity, D = ⟨ω⟩, C = RS[F_p, D, k]. Search for f, g ∈ F_p^D such that

```
|{ z ∈ F_p : Δ(f + zg, C) ≤ δ }|  is large,   while   Δ([f,g], C²) > δ
```

That is, an affine line with many close points but no correlated agreement. Constructing one is hard; **checking one is a finite exact computation**. Perfect asymmetry. This is the same object Krachun-Kazanin-Haböck built near capacity, pushed deeper into the window.

**Why an agent harness helps here specifically.** The construction space is structured (choice of prime, subgroup structure, sumset configuration, dimension ladder) and the objective is a scalar count with an exact checker. This is a search problem with a cheap oracle, not a proof problem. It is closer to zk.golf than to Erdős problems.

**Concrete parameterized target:** KKH26 gets η = Θ_ρ(1/log n) below capacity. Any construction that pushes η substantially larger, meaning deeper into the window and further from capacity, is a publishable strengthening and directly moves soundcalc.

### 7.2 Extending or generalizing the KKH26 construction

Read arXiv 2604.09724 first, then ePrint 2026/782. The core is an additive-combinatorics lemma on sumsets plus Linnik's theorem for quantitative existence of the right primes. The question of which subgroup structures admit large sumset counts is combinatorial and machine-searchable. BCHKS25 also has a Conjecture 1.12 in additive number theory about "admissible" triples (q, a, b) that gates the existence of infinitely many of their mild-loss instances. That conjecture is clean, basic, and stated in a form that supports computational attack.

### 7.3 Auditing published proofs for errors

The ArkLib campaign found two genuine errors in BCIKS20's Appendix A recursion. That is a real result and it came from formalization, not insight. The corpus of proximity-gap papers is now large, recent, and mostly not machine-checked. Systematically formalizing them against ArkLib will find more errors. This is boring, agent-friendly, high-yield, and publishable.

### 7.4 Lean formalization as a differentiator

The prize explicitly encourages formal verification. `Verified-zkEVM/ArkLib` already formalizes FRI, STIR, WHIR, sum-check, Fiat-Shamir, and BCS. `zksecurity/simple-rbr-fri` formalizes the Garreta-Mohnblatt-Wagner FRI round-by-round proof. There is a Rust-to-Lean pipeline paper (arXiv 2605.30106) using Aeneas/Hax plus AI provers (Aristotle from Harmonic, Aleph from Logical Intelligence) that is worth reading for harness design ideas.

### 7.5 What to avoid

- **Do not attack the at-capacity conjectures.** Dead, three times over, in Nov 2025.
- **Do not attempt a positive MCA result past Johnson via moment, energy, Parseval, or spectral methods.** There is a machine-checked no-go. More generally, a positive result in the window implies beyond-Johnson explicit RS list decoding, which is a 25-year barrier. If you find yourself heading there, you have either made a mistake or made history.
- **Do not expect the BGK character-sum wall to fall to compute.** It is analytic, it has resisted for two decades, and naming it does not shorten it.

---

## 8. A concrete two-week plan

**Days 1-3: load the problem.**
- ABF26 (ePrint 2026/680). The prize statement. Non-negotiable first read.
- zkSecurity's "Proximity Gaps: What Happened" (blog.zksecurity.xyz/posts/proximity-conjecture). Best 7-minute orientation, with the ρ-δ diagram that organizes everything.
- Play with Mahdi Sedaghat's interactive parameter tool at proximity.sedaghat.xyz to build intuition for where the regions sit.
- Angus Gruen's slides from ethproofs call #6 (youtube.com/watch?v=9zw5jOMB9UY).

**Days 4-6: load the state of the art.**
- CS25 (ePrint 2025/2046). The reduction that killed everything. Understand *why* it kills, because that constrains what you are allowed to hope for.
- BCHKS25 (ECCC TR25-169 / ePrint 2025/2055). The Johnson barrier.
- Kambiré (arXiv 2604.09724), then KKH26 (ePrint 2026/782). The counterexample mechanics. This is your template.
- BCIKS20 (ePrint 2020/654, J.ACM 2023). The original. Skim, then read §5 and Appendix A carefully, since that is where errors were found.

**Days 7-9: build the checker before the searcher.**
- Clone `ethereum/soundcalc`. Run `python3 -m soundcalc`. Understand exactly which regime and which bound your target result would move. If your result does not change a soundcalc number, it will not make news.
- Write an exact-arithmetic probe: given (p, n, k, f, g, δ), count |{z : Δ(f+zg, C) ≤ δ}| exactly. No floating point. This is your oracle. Every claim you ever make gets run through it first.
- Cross-check your probe against the published KKH26 counterexample parameters. If you cannot reproduce a known counterexample, your probe is wrong.

**Days 10-14: decide the seam and start.**
- Clone `lalalune/ArkLib`, read `DISPROOF_LOG.md` and `docs/kb/deltastar-research-map.md`, and run `#print axioms` on two or three of the claimed theorems. This tells you both what is genuinely done and what has already been ruled out, which is the cheapest possible way to avoid burning a month.
- Read issue #444 for the campaign record.
- Then pick: parameterized counterexample search (§7.1/7.2) if you want the harness angle, or literature formalization/auditing (§7.3) if you want reliable incremental output.

**Register your work publicly early.** The prize timestamps by first public ePrint/arXiv version. Given that at least one organized campaign and several academic groups are on this, posting a partial result is strictly better than sitting on it.

---

## 9. Honest assessment

**Odds of a full resolution:** low. The proof direction is behind Guruswami-Sudan. The disproof direction inside the window is behind BGK. Both are famous walls with serious people camped on them.

**Odds of a publishable partial result:** decent, and the prize explicitly funds partial progress. A new counterexample family that pushes δ* down anywhere in the window, a strengthening of KKH26's η, a corrected error in a published proof, or a new machine-checked impossibility for a class of methods all qualify.

**Odds of news coverage, by result tier:**

| Result | Coverage |
|---|---|
| Formalization of an existing result in Lean | ZK community only |
| Error found in a published proximity-gaps proof | zkSecurity/Veridise blogs, ZK Podcast, ethproofs call |
| New counterexample that moves soundcalc numbers | The Block, CoinDesk, Schneier-tier security blogs, EF blog response |
| Pinning δ\* in the window (either direction) | Mainstream tech press, IACR distinguished paper, $1M |

**The realistic play,** if your goal is the headline: aim at tier three. A new counterexample that forces named zkEVM teams to change parameters before the end-2026 128-bit deadline is a story with a villain, a deadline, a dollar figure, and an official EF scoreboard confirming it. That is a much shorter path to legibility than "solved a coding theory conjecture."

**The thing that would actually differentiate your harness** from the campaigns already running: they are doing proof search with a Lean kernel as the checker. The counterexample search in §7.1 is a different problem, closer to what you already build, where the checker is exact integer arithmetic rather than a proof assistant, the objective is a scalar, and the search space is parameterized by number-theoretic structure that can be enumerated. Nobody appears to be running that at scale with a proper adaptive harness. That is your seam.

---

## 10. Link index

**Prize and problem statements**
- proximityprize.org
- ePrint 2026/680 (Arnon, Boneh, Fenzi, "Open Problems in List Decoding and Correlated Agreement")
- poseidon-initiative.info (sibling $1M target, currently paused as of 1 Aug 2026)

**Core papers**
- ePrint 2020/654 / J.ACM 2023, dl.acm.org/doi/full/10.1145/3614423 (BCIKS20, the original)
- ePrint 2025/2046 (Crites-Stewart)
- ePrint 2025/2010 (Diamond-Gruen)
- ECCC TR25-169 / ePrint 2025/2055 (Ben-Sasson, Carmon, Haböck, Kopparty, Saraf)
- ePrint 2025/2051 (Bordage, Chiesa, Guan, Manzur), ePrint 2025/2054 (Goyal-Guruswami), ECCC 2025/170 (Chatterjee, Harsha, Kumar), ePrint 2025/2110 (Haböck), ePrint 2025/1993 (Garreta, Mohnblatt, Wagner)
- ePrint 2026/782 (Krachun, Kazanin, Haböck), arXiv 2604.09724 (Kambiré exposition)
- arXiv 2607.08516, ePrint 2026/1432, ePrint 2026/891, ePrint 2026/1479, ePrint 2026/861, arXiv 2601.10047, arXiv 2605.07595

**Tooling and code**
- github.com/ethereum/soundcalc
- github.com/Verified-zkEVM/ArkLib (upstream, EF-adjacent)
- github.com/lalalune/ArkLib (the agent campaign fork), issue #444
- github.com/zksecurity/simple-rbr-fri
- deltastar.computer, deltastar.computer/mission.md, deltastar.computer/skill.md
- proximity.sedaghat.xyz (interactive parameter explorer)
- verified-zkevm.org, leanroadmap.org

**Explainers and context**
- blog.zksecurity.xyz/posts/proximity-conjecture (start here)
- blog.zksecurity.xyz/posts/fri-security ("Why does FRI work?")
- blog.ethereum.org/2025/12/18/zkevm-security-foundations (the milestones)
- veridise.com/blog/learn-blockchain/proximity-gap-and-correlated-agreement
- hexens.io/blog/proximity-gaps
- zeroknowledge.fm/podcast/393 (lean Ethereum Part 3, with Fenzi and Sanso, includes a Proximity Prize update)
- youtube.com/watch?v=9zw5jOMB9UY (ethproofs call #6)

**Note on ePrint:** eprint.iacr.org blocks automated fetching and bans IPs for robots.txt violations. If you point an agent at this corpus, fetch through arXiv mirrors or download manually. Do not let a harness crawl ePrint.
