---
name: graphify-project-first
description: Use when beginning work in an existing software project. Generate and inspect a Graphify architecture graph before diagnosis, planning, edits, or implementation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [graphify, architecture, codebase, discovery, planning]
    related_skills: [plan, systematic-debugging, test-driven-development]
---

# Graphify Project-First Discovery

## Overview

Graphify (`graphify`) creates a navigable codebase knowledge graph from local AST extraction: files, symbols, imports, calls, and communities. It produces `graph.json`, an interactive `graph.html`, and `GRAPH_REPORT.md` without an LLM when using `--code-only`.

Use the graph as the first architecture-discovery step on existing projects. It identifies entrypoints, hubs, dependency paths, and affected areas before changes are proposed or files are edited.

## When to Use

- Debugging, fixing, extending, reviewing, or refactoring an existing project.
- The task spans more than one source file or the architecture is not already known from this session.
- The user asks to understand a repository or create a dependency/architecture graph.

Do not block tiny, isolated edits (for example, a one-line correction in a file already fully understood) on a fresh full-project scan.

## Mandatory Tight Loop

1. **Discover Graphify and project root.**
   ```bash
   command -v graphify
   git -C <project> rev-parse --show-toplevel
   ```
   If `graphify` is unavailable, report the blocker and do normal lightweight code discovery; do not pretend a graph was created.

2. **Generate a local code graph before edits.**
   Put generated artifacts under the approved work area, never inside a source repository unless the user requests that location.
   ```bash
   graphify extract <project> --code-only --out /home/forget/QwertyWork/<project>-graph --max-workers 4
   graphify cluster-only /home/forget/QwertyWork/<project>-graph --no-label
   ```
   `--code-only` is the default for implementation tasks: it is deterministic, does not need an external model/API key, and avoids reading or sending sensitive documents. Use full semantic extraction only if the user asks for document/paper analysis and a configured backend is available.

3. **Read the graph report and inspect targeted structure.**
   ```bash
   graphify god-nodes --top 10 --graph <out>/graphify-out/graph.json
   graphify explain "<entrypoint-or-symbol>" --graph <out>/graphify-out/graph.json
   graphify affected "<changed-symbol>" --depth 2 --graph <out>/graphify-out/graph.json
   graphify path "<node-a>" "<node-b>" --graph <out>/graphify-out/graph.json
   ```
   Completion criterion: identify the relevant entrypoint(s), the owning modules, and the test/consumer surface before changing code.

4. **Make the smallest justified change.**
   Use graph findings to limit scope. Treat inferred edges as hypotheses and verify them in source before relying on them.

5. **Update the graph after structural edits.**
   ```bash
   graphify update <project>
   graphify cluster-only <project> --no-label
   ```
   If output was intentionally outside the project, rerun the extraction command from step 2. Completion criterion: graph artifacts reflect the final source tree and tests cover the changed path.

## Artifact Contract

A successful graph-first pass has all of:

- `<out>/graphify-out/graph.json`
- `<out>/graphify-out/GRAPH_REPORT.md`
- `<out>/graphify-out/graph.html`

Report the absolute artifact directory and concise evidence: node/edge/community counts plus the relevant hubs. Do not dump the whole JSON into chat.

## Useful Queries

| Need | Command |
|---|---|
| Entry points / architectural hubs | `graphify god-nodes --top 10 --graph <graph>` |
| What a symbol does and connects to | `graphify explain "Symbol" --graph <graph>` |
| Change impact | `graphify affected "Symbol" --depth 2 --graph <graph>` |
| Relationship between components | `graphify path "A" "B" --graph <graph>` |
| Natural-language graph traversal | `graphify query "question" --graph <graph>` |
| Browser visualization | Open `<out>/graphify-out/graph.html` |

## Common Pitfalls

1. **Assuming Graphify is Graphiti.** They are different tools. This workflow is for the installed `graphify` CLI, a local repository graph extractor.
2. **Running `extract` without `--code-only` when no model key is configured.** Docs/papers/images trigger semantic extraction and the run will stop for an API key. Start with `--code-only`.
3. **Stopping after `extract`.** Run `cluster-only --no-label` so `GRAPH_REPORT.md` and `graph.html` exist.
4. **Writing graph artifacts into the repository by accident.** Use `/home/forget/QwertyWork/<project>-graph` by default.
5. **Treating graph edges as proof.** AST edges are strong evidence; inferred/semantic edges still require source verification.
6. **Skipping re-indexing after structural changes.** Rebuild or update the graph before declaring architecture-sensitive work complete.

## Verification Checklist

- [ ] `graphify --version` ran successfully.
- [ ] Graph generated before source edits or diagnostic conclusions.
- [ ] `graph.json`, `GRAPH_REPORT.md`, and `graph.html` exist.
- [ ] Relevant hubs, entrypoints, and affected paths were inspected.
- [ ] Source verified any inferred relationship used for a decision.
- [ ] Graph regenerated after structural changes.
