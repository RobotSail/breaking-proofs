---
name: workflow-skill-refine
description: "Verified skill generation pipeline — templatize, review, guard, split. Converts Pydantic workflow graphs into verified SKILL.md files with annotations. Use to regenerate skills after workflow definition changes."
disable-model-invocation: true
argument-hint: "<project_path>"
---

# Skill Refine Workflow

The user wants: **$ARGUMENTS**

## Step: Dag Sort

Dump the workflow DAG in topological order. Must run first to provide node ordering for templatization.

```bash
factory workflow show $PROJECT_PATH
```

## Step: Templatize

Convert the workflow graph into a templatized SKILL.md with slot markers for the reviewer to refine.

```bash
factory workflow export-skills --templatize $PROJECT_PATH
```

## Phase 1: Skill Reviewer — Review Agent

```bash
factory agent skill_reviewer --task "Review and refine the templatized skill document. You may ONLY modify values inside double-brace slot markers (format: name::default). Do NOT change any text outside markers, annotations, or structure. Use the provided context bundle (agent prompts, CLI docs, edge topology) to make informed improvements to timeouts, task prompts, gate prompts, failure actions, and finalize commands.
Read: .factory/strategy/templatized-skill.md
Write output to: .factory/strategy/refined-skill.md" --project "$PROJECT_PATH" --timeout 600
```

```bash
# Artifact verification: review_agent
_vfail=0
_f="$PROJECT_PATH/.factory/strategy/refined-skill.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: review_agent: .factory/strategy/refined-skill.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: review_agent: .factory/strategy/refined-skill.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=review_agent" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: review_agent artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=review_agent" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

### Gate — Guard (Automated)

**MANDATORY:** Wait for the preceding agent to finish, then run this check BEFORE spawning the next agent. Do NOT run agents in parallel across this gate.

```bash
python3 -c "from factory.workflow.guard import check; from pathlib import Path; s = Path('$PROJECT_PATH/.factory/strategy/templatized-skill.md').read_text(); r = Path('$PROJECT_PATH/.factory/strategy/refined-skill.md').read_text(); result = check(s, r); print(result.verdict)"
```

- **PROCEED** (exit 0 / no FAIL in output) → continue to `split`
- **HALT** (exit non-zero / FAIL in output) → do NOT spawn `split`. Skip to the next CEO review gate or finalize as error.

*On RELOOP: return to `review_agent` (max 3 iterations)*

## Step: Split

Split the guard-approved refined skill into clean SKILL.md and SKILL.annotations.yaml.

```bash
factory workflow export-skills --split $PROJECT_PATH
```
