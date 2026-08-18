---
name: workflow-doc-update
description: "Run the doc-update workflow."
disable-model-invocation: true
argument-hint: "<project_path>"
---

# Doc Update Workflow

The user wants: **$ARGUMENTS**

## Step: Diff Scope

Map git diff to affected documentation files. Must run first to scope the update for the patcher agent.

```bash
python3 -c "import subprocess, re, sys; from pathlib import Path; changed = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD~1'], text=True).strip().splitlines(); doc_files = [f for f in Path('$PROJECT_PATH').rglob('*.md')]; affected = []; [affected.append(str(d)) for d in doc_files for c in changed if c in d.read_text()]; scope = '# Doc Update Scope\n\n## Changed source files\n' + '\n'.join(f'- {{f}}' for f in changed) + '\n\n## Affected doc files\n' + '\n'.join(f'- {{f}}' for f in set(affected)); Path('$PROJECT_PATH/.factory/doc_update_scope.md').write_text(scope); print('PROCEED')"
```

## Phase 1: Researcher — Patch Docs

```bash
factory agent researcher --task "Read the scoped changes at .factory/doc_update_scope.md. Update only the affected documentation sections. Targeted updates only — do not rewrite entire files.
Read: .factory/doc_update_scope.md
Write output to: CLAUDE.md, README.md, docs/" --project "$PROJECT_PATH" --timeout 600
```

```bash
# Artifact verification: patch_docs
_vfail=0
_f="$PROJECT_PATH/CLAUDE.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: patch_docs: CLAUDE.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: patch_docs: CLAUDE.md is empty" && _vfail=1
_f="$PROJECT_PATH/README.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: patch_docs: README.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: patch_docs: README.md is empty" && _vfail=1
_f="$PROJECT_PATH/docs/"
[ ! -f "$_f" ] && echo "VERIFY FAIL: patch_docs: docs/ missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: patch_docs: docs/ is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=patch_docs" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: patch_docs artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=patch_docs" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

### CEO Review — Patch

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/doc_update_scope.md`
3. Assess: Check that documentation patches match the diff scope. Were all affected doc files touched? Do the updates accurately reflect the source changes? RELOOP if patches are incomplete or inaccurate.
4. Write verdict to `.factory/reviews/ceo-verdict-patch.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `patch_docs` (max 3 iterations)*

## Step: Revalidate

Re-validate file references after doc patches. Prints PROCEED or FAIL with missing paths.

```bash
python3 -c "import re, sys; from pathlib import Path; errors = []; scope = Path('$PROJECT_PATH/.factory/doc_update_scope.md'); [errors.append(f'missing: {{p}}') for p in re.findall(r'`([^`]+\.(?:py|md|yaml|toml|json))`', scope.read_text()) if not Path('$PROJECT_PATH/' + p).exists()]; print('PROCEED' if not errors else 'FAIL: ' + '; '.join(errors[:10]))"
```

### CEO Review — Revalidate

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/doc_update_scope.md`
3. Assess: Final quality gate for documentation updates. Review validation results and confirm patches are correct. PROCEED if all references are valid. RELOOP if issues remain.
4. Write verdict to `.factory/reviews/ceo-verdict-revalidate.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `revalidate` (max 3 iterations)*
