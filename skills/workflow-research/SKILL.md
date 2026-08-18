---
name: workflow-research
description: "Research mode — extends improve with baseline measurement, failure analysis, research-command eval, and plateau detection. Use when the project has research_target configured and the user says 'research X' or wants metric-driven optimization."
disable-model-invocation: true
argument-hint: "<project_path>"
---

# Research Workflow

The user wants: **$ARGUMENTS**

## Step: Baseline

Run baseline evaluation to capture current scores before any changes. Must run before failure analysis.

```bash
factory eval $PROJECT_PATH
```

## Phase 1: Failure Analyst

```bash
factory agent failure_analyst --task "Analyze research run results. Read run artifacts at .factory/research/runs/. Read research target config from .factory/config.json. Classify failures by type and severity. Compute failure distribution. Suggest interventions within mutable surfaces only. Write to .factory/strategy/failure_analysis.md.
Read: .factory/experiments/baseline.json
Write output to: .factory/strategy/failure_analysis.md" --project "$PROJECT_PATH" --timeout 600
```

```bash
# Artifact verification: failure_analyst
_vfail=0
_f="$PROJECT_PATH/.factory/strategy/failure_analysis.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: failure_analyst: .factory/strategy/failure_analysis.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: failure_analyst: .factory/strategy/failure_analysis.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=failure_analyst" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: failure_analyst artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=failure_analyst" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

## Phase 2: Researcher

```bash
factory agent researcher --task "Failure-targeted research. Read failure analysis at .factory/strategy/failure_analysis.md. Search the web for solutions to the dominant failure modes. Check .factory/archive/ for prior knowledge on these patterns. Write findings to .factory/strategy/research-local.md.
Read: .factory/strategy/failure_analysis.md
Write output to: .factory/strategy/research-local.md" --project "$PROJECT_PATH" --timeout 600
```

```bash
# Artifact verification: researcher
_vfail=0
_f="$PROJECT_PATH/.factory/strategy/research-local.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: researcher: .factory/strategy/research-local.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: researcher: .factory/strategy/research-local.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=researcher" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: researcher artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=researcher" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

### CEO Review — Research

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/strategy/research-local.md`
3. Assess: Are observations grounded in data? Did web research surface useful patterns? Any blind spots in the analysis?
4. Write verdict to `.factory/reviews/ceo-verdict-research.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `researcher` (max 3 iterations)*

## Phase 3: Strategist

```bash
factory agent strategist --task "Generate research hypotheses targeting dominant failure modes. Each hypothesis must improve over the previous baseline score. Each hypothesis must name specific files from mutable_surfaces to modify. Hypotheses MUST NOT modify files in fixed_surfaces. Prioritize by expected impact on the target metric. Write 1-3 hypotheses to .factory/strategy/current.md.
Read: .factory/strategy/failure_analysis.md, .factory/strategy/research-local.md
Write output to: .factory/strategy/current.md" --project "$PROJECT_PATH" --timeout 600
```

```bash
# Artifact verification: strategist
_vfail=0
_f="$PROJECT_PATH/.factory/strategy/current.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: strategist: .factory/strategy/current.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: strategist: .factory/strategy/current.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=strategist" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: strategist artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=strategist" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

### CEO Review — Strategy

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/strategy/current.md`
3. Assess: HARD GATE. Check: specific enough to implement? Scoped to one PR? Expected eval impact realistic? Follows FEEC priority? Not redundant with reverted experiment? At least one growth hypothesis? Backlog convergence? Write PLAN APPROVED with approved hypotheses in priority order.
4. Write verdict to `.factory/reviews/ceo-verdict-strategy.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `strategist` (max 3 iterations)*

## Step: Apply Spec Diff

Apply the SPEC Diff section from the strategist's plan to SPEC.md. No-op if no SPEC Diff section exists.

```bash
factory spec apply-diff $PROJECT_PATH
```

## Step: Begin

Open a new experiment for the current hypothesis. The CEO must substitute $HYPOTHESIS with the hypothesis text.

```bash
factory begin $PROJECT_PATH --hypothesis "$HYPOTHESIS"
```

## Phase 4: Builder

```bash
factory agent builder --task "Implement the current hypothesis from .factory/strategy/current.md. Read CLAUDE.md and factory.md. Read the CEO strategy approval. Implement exactly what the hypothesis describes. Run tests. Commit and open a draft PR.
Read: .factory/strategy/current.md
Write output to: .factory/reviews/builder-latest.md" --project "$PROJECT_PATH" --timeout 1200
```

```bash
# Artifact verification: builder
_vfail=0
_f="$PROJECT_PATH/.factory/reviews/builder-latest.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: builder: .factory/reviews/builder-latest.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: builder: .factory/reviews/builder-latest.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=builder" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: builder artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=builder" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

### CEO Review — Build

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/reviews/builder-latest.md`
3. Assess: Read builder output and PR diff. Does work match the hypothesis? No scope creep? Tests included? REDIRECT if off-scope.
4. Write verdict to `.factory/reviews/ceo-verdict-build.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `builder` (max 3 iterations)*

## Phase 5: Qa (Parallel)

Spawn 3 agents in parallel:

```bash
factory agent health_checker --task "Execute health_checker task for the project.
Read: .factory/reviews/builder-latest.md, .factory/strategy/current.md
Write output to: .factory/reviews/health-check.md" --project "$PROJECT_PATH" --timeout 600 &
```

