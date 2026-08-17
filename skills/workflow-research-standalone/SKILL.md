---
name: workflow-research-standalone
description: "Run the research-standalone workflow."
disable-model-invocation: true
argument-hint: "<project_path>"
---

# Research Standalone Workflow

The user wants: **$ARGUMENTS**

## Phase 1: Research (Parallel)

Spawn 3 agents in parallel:

```bash
factory agent researcher --review-tag similar --task "Similar projects research. Search the web for similar projects, existing solutions, and prior art. Analyze their strengths, weaknesses, and market positioning. Check .factory/archive/ for prior knowledge on similar builds. Write findings to .factory/strategy/research-similar.md covering: similar projects found (with links), what they do well and what's missing, differentiation opportunities.
Write output to: .factory/strategy/research-similar.md" --project "$PROJECT_PATH" --timeout 600 &
```

```bash
factory agent researcher --review-tag techstack --task "Tech stack research. Identify the best technology stack for this type of project. Find architecture patterns and best practices. Evaluate framework/library options with trade-offs. Write findings to .factory/strategy/research-techstack.md covering: recommended tech stack with rationale, architecture patterns, framework comparisons.
Write output to: .factory/strategy/research-techstack.md" --project "$PROJECT_PATH" --timeout 600 &
```

```bash
factory agent researcher --review-tag pitfalls --task "Pitfalls and scope research. Identify potential pitfalls and common mistakes for this type of project. Research MVP scope best practices. Check .factory/archive/ for lessons from past builds. Write findings to .factory/strategy/research-pitfalls.md covering: potential pitfalls to avoid, MVP scope recommendation, lessons from similar past builds.
Write output to: .factory/strategy/research-pitfalls.md" --project "$PROJECT_PATH" --timeout 600 &
```

```bash
wait
```

**Important:** Run ALL commands above in a **single** Bash tool call with timeout set to at least 600 seconds.

```bash
# Artifact verification: researcher_similar
_vfail=0
_f="$PROJECT_PATH/.factory/strategy/research-similar.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: researcher_similar: .factory/strategy/research-similar.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: researcher_similar: .factory/strategy/research-similar.md is empty" && _vfail=1
[ -f "$_f" ] && [ "$(wc -c < "$_f")" -lt 50 ] && echo "VERIFY FAIL: researcher_similar: .factory/strategy/research-similar.md smaller than 50 bytes" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=researcher_similar" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: researcher_similar artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=researcher_similar" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"

# Artifact verification: researcher_techstack
_vfail=0
_f="$PROJECT_PATH/.factory/strategy/research-techstack.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: researcher_techstack: .factory/strategy/research-techstack.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: researcher_techstack: .factory/strategy/research-techstack.md is empty" && _vfail=1
[ -f "$_f" ] && [ "$(wc -c < "$_f")" -lt 50 ] && echo "VERIFY FAIL: researcher_techstack: .factory/strategy/research-techstack.md smaller than 50 bytes" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=researcher_techstack" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: researcher_techstack artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=researcher_techstack" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"

# Artifact verification: researcher_pitfalls
_vfail=0
_f="$PROJECT_PATH/.factory/strategy/research-pitfalls.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: researcher_pitfalls: .factory/strategy/research-pitfalls.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: researcher_pitfalls: .factory/strategy/research-pitfalls.md is empty" && _vfail=1
[ -f "$_f" ] && [ "$(wc -c < "$_f")" -lt 50 ] && echo "VERIFY FAIL: researcher_pitfalls: .factory/strategy/research-pitfalls.md smaller than 50 bytes" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=researcher_pitfalls" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: researcher_pitfalls artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=researcher_pitfalls" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(post-barrier harness verification — DO NOT SKIP)*

## Barrier: Research

Wait for all parallel agents to complete: `researcher_similar`, `researcher_techstack`, `researcher_pitfalls`

### CEO Review — Research

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/strategy/research-pitfalls.md`, `.factory/strategy/research-similar.md`, `.factory/strategy/research-techstack.md`
3. Assess: Is the research relevant? Does it cover the technology landscape adequately? Check for gaps in similar projects, tech stack analysis, and pitfall coverage.
4. Write verdict to `.factory/reviews/ceo-verdict-research.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival
