---
name: workflow-improve
description: "Improve an existing project through systematic experimentation. Runs study, research, hypothesis generation, build/eval loop, and archival. Use when the user says 'improve X', 'make X better', or the project state is has_factory."
disable-model-invocation: true
argument-hint: "<project_path> [--focus <target>]"
---

# Improve Workflow

The user wants: **$ARGUMENTS**

## Phase 1: Observe

Run local study to gather observations:

```bash
factory study $PROJECT_PATH
```

Writes observations to `.factory/strategy/observations.md`.

## Phase 2: Researcher

```bash
factory agent researcher --task "Deep research for the project. Read observations at .factory/strategy/observations.md. Analyze codebase structure, eval scores, and experiment history. Search the web for best practices relevant to weak dimensions. Check .factory/archive/ for prior knowledge. Write findings to .factory/strategy/research-local.md.
Read: .factory/strategy/observations.md
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
factory agent strategist --task "Generate prioritized hypotheses. Read the backlog at .factory/strategy/backlog.md — clear as many items as possible. Read Hypothesis Budget from observations for constraints. Read CEO research review at .factory/reviews/ceo-verdict-researcher.md. Each hypothesis must be specific, scoped to one PR, tied to observations, with expected impact on eval dimensions. Tag backlog items with **Backlog item:** and new items with **New:**. Write to .factory/strategy/current.md.
Read: .factory/strategy/observations.md, .factory/strategy/research-local.md
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
factory agent code_reviewer --task "Execute code_reviewer task for the project.
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
