---
name: workflow-parallel-improve
description: "Parallel improve mode — runs N hypotheses concurrently in isolated worktrees, then selects the best result. Use when the user says 'parallel improve', 'try multiple hypotheses', or wants tournament-style experimentation."
disable-model-invocation: true
argument-hint: "<project_path>"
---

# Parallel Improve Workflow

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
factory agent strategist --task "Generate prioritized hypotheses for PARALLEL execution. Read the backlog at .factory/strategy/backlog.md — clear as many items as possible. Read Hypothesis Budget from observations for constraints. Read CEO research review at .factory/reviews/ceo-verdict-researcher.md. Generate MULTIPLE independent hypotheses that can run concurrently. Each hypothesis must target different files/areas to avoid merge conflicts. Tag backlog items with **Backlog item:** and new items with **New:**. Write to .factory/strategy/current.md with each hypothesis under a ## Hypothesis N heading.
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
3. Assess: HARD GATE for parallel experiments. Check: Are hypotheses independent (target different files/areas)? Would merge conflicts be unlikely? Each specific enough to implement? Scoped to one PR each? Expected eval impact realistic? Follows FEEC priority? Write PLAN APPROVED with approved hypotheses.
4. Write verdict to `.factory/reviews/ceo-verdict-strategy.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `strategist` (max 3 iterations)*

## Phase 4: Experiments (Parallel Experiments)

Fork up to 3 parallel experiment branches, each in an isolated worktree:

For each hypothesis from the strategy:
1. Create an experiment worktree branching from the current commit
2. Run the experiment subgraph (`exp_begin` → `exp_eval`)
3. Each branch runs independently: begin → builder → QA → eval

All branches run concurrently. Results are collected at the barrier.

## Barrier: Experiments

Wait for all parallel agents to complete: `fork_experiments`

Read combined outputs: `.factory/parallel_results.json`

Write combined result to: `.factory/parallel_joined.json`

## Phase 5: Select Best Experiment

**Selection strategy: `best_score`**

Compare all completed experiment branches:
1. Read eval results from each branch's worktree
2. Select the branch with the highest composite score
3. Merge the winner's branch into the baseline
4. Mark losing experiments as `superseded`
5. Clean up all experiment worktrees

## Phase 6: Archivist

```bash
factory agent archivist --task "Archive parallel experiment tournament results. Record which hypotheses were tested, their scores, which one won and why, and learnings from losers.
Read: .factory/selection_result.json
Write output to: .factory/archive/experiment.md" --project "$PROJECT_PATH" --timeout 300 --model haiku &
```
*(fire-and-forget — CEO continues immediately)*
