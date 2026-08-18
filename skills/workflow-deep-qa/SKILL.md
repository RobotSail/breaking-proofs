---
name: workflow-deep-qa
description: "Deep-QA mode — run the 3-specialist verification pipeline against a PR. Spawns health_checker, code_reviewer, and adversarial_tester agents with sequential gates, precheck, and posts verdict as GitHub PR review."
disable-model-invocation: true
argument-hint: "<project_path> --pr <number>"
---

# Deep Qa Workflow

The user wants: **$ARGUMENTS**

**Output constraint:** Your ONLY GitHub output artifact is the `factory review` command in the final step. Do NOT run `gh pr comment`, `gh issue comment`, or post any other comments on the PR. All analysis stays in .factory/reviews/ files.

## Phase 1: Qa (Parallel)

Spawn 3 agents in parallel:

```bash
factory agent health_checker --task "Execute health_checker task for the project.
Write output to: .factory/reviews/health-check.md" --project "$PROJECT_PATH" --timeout 600 &
```

```bash
factory agent code_reviewer --task "Execute code_reviewer task for the project.
Write output to: .factory/reviews/code-review.md" --project "$PROJECT_PATH" --timeout 900 &
```

```bash
factory agent adversarial_tester --task "Execute adversarial_tester task for the project.
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

### Gate — Precheck (Automated)

**MANDATORY:** Wait for the preceding agent to finish, then run this check BEFORE spawning the next agent. Do NOT run agents in parallel across this gate.

```bash
factory precheck $PROJECT_PATH --score-before 0 --score-after 0
```

- **PROCEED** (exit 0 / no FAIL in output) → continue to `post_review`
- **HALT** (exit non-zero / FAIL in output) → continue to `post_review` instead.

## Step: Post Review

```bash
factory review --verdict $VERDICT --pr $PR_NUMBER --score-before $SCORE_BEFORE --score-after $SCORE_AFTER
```
