---
name: workflow-review
description: "Review mode — verify eval dimensions work, create factory.md, and run baseline eval. Use when the project state is evals_pending_review. Tests all dimensions, marks the profile as reviewed, initializes the factory store, and runs E2E verification."
disable-model-invocation: true
argument-hint: "<project_path>"
---

# Review Workflow

The user wants: **$ARGUMENTS**

## Step: Eval Test

Run the eval harness to test all discovered dimensions. Output is reviewed by the CEO gate to catch broken dimensions.

```bash
cd $PROJECT_PATH && python eval/score.py
```

### CEO Review — Eval

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/reviews/eval-test-latest.md`
3. Assess: Check eval output. Did all dimensions pass? If any dimension failed, dispatch the Builder to fix it (install missing tool, adjust command, remove broken dimension). PROCEED only when all dimensions produce valid scores.
4. Write verdict to `.factory/reviews/ceo-verdict-eval.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `eval_test` (max 3 iterations)*

## Step: Mark Reviewed

Mark the eval profile as human-reviewed by setting the human_reviewed flag. Must run after the CEO approves all dimensions.

```bash
python3 -c "import json; from pathlib import Path; p = Path('$PROJECT_PATH/.factory/eval_profile.json'); d = json.loads(p.read_text()); d['human_reviewed'] = True; p.write_text(json.dumps(d, indent=2))"
```

## Phase 1: Ceo — Create Factory Md

```bash
factory agent ceo --task "Create factory.md from template. Copy the factory config template to the project root. Fill in: Goal, Scope, Guards, Eval command, Threshold, and Smoke Test. If .factory/eval_spec.json exists, populate the Eval Spec section. If .factory/strategy/current.md has a Research Configuration section, populate research sections (Research Target, Mutable/Fixed Surfaces, etc.).
Read: .factory/eval_profile.json
Write output to: factory.md" --project "$PROJECT_PATH" --timeout 3600
```

```bash
# Artifact verification: create_factory_md
_vfail=0
_f="$PROJECT_PATH/factory.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: create_factory_md: factory.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: create_factory_md: factory.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=create_factory_md" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: create_factory_md artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=create_factory_md" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

## Step: Factory Init

Parse factory.md and generate .factory/config.json. Must run after factory.md is created.

```bash
factory init $PROJECT_PATH
```

## Step: Baseline Eval

Run the first full eval after factory initialization to establish a baseline score.

```bash
factory eval $PROJECT_PATH
```

## Step: Commit

Commit the factory setup artifacts (factory.md, eval/score.py, .factory/) to git. Must run after baseline eval.

```bash
cd $PROJECT_PATH && git add factory.md eval/score.py .factory/ && git commit -m "factory: initialize factory config and baseline eval"
```

### CEO Review — E2E

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/config.json`, `factory.md`
3. Assess: E2E verification gate. Verify the project runs end-to-end. Check the Smoke Test command in factory.md and run it. If this is a pre-existing project entering the factory for the first time, it MUST be verified before transitioning to Improve mode.
4. Write verdict to `.factory/reviews/ceo-verdict-e2e.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival
