---
name: workflow-refine
description: "Refine mode — lightweight pipeline for user-directed refinements. Use when the user says 'refine X', passes --refine, or wants a targeted change without the overhead of research and multi-hypothesis cycles. Classifies the request, implements with Builder, verifies with QA, and archives."
disable-model-invocation: true
argument-hint: "<project_path> --refine "<request>""
---

# Refine Workflow

The user wants: **$ARGUMENTS**

## Phase 1: Refiner

```bash
factory agent refiner --task "Classify and scope a refinement request. Read CLAUDE.md and factory.md. Analyze the codebase to identify which files need to change, estimate scope, and classify the request as Tier 1, 2, or 3. Produce the structured classification output with a Builder task description. Write the refinement plan to .factory/strategy/current.md.
Write output to: .factory/reviews/refiner-latest.md, .factory/strategy/current.md" --project "$PROJECT_PATH" --timeout 600
```

```bash
# Artifact verification: refiner
_vfail=0
_f="$PROJECT_PATH/.factory/reviews/refiner-latest.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: refiner: .factory/reviews/refiner-latest.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: refiner: .factory/reviews/refiner-latest.md is empty" && _vfail=1
_f="$PROJECT_PATH/.factory/strategy/current.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: refiner: .factory/strategy/current.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: refiner: .factory/strategy/current.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=refiner" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: refiner artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=refiner" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

### CEO Review — Refiner

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/reviews/refiner-latest.md`
3. Assess: Review Refiner classification. Is the tier classification reasonable? Are the identified files correct? Is the Builder task description specific enough? REDIRECT if the classification is wrong.
4. Write verdict to `.factory/reviews/ceo-verdict-refiner.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `refiner` (max 3 iterations)*

### Gate — Tier (Automated)

**MANDATORY:** Wait for the preceding agent to finish, then run this check BEFORE spawning the next agent. Do NOT run agents in parallel across this gate.

```bash
python3 -c "from pathlib import Path; text = Path('$PROJECT_PATH/.factory/reviews/refiner-latest.md').read_text(); print('HALT' if 'Tier 3' in text or 'tier 3' in text or 'TIER 3' in text else 'PROCEED')"
```

- **PROCEED** (exit 0 / no FAIL in output) → continue to `begin`
- **HALT** (exit non-zero / FAIL in output) → do NOT spawn `begin`. Skip to the next CEO review gate or finalize as error.

## Step: Begin

Open a new experiment for the refinement. The CEO must substitute $HYPOTHESIS with the refinement description.

```bash
factory begin $PROJECT_PATH --hypothesis "$HYPOTHESIS"
```

## Step: Create Issue

Create a GitHub issue to track the refinement. Must run after begin so the experiment ID is available.

```bash
gh issue create --title "Refine: refinement request" --label "refinement" --body "Factory refinement experiment."
```

## Phase 2: Builder

```bash
factory agent builder --task "Implement the refinement described in the Refiner's output. Read the GitHub issue. Read CLAUDE.md and factory.md. Implement exactly what the issue describes. Run tests. Commit and open a draft PR.
Read: .factory/reviews/refiner-latest.md
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

## Phase 3: Qa (Parallel)

Spawn 3 agents in parallel:

```bash
factory agent health_checker --task "Execute health_checker task for the project.
Read: .factory/reviews/builder-latest.md, .factory/strategy/current.md
Write output to: .factory/reviews/health-check.md" --project "$PROJECT_PATH" --timeout 600 &
```

```bash
factory agent code_reviewer --task "Run `factory guard --check-scope` to verify the refinement stays within declared scope.
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
3. Assess: Read QA output. Did all verification sections pass? Are there issues that need Builder fixes? REDIRECT to Builder if issues found (max 3 iterations).
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

Close the refinement experiment with a verdict. The CEO must substitute $EXP_ID, $VERDICT (keep/revert/error), and $HYPOTHESIS.

```bash
factory finalize $PROJECT_PATH --id $EXP_ID --verdict $VERDICT --hypothesis "$HYPOTHESIS"
```

## Phase 4: Archivist

```bash
factory agent archivist --task "Archive refinement experiment results and learnings.
Read: .factory/experiments/verdict.json
Write output to: .factory/archive/refinement.md" --project "$PROJECT_PATH" --timeout 300 --model haiku &
```
*(fire-and-forget — CEO continues immediately)*