```bash
factory agent code_reviewer --task "Verify mutable/fixed surface constraint compliance. Check that no files in fixed_surfaces were modified.
Read: .factory/reviews/builder-latest.md, .factory/strategy/current.md
Write output to: .factory/reviews/code-review.md" --project "$PROJECT_PATH" --timeout 900 &
```

```bash
factory agent adversarial_tester --task "Execute adversarial_tester task for the project.
Read: .factory/reviews/builder-latest.md, .factory/strategy/current.md
Write output to: .factory/reviews/adversarial-qa.md" --project "$PROJECT_PATH" --timeout 1800 &
```

```bash
wait
```

**Important:** Run ALL commands above in a **single** Bash tool call with timeout set to at least 1800 seconds.

```bash
# Artifact verification: health_checker
_vfail=0
_f="$PROJECT_PATH/.factory/reviews/health-check.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: health_checker: .factory/reviews/health-check.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: health_checker: .factory/reviews/health-check.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=health_checker" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: health_checker artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=health_checker" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"

# Artifact verification: code_reviewer
_vfail=0
_f="$PROJECT_PATH/.factory/reviews/code-review.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: code_reviewer: .factory/reviews/code-review.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: code_reviewer: .factory/reviews/code-review.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=code_reviewer" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: code_reviewer artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=code_reviewer" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"

# Artifact verification: adversarial_tester
_vfail=0
_f="$PROJECT_PATH/.factory/reviews/adversarial-qa.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: adversarial_tester: .factory/reviews/adversarial-qa.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: adversarial_tester: .factory/reviews/adversarial-qa.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=adversarial_tester" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: adversarial_tester artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=adversarial_tester" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(post-barrier harness verification — DO NOT SKIP)*

## Barrier: Qa

Wait for all parallel agents to complete: `health_checker`, `code_reviewer`, `adversarial_tester`

Read combined outputs: `.factory/reviews/adversarial-qa.md`, `.factory/reviews/code-review.md`, `.factory/reviews/health-check.md`

### CEO Review — Qa

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/reviews/adversarial-qa.md`, `.factory/reviews/code-review.md`, `.factory/reviews/health-check.md`
3. Assess: Review QA results. PROCEED if all checks pass. RELOOP to builder (max 3 iterations) if issues found.
4. Write verdict to `.factory/reviews/ceo-verdict-qa.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `builder` (max 3 iterations)*

### CEO Review — Doc Freshness

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/reviews/adversarial-qa.md`
3. Assess: Check the PR diff for documentation freshness. If public APIs, CLI commands, configuration options, or architecture were changed or added, corresponding documentation (README.md, CLAUDE.md, docstrings, --help text, or doc/ files) MUST be updated. PROCEED if docs are current or no doc-worthy changes exist. RELOOP to builder if documentation is stale — specify exactly which changes need doc updates.
4. Write verdict to `.factory/reviews/ceo-verdict-doc-freshness.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `builder` (max 3 iterations)*

### Gate — Precheck (Automated)

**MANDATORY:** Wait for the preceding agent to finish, then run this check BEFORE spawning the next agent. Do NOT run agents in parallel across this gate.

```bash
factory precheck $PROJECT_PATH --score-before 0 --score-after 0
```

- **PROCEED** (exit 0 / no FAIL in output) → continue to `finalize`
- **HALT** (exit non-zero / FAIL in output) → continue to `archivist` instead.

## Step: Finalize

Close the experiment with a keep/revert verdict. The CEO must substitute $EXP_ID, $VERDICT (keep/revert/error), and $HYPOTHESIS.

```bash
factory finalize $PROJECT_PATH --id $EXP_ID --verdict $VERDICT --hypothesis "$HYPOTHESIS"
```

## Phase 6: Archivist

```bash
factory agent archivist --task "Archive experiment results and learnings.
Read: .factory/experiments/verdict.json
Write output to: .factory/archive/experiment.md" --project "$PROJECT_PATH" --timeout 300 --model haiku &
```
*(fire-and-forget — CEO continues immediately)*

## Step: Spec Update

Update SPEC.md via the gated spec-update workflow if it exists. Runs non-blocking after archival; skips silently if no spec file is present.

```bash
python3 -c "from pathlib import Path; import subprocess, sys; sys.exit(0) if not Path('$PROJECT_PATH/SPEC.md').is_file() else None; r = subprocess.run(['factory', 'workflow', 'run', 'spec-update', '$PROJECT_PATH'], capture_output=True, text=True); print(r.stdout); print(r.stderr, file=sys.stderr); sys.exit(0)"
```

### Gate — Plateau Gate (Automated)

**MANDATORY:** Wait for the preceding agent to finish, then run this check BEFORE spawning the next agent. Do NOT run agents in parallel across this gate.

```bash
python3 -c "import json, pathlib, sys; tsv = pathlib.Path('$PROJECT_PATH/.factory/results.tsv'); lines = [l for l in tsv.read_text().strip().splitlines()[1:] if l.strip()] if tsv.exists() else []; scores = []; [scores.append(float(p)) for l in lines for i, p in enumerate(l.split(chr(9))) if i == 2 and p]; recent = scores[-3:] if len(scores) >= 3 else scores; improved = len(recent) < 2 or recent[-1] > recent[-2]; print('RELOOP' if improved else 'PROCEED')"
```

*On RELOOP: return to `baseline` (max 3 iterations)*
