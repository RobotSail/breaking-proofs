---
name: workflow-meta
description: "Meta mode — cross-project insights, playbook evolution, and test pruning. Use when the user says 'meta', 'self-improve', 'evolve playbooks', or wants to improve the factory's own agents."
disable-model-invocation: true
argument-hint: "<project_path>"
---

# Meta Workflow

The user wants: **$ARGUMENTS**

## Step: Insights

Collect cross-project insights from the global registry. Must run before researcher to provide data for pattern analysis.

```bash
factory insights $PROJECT_PATH
```

## Phase 1: Researcher

```bash
factory agent researcher --task "Read cross-project insights at .factory/strategy/insights.md and current playbooks. Identify recurring patterns, anti-patterns, and improvement opportunities. Compare agent performance across projects. Write findings to .factory/strategy/research-local.md.
Read: .factory/strategy/insights.md
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
3. Assess: Are cross-project patterns well-supported by data? Are proposed improvements actionable? Any blind spots?
4. Write verdict to `.factory/reviews/ceo-verdict-research.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `researcher` (max 3 iterations)*

## Phase 2: Strategist

```bash
factory agent strategist --task "Propose specific playbook edits based on cross-project research. For each agent role, propose DO/DON'T bullet additions or removals with supporting evidence from experiment data. Write diffs to .factory/strategy/playbook-diffs.md.
Read: .factory/strategy/research-local.md
Write output to: .factory/strategy/playbook-diffs.md" --project "$PROJECT_PATH" --timeout 600
```

```bash
# Artifact verification: strategist
_vfail=0
_f="$PROJECT_PATH/.factory/strategy/playbook-diffs.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: strategist: .factory/strategy/playbook-diffs.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: strategist: .factory/strategy/playbook-diffs.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=strategist" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: strategist artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=strategist" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

### Steering Point — User (User Approval)

**This is a USER approval gate, NOT a CEO review gate. Do NOT self-approve.**

Present the strategy/findings to the user by summarizing key points in your output.
Then explicitly ask the user: "Do you approve this plan, or do you have feedback?"

**You MUST wait for the user's response before proceeding.**
- The user says "approve", "yes", "looks good", or similar → proceed to next step
- The user provides feedback or corrections → re-run the previous step incorporating their feedback
- Do NOT write a verdict file and auto-proceed — this gate requires human input

*On RELOOP: return to `strategist` (max 3 iterations)*

## Step: Apply Playbooks

Apply user-approved playbook diffs via the ACE engine. Runs after user gate approval.

```bash
factory ace $PROJECT_PATH
```

## Phase 3: Archivist

```bash
factory agent archivist --task "Archive playbook evolution results.
Read: .factory/archive/playbooks-applied.md
Write output to: .factory/archive/meta.md" --project "$PROJECT_PATH" --timeout 300 --model haiku &
```
*(fire-and-forget — CEO continues immediately)*

## Step: Test Collect

Collect test inventory via pytest dry-run. Never fails (|| true) — output feeds the test pruning researcher.

```bash
pytest --co -q 2>/dev/null || true
```

## Phase 4: Test Researcher

```bash
factory agent researcher --task "Analyze test inventory for redundant, dead, or flaky tests. Identify tests that overlap, test nothing meaningful, or are consistently flaky. Write findings to .factory/strategy/test-analysis.md with specific test names and reasons for removal.
Read: .factory/strategy/test-inventory.md
Write output to: .factory/strategy/test-analysis.md" --project "$PROJECT_PATH" --timeout 600
```

```bash
# Artifact verification: test_researcher
_vfail=0
_f="$PROJECT_PATH/.factory/strategy/test-analysis.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: test_researcher: .factory/strategy/test-analysis.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: test_researcher: .factory/strategy/test-analysis.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=test_researcher" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: test_researcher artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=test_researcher" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

### Steering Point — Test Prune (User Approval)

**This is a USER approval gate, NOT a CEO review gate. Do NOT self-approve.**

Present the strategy/findings to the user by summarizing key points in your output.
Then explicitly ask the user: "Do you approve this plan, or do you have feedback?"

**You MUST wait for the user's response before proceeding.**
- The user says "approve", "yes", "looks good", or similar → proceed to next step
- The user provides feedback or corrections → re-run the previous step incorporating their feedback
- Do NOT write a verdict file and auto-proceed — this gate requires human input

*On RELOOP: return to `test_researcher` (max 3 iterations)*

## Phase 5: Test Builder

```bash
factory agent builder --task "Delete the approved redundant tests. Verify remaining suite still passes.
Read: .factory/strategy/test-analysis.md
Write output to: .factory/reviews/test-pruning-latest.md" --project "$PROJECT_PATH" --timeout 1800
```

```bash
# Artifact verification: test_builder
_vfail=0
_f="$PROJECT_PATH/.factory/reviews/test-pruning-latest.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: test_builder: .factory/reviews/test-pruning-latest.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: test_builder: .factory/reviews/test-pruning-latest.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=test_builder" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: test_builder artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=test_builder" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

## Phase 6: Health Checker — Qa Verify

```bash
factory agent health_checker --task "Verify the test suite still passes after pruning. Run health check and confirm no regressions. Write results to .factory/reviews/qa-verify-latest.md
Read: .factory/reviews/test-pruning-latest.md
Write output to: .factory/reviews/qa-verify-latest.md" --project "$PROJECT_PATH" --timeout 1800
```

```bash
# Artifact verification: qa_verify
_vfail=0
_f="$PROJECT_PATH/.factory/reviews/qa-verify-latest.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: qa_verify: .factory/reviews/qa-verify-latest.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: qa_verify: .factory/reviews/qa-verify-latest.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=qa_verify" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: qa_verify artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=qa_verify" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

### CEO Review — Qa Verify

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/reviews/qa-verify-latest.md`
3. Assess: Review QA verification of test pruning. PROCEED if tests still pass. RELOOP to test_builder (max 3 iterations) if regressions found.
4. Write verdict to `.factory/reviews/ceo-verdict-qa-verify.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `test_builder` (max 3 iterations)*
