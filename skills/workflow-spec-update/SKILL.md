---
name: workflow-spec-update
description: "Run the spec-update workflow."
disable-model-invocation: true
argument-hint: "<project_path>"
---

# Spec Update Workflow

The user wants: **$ARGUMENTS**

## Step: Graph Update

Refresh the code knowledge graph with latest source changes before scoping the diff.

```bash
factory graph update $PROJECT_PATH
```

## Step: Diff Scope

Map git diff to affected spec modules. Must run first to scope the patch for the spec patcher.

```bash
factory spec scope $PROJECT_PATH
```

## Phase 1: Researcher — Patch

```bash
factory agent researcher --task "Patch the repo spec based on scoped changes. Read the spec_patcher prompt at factory/agents/prompts/spec_patcher.md. Read .factory/spec_update_scope.md for the list of affected modules and new files. Read SPEC.md for the current spec. Read changed source files and update affected module behavioral contracts. Add new module entries for unmapped files. Remove modules whose paths no longer exist. Write updated spec to SPEC.md.
Read: .factory/spec_update_scope.md
Write output to: SPEC.md" --project "$PROJECT_PATH" --timeout 600
```

```bash
# Artifact verification: patch
_vfail=0
_f="$PROJECT_PATH/SPEC.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: patch: SPEC.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: patch: SPEC.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=patch" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: patch artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=patch" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

### CEO Review — Patch

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/spec_update_scope.md`, `SPEC.md`
3. Assess: Review the patched spec at SPEC.md. Check: do updates match the diff scope? Were all affected modules touched? Were new files mapped to modules? Were deleted modules removed? PROCEED if updates are reasonable. RELOOP to patch if issues.
4. Write verdict to `.factory/reviews/ceo-verdict-patch.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `patch` (max 3 iterations)*

## Step: Revalidate

Re-validate the spec after patching to catch regressions. Output feeds the final CEO quality gate.

```bash
factory spec validate $PROJECT_PATH
```

### CEO Review — Revalidate

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/spec_validation.md`
3. Assess: Final quality gate for the updated spec. Read .factory/spec_validation.md. If validation errors exist, RELOOP to patch for fixes. PROCEED if the spec passes validation.
4. Write verdict to `.factory/reviews/ceo-verdict-revalidate.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `patch` (max 3 iterations)*
