---
name: workflow-frontend-design-discover
description: "Design system extraction — discovers the project's design system and produces human-readable, editable artifacts. Runs 5 parallel researchers (tokens, components, patterns, UX, infrastructure) then synthesizes into design-baseline.json and rules.md. Run this once to establish the design system, review and edit the output, then use frontend-design (build) mode for each new feature without re-running researchers. Supports external design system URLs via --focus for cross-referencing (e.g., 'https://ux.redhat.com/'). Use when the user says 'discover design system', 'extract design system', or wants to establish design rules before building features."
disable-model-invocation: true
argument-hint: "<project_path>"
---

# Frontend Design Discover Workflow

The user wants: **$ARGUMENTS**

## Phase 1: Discover Research (Parallel)

Spawn 5 agents in parallel:

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
factory agent researcher --review-tag infra --task "Infrastructure context research. Discover the backend deployment architecture by reading Dockerfile, docker-compose.yml, k8s/ manifests, and Helm charts. Identify what environment the backend runs in (container, K8s pod, VM, serverless) and what system tools are available inside the container. Examine the backend API architecture: framework (FastAPI, Flask, etc.), router registration pattern, how new endpoints are added, existing endpoint inventory. Map resource access patterns: how the backend reaches external resources — K8s API via in-cluster config, SSH backends, database connections, external APIs. Document data sources: where data comes from (K8s node resources, subprocess calls, database queries, external APIs) and which client libraries are available. Write to .factory/design-system/infra-context.md.
Write output to: .factory/design-system/infra-context.md" --project "$PROJECT_PATH" --timeout 600 &
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

# Artifact verification: researcher_infra
_vfail=0
_f="$PROJECT_PATH/.factory/design-system/infra-context.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: researcher_infra: .factory/design-system/infra-context.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: researcher_infra: .factory/design-system/infra-context.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=researcher_infra" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: researcher_infra artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=researcher_infra" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(post-barrier harness verification — DO NOT SKIP)*

## Barrier: Discover Research

Wait for all parallel agents to complete: `researcher_tokens`, `researcher_components`, `researcher_patterns`, `researcher_ux`, `researcher_infra`

Read combined outputs: `.factory/design-system/component-inventory.md`, `.factory/design-system/infra-context.md`, `.factory/design-system/pattern-library.md`, `.factory/design-system/token-audit.md`, `.factory/design-system/ux-patterns.md`

### CEO Review — Discover Research

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/design-system/component-inventory.md`, `.factory/design-system/infra-context.md`, `.factory/design-system/pattern-library.md`, `.factory/design-system/token-audit.md`, `.factory/design-system/ux-patterns.md`
3. Assess: Verify all five design research artifacts exist and are substantive. token-audit.md must list actual CSS custom properties. component-inventory.md must list actual .tsx files with component names. pattern-library.md must describe actual page layout patterns. ux-patterns.md must describe actual animation, hierarchy, or UX patterns. infra-context.md must describe the deployment environment and backend API architecture. RELOOP if any artifact is empty or clearly fabricated. PROCEED if all five have real data.
4. Write verdict to `.factory/reviews/ceo-verdict-discover-research.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `fork_discover_research` (max 3 iterations)*

## Phase 2: Strategist — Design Auditor

```bash
factory agent strategist --task "Design system auditor (discover mode). Read .factory/design-system/token-audit.md, component-inventory.md, pattern-library.md, ux-patterns.md, and infra-context.md. Synthesize into two outputs: (1) .factory/design-system/design-baseline.json — valid JSON with token_registry, component_inventory, pattern_library, ux_patterns, and infrastructure keys. The infrastructure key must include: deployment (type, orchestrator), container_capabilities (available and unavailable tools), resource_access (how the backend reaches external resources), api_architecture (framework, router pattern, existing endpoints), and data_sources (where data comes from). Extract actual values from the research, do not fabricate. (2) .factory/design-system/rules.md — HARD RULES section (token purity, font family, component wrappers, dark mode parity, accessibility floor, infrastructure fidelity — no unavailable system tools, use established resource access patterns, follow API registration pattern) and SOFT GUIDELINES section (spacing, border-radius, motion choreography, icons, page structure, status colors, information hierarchy, user-friendliness). If previous design-baseline.json exists, merge and flag drift. Preserve any existing MANUAL OVERRIDES section in rules.md. This is a discover-only run — the design system files will be reviewed and edited by a human designer before feature builds.
Read: .factory/design-system/component-inventory.md, .factory/design-system/infra-context.md, .factory/design-system/pattern-library.md, .factory/design-system/token-audit.md, .factory/design-system/ux-patterns.md
Write output to: .factory/design-system/design-baseline.json, .factory/design-system/rules.md" --project "$PROJECT_PATH" --timeout 600
```

```bash
# Artifact verification: design_auditor
_vfail=0
_f="$PROJECT_PATH/.factory/design-system/design-baseline.json"
[ ! -f "$_f" ] && echo "VERIFY FAIL: design_auditor: .factory/design-system/design-baseline.json missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: design_auditor: .factory/design-system/design-baseline.json is empty" && _vfail=1
_f="$PROJECT_PATH/.factory/design-system/rules.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: design_auditor: .factory/design-system/rules.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: design_auditor: .factory/design-system/rules.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=design_auditor" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: design_auditor artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=design_auditor" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

### CEO Review — Discover Audit

Apply the CEO Review Gate protocol:
1. Read the agent output for the preceding step
2. Read artifacts: `.factory/design-system/design-baseline.json`, `.factory/design-system/rules.md`
3. Assess: Verify design-baseline.json is valid JSON with token_registry, component_inventory, and pattern_library keys. Verify rules.md contains both HARD RULES and SOFT GUIDELINES sections. RELOOP if malformed. PROCEED if structurally valid.
4. Write verdict to `.factory/reviews/ceo-verdict-discover-audit.md`
5. **PROCEED** → continue to next step
6. **REDIRECT** → re-invoke the preceding agent with corrections (max 2)
7. **ABORT** → log failure and skip to archival

*On RELOOP: return to `design_auditor` (max 3 iterations)*

## Phase 3: Archivist Discover

```bash
factory agent archivist --task "Archive the design system discovery results. Note which artifacts were produced and summarize the design system for future reference. The user should review and edit the design system files before running feature builds.
Read: .factory/design-system/design-baseline.json, .factory/design-system/rules.md
Write output to: .factory/archive/design-discover.md" --project "$PROJECT_PATH" --timeout 300 --model haiku &
```
*(fire-and-forget — CEO continues immediately)*
