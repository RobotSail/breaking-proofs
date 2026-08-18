---
name: workflow-doc-generate
description: "Run the doc-generate workflow."
disable-model-invocation: true
argument-hint: "<project_path>"
---

# Doc Generate Workflow

The user wants: **$ARGUMENTS**

## Phase 1: Researcher — Scan Project

```bash
factory agent researcher --task "Scan the codebase for documentable surfaces. Identify public APIs, CLI commands, configuration options, architecture patterns, and entry points. Write a complete inventory to .factory/doc_scan.md.
Write output to: .factory/doc_scan.md" --project "$PROJECT_PATH" --timeout 600
```

```bash
# Artifact verification: scan_project
_vfail=0
_f="$PROJECT_PATH/.factory/doc_scan.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: scan_project: .factory/doc_scan.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: scan_project: .factory/doc_scan.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=scan_project" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: scan_project artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=scan_project" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

### CEO Review — Scan

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/doc_scan.md`
3. Assess: Check scan completeness. Are all major documentable surfaces identified? Public APIs, CLI commands, config options, architecture, and entry points should all be covered. RELOOP if significant surfaces are missing.
4. Write verdict to `.factory/reviews/ceo-verdict-scan.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `scan_project` (max 3 iterations)*

## Phase 2: Researcher — Generate Docs

```bash
factory agent researcher --task "Generate or update documentation files based on the scan inventory at .factory/doc_scan.md. Update README.md, CLAUDE.md, and docs/ files as needed. Ensure accuracy, completeness, and clear structure.
Read: .factory/doc_scan.md
Write output to: CLAUDE.md, README.md, docs/" --project "$PROJECT_PATH" --timeout 600
```

```bash
# Artifact verification: generate_docs
_vfail=0
_f="$PROJECT_PATH/CLAUDE.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: generate_docs: CLAUDE.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: generate_docs: CLAUDE.md is empty" && _vfail=1
_f="$PROJECT_PATH/README.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: generate_docs: README.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: generate_docs: README.md is empty" && _vfail=1
_f="$PROJECT_PATH/docs/"
[ ! -f "$_f" ] && echo "VERIFY FAIL: generate_docs: docs/ missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: generate_docs: docs/ is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=generate_docs" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: generate_docs artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=generate_docs" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

### CEO Review — Docs

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `CLAUDE.md`, `README.md`
3. Assess: Review generated documentation. Is it accurate, complete, and well-structured? Do the docs match the scan inventory? RELOOP if documentation has gaps or inaccuracies.
4. Write verdict to `.factory/reviews/ceo-verdict-docs.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `generate_docs` (max 3 iterations)*

## Step: Validate Docs

Validate that all file references in the doc scan actually exist on disk. Prints PROCEED or FAIL with missing paths.

```bash
python3 -c "import re, sys; from pathlib import Path; errors = []; scan = Path('$PROJECT_PATH/.factory/doc_scan.md'); [errors.append(f'missing: {{p}}') for p in re.findall(r'`([^`]+\.(?:py|md|yaml|toml|json))`', scan.read_text()) if not Path('$PROJECT_PATH/' + p).exists()]; print('PROCEED' if not errors else 'FAIL: ' + '; '.join(errors[:10]))"
```

### CEO Review — Validate

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/doc_scan.md`
3. Assess: Final quality gate. Review validation results and overall documentation quality. PROCEED if all references are valid and docs are ready. RELOOP if issues remain.
4. Write verdict to `.factory/reviews/ceo-verdict-validate.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `validate_docs` (max 3 iterations)*
