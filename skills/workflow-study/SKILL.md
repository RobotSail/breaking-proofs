---
name: workflow-study
description: "Codebase structure and dependency graph analysis. Updates the code knowledge graph, runs factory study for observations, then explores the graph for structural insights via an agent. Terminal mode — does not chain to other modes. Use when the user says 'study', 'analyze codebase', or wants a structural understanding of the project before planning work."
disable-model-invocation: true
argument-hint: "<project_path>"
---

# Study Workflow

The user wants: **$ARGUMENTS**

## Step: Graph Update

Extract or incrementally update the code knowledge graph before study.

```bash
factory graph update $PROJECT_PATH
```

## Phase 1: Observe

Run local study to gather observations:

```bash
factory study $PROJECT_PATH
```

Writes observations to `.factory/strategy/observations.md`.

## Phase 2: Researcher — Graph Explorer

```bash
factory agent researcher --task "Explore the project's code knowledge graph to build structural understanding. Read .factory/strategy/observations.md for focus context.

If graphify is installed and graph.json exists:
1. Run `factory graph query "<focus from observations>" --depth 2` to find relevant nodes
2. Run `factory graph explain "<key node>"` on the most important nodes to understand their connections and dependencies
3. Run `factory graph path "<A>" "<B>"` to trace dependency paths between key components
4. Write structured findings to .factory/strategy/graph-context.md covering: key modules and their relationships, dependency paths, architectural layers, entry points and hotspots

If graphify is NOT installed or graph.json is missing, fall back to direct file exploration:
1. Use `find . -name '*.py' | head -50` to discover source files
2. Use `grep -rn 'class \|def ' --include='*.py' | head -100` to map functions and classes
3. Use `grep -rn 'import ' --include='*.py' | head -100` to trace dependencies
4. Write the same structured findings to .factory/strategy/graph-context.md
Read: .factory/strategy/observations.md
Write output to: .factory/strategy/graph-context.md" --project "$PROJECT_PATH" --timeout 600
```

```bash
# Artifact verification: graph_explorer
_vfail=0
_f="$PROJECT_PATH/.factory/strategy/graph-context.md"
[ ! -f "$_f" ] && echo "VERIFY FAIL: graph_explorer: .factory/strategy/graph-context.md missing" && _vfail=1
[ -f "$_f" ] && [ ! -s "$_f" ] && echo "VERIFY FAIL: graph_explorer: .factory/strategy/graph-context.md is empty" && _vfail=1
[ "$_vfail" -ne 0 ] && echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_FAIL node=graph_explorer" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt" && exit 1
echo "VERIFY OK: graph_explorer artifacts validated"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) VERIFY_OK node=graph_explorer" >> "$PROJECT_PATH/.factory/hooks/hook-log.txt"
```
*(harness verification — DO NOT SKIP)*

## Step: Concat Study

```bash
cat $PROJECT_PATH/.factory/strategy/observations.md $PROJECT_PATH/.factory/strategy/graph-context.md > $PROJECT_PATH/.factory/strategy/study-combined.md
```
