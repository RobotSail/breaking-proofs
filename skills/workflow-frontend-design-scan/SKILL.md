---
name: workflow-frontend-design-scan
description: "Continuous design health monitoring — scans the entire codebase for design system drift without building anything. Researches tokens, components, patterns, and UX quality, then runs all design check scripts against every source file. Produces a structured health report with per-dimension scores and trend data. Designed for use with --loop for hourly continuous scanning. Use when the user says 'scan for design drift', 'check design health', or wants passive design consistency monitoring."
disable-model-invocation: true
argument-hint: "<project_path>"
---

# Frontend Design Scan Workflow

The user wants: **$ARGUMENTS**

## Phase 1: Scan Research (Parallel)

Spawn 4 agents in parallel:

```bash
factory agent researcher --review-tag tokens --task "Design token research. Find the project's main CSS/theme files (index.css, globals.css, theme.ts, tailwind.config, etc.). Extract every color token, CSS custom property, and theme variable with values for all theme modes. Search all component files for hardcoded color values (hex, rgb, hsl) that bypass the token system. Count frequencies. Document the font families, spacing scale, and border-radius tiers. Write to .factory/design-system/token-audit.md.
Write output to: .factory/design-system/token-audit.md" --project "$PROJECT_PATH" --timeout 600 &
```

```bash
factory agent researcher --review-tag components --task "Component inventory research. Find the project's component library directory and catalog every shared component — names, props, variant systems. Identify the primitive UI library (Radix, MUI, Chakra, Headless UI, etc.) and which components wrap it. List feature-specific components. Document UI dependencies from package.json. Map composition patterns. Write to .factory/design-system/component-inventory.md.
Write output to: .factory/design-system/component-inventory.md" --project "$PROJECT_PATH" --timeout 600 &
```

```bash
factory agent researcher --review-tag patterns --task "Layout and pattern research. Read layout.tsx, router.tsx, and every page.tsx in feature modules. Document the shell structure, page templates, data-fetching patterns (e.g. TanStack Query, SWR, Apollo, RTK Query), state management (e.g. Zustand, Redux, Pinia, Context), error handling, motion/animation vocabulary, and accessibility patterns. Write to .factory/design-system/pattern-library.md.
Write output to: .factory/design-system/pattern-library.md" --project "$PROJECT_PATH" --timeout 600 &
```

```bash
factory agent researcher --review-tag ux --task "UX quality research. Analyze the project's experiential layer: animation choreography (stagger timing, easing curves, entrance sequences, coordinated transitions, duration scale, exit animations, loading states), information hierarchy (heading structure, visual weight, content density, progressive disclosure, data presentation for non-technical users), and user-friendliness patterns (plain language, contextual help, onboarding/empty states, error messages, feedback patterns). Write to .factory/design-system/ux-patterns.md.
Write output to: .factory/design-system/ux-patterns.md" --project "$PROJECT_PATH" --timeout 600 &
```

```bash
wait
```

**Important:** Run ALL commands above in a **single** Bash tool call with timeout set to at least 600 seconds.

