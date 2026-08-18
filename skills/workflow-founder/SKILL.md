---
name: workflow-founder
description: "Founder mode — rapid prototyping pipeline for fast hypothesis iteration. Use when you want to test ideas quickly without full QA overhead. Picks one hypothesis, builds a prototype, runs tests once, records the result. No research, no code review, no adversarial QA, no eval scoring. Terminal — does not chain to other modes. Run --mode improve to harden."
disable-model-invocation: true
argument-hint: "<project_path>"
---

# Founder Workflow

The user wants: **$ARGUMENTS**

## Phase 1: Observe

Run local study to gather observations:

```bash
factory study $PROJECT_PATH
```

Writes observations to `.factory/strategy/observations.md`.

## Phase 2: Strategist

```bash
factory agent strategist --task "Pick ONE high-leverage hypothesis to prototype. Read observations at .factory/strategy/observations.md. Skip FEEC classification and backlog grooming — just pick the most promising idea and write it to .factory/strategy/current.md. Keep it scoped: one idea, one PR, fast to implement.
Read: .factory/strategy/observations.md
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

## Phase 3: Builder

```bash
factory agent builder --task "Prototype the hypothesis from .factory/strategy/current.md. Read CLAUDE.md and factory.md for project context. Prioritize getting something working over code quality. Skip edge cases and comprehensive error handling. Run tests to verify it works. Commit the changes.
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

### Gate — Tests (Automated)

**MANDATORY:** Wait for the preceding agent to finish, then run this check BEFORE spawning the next agent. Do NOT run agents in parallel across this gate.

```bash
cd $PROJECT_PATH && python -m pytest --tb=short -q 2>&1 && ruff check . 2>&1
```

- **PROCEED** (exit 0 / no FAIL in output) → continue to `finalize`
- **HALT** (exit non-zero / FAIL in output) → do NOT spawn `finalize`. Skip to the next CEO review gate or finalize as error.

*On RELOOP: return to `builder` (max 3 iterations)*

## Step: Finalize

Record experiment to .factory/results.tsv, bypassing precheck gates (no QA agents or eval scores in founder mode). The CEO must substitute $EXP_ID, $VERDICT (keep/revert), and $HYPOTHESIS.

```bash
factory finalize $PROJECT_PATH --id $EXP_ID --verdict $VERDICT --hypothesis "$HYPOTHESIS" --force
```