```bash
# Artifact verification: researcher_tokens
_vfail=0
_f="$PROJECT_PATH/.factory/design-system/token-audit.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: researcher_tokens: .factory/design-system/token-audit.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: researcher_tokens: .factory/design-system/token-audit.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=researcher_tokens" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: researcher_tokens artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=researcher_tokens" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"

# Artifact verification: researcher_components
_vfail=0
_f="$PROJECT_PATH/.factory/design-system/component-inventory.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: researcher_components: .factory/design-system/component-inventory.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: researcher_components: .factory/design-system/component-inventory.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=researcher_components" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: researcher_components artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=researcher_components" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"

# Artifact verification: researcher_patterns
_vfail=0
_f="$PROJECT_PATH/.factory/design-system/pattern-library.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: researcher_patterns: .factory/design-system/pattern-library.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: researcher_patterns: .factory/design-system/pattern-library.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=researcher_patterns" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: researcher_patterns artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=researcher_patterns" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"

# Artifact verification: researcher_ux
_vfail=0
_f="$PROJECT_PATH/.factory/design-system/ux-patterns.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: researcher_ux: .factory/design-system/ux-patterns.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: researcher_ux: .factory/design-system/ux-patterns.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=researcher_ux" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: researcher_ux artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=researcher_ux" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(post-barrier harness verification — DO NOT SKIP)*

## Barrier: Scan Research

Wait for all parallel agents to complete: `researcher_tokens`, `researcher_components`, `researcher_patterns`, `researcher_ux`

Read combined outputs: `.factory/design-system/component-inventory.md`, `.factory/design-system/pattern-library.md`, `.factory/design-system/token-audit.md`, `.factory/design-system/ux-patterns.md`

## Phase 2: Strategist — Scan Auditor

```bash
factory agent strategist --task "Design system auditor (scan mode). Read all four research files: token-audit.md, component-inventory.md, pattern-library.md, and ux-patterns.md. Synthesize into design-baseline.json and rules.md. If previous design-baseline.json exists, diff and report drift. This is a scan-only run — no features will be built.
Read: .factory/design-system/component-inventory.md, .factory/design-system/pattern-library.md, .factory/design-system/token-audit.md, .factory/design-system/ux-patterns.md
Write output to: .factory/design-system/design-baseline.json, .factory/design-system/rules.md" --project "$PROJECT_PATH" --timeout 600
```

```bash
# Artifact verification: scan_auditor
_vfail=0
_f="$PROJECT_PATH/.factory/design-system/design-baseline.json"
[ ! -f "$_f" ] && echo "VERIFY FAIL: scan_auditor: .factory/design-system/design-baseline.json missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: scan_auditor: .factory/design-system/design-baseline.json is empty" && _vfail=1
_f="$PROJECT_PATH/.factory/design-system/rules.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: scan_auditor: .factory/design-system/rules.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: scan_auditor: .factory/design-system/rules.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=scan_auditor" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: scan_auditor artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=scan_auditor" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

## Phase 3: Scan Checks (Parallel)

Spawn 6 agents in parallel:

```bash
cd $PROJECT_PATH && SCAN_MODE=full bash .factory/design-system/checks/check-token-purity.sh --score
```

```bash
cd $PROJECT_PATH && SCAN_MODE=full bash .factory/design-system/checks/check-dark-mode.sh --score
```

```bash
cd $PROJECT_PATH && SCAN_MODE=full bash .factory/design-system/checks/check-a11y-baseline.sh --score
```

```bash
cd $PROJECT_PATH && SCAN_MODE=full bash .factory/design-system/checks/check-component-import.sh --score
```

```bash
cd $PROJECT_PATH && SCAN_MODE=full bash .factory/design-system/checks/check-font-family.sh --score
```

```bash
cd $PROJECT_PATH && SCAN_MODE=full bash .factory/design-system/checks/check-patterns.sh --score
```

```bash
wait
```

## Barrier: Scan Checks

Wait for all parallel agents to complete: `check_token_purity`, `check_dark_mode`, `check_a11y`, `check_component_import`, `check_font_family`, `check_patterns`

## Phase 4: Strategist — Health Report Writer

```bash
factory agent strategist --task "Design health report writer. Read the output of all 6 design check scripts and the design-baseline.json. Produce .factory/design-system/health-report.json with overall_score (0.0-1.0), per-dimension scores (token_purity, dark_mode_coverage, accessibility, component_wrapping, font_compliance, pattern_adherence), issue counts, top issues list, trend data (compare with previous report if exists), and actionable recommendations.
Read: .factory/design-system/design-baseline.json
Write output to: .factory/design-system/health-report.json" --project "$PROJECT_PATH" --timeout 600
```

```bash
# Artifact verification: health_report_writer
_vfail=0
_f="$PROJECT_PATH/.factory/design-system/health-report.json"
[ ! -f "$_f" ] && echo "VERIFY FAIL: health_report_writer: .factory/design-system/health-report.json missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: health_report_writer: .factory/design-system/health-report.json is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=health_report_writer" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: health_report_writer artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=health_report_writer" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

## Phase 5: Archivist Scan

```bash
factory agent archivist --task "Archive the design scan results and health report.
Read: .factory/design-system/health-report.json
Write output to: .factory/archive/design-scan.md" --project "$PROJECT_PATH" --timeout 300 --model haiku &
```
*(fire-and-forget — CEO continues immediately)*
