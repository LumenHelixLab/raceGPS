# raceGPS + Graphify Knowledge Graph Integration Plan

> For Hermes: this is a plan-mode document only. Do not implement until the user approves one option.

Goal: reduce cold-start repo re-reading by building a persistent knowledge graph for raceGPS and later extending the same pattern to the user’s other projects.

Architecture: treat Graphify as a graph-construction engine, not as a replacement for source control or test verification. The graph should summarize architecture, file ownership, systems, roadmap state, and cross-file relationships; Hermes should query the graph first, then drill into exact files only when execution or verification is needed.

Tech stack: Graphify (Python CLI / MCP mode), raceGPS repo docs/plans, optional Obsidian/wiki export, Hermes session workflow.

---

## Current raceGPS re-entry snapshot

Verified from the live repo on 2026-06-10:
- active repo: `D:/projects/racegps`
- current uncommitted work exists across Unreal gameplay/UI source, generated level spec files, installer files, and tests
- latest 5 commits show heavy recent product work: menu/save integration, CityHub, UI/docs, audio, gameplay systems
- prior local plan docs already conclude:
  - Milestone 2 (premium menu pass) = repo-side complete
  - Milestone 3 (onboarding completion flow) = repo-side complete
  - Milestone 1 (first-drive proof) = blocked on real Unreal Editor world creation and PIE verification

This means the graph should not be a generic repo index. It should become a project memory layer for:
- milestone state
- system relationships
- authoritative docs/plans
- generated artifact lineage
- exact blockers and next actions

---

## What Graphify appears to provide

Verified from the upstream README / metadata:
- repo: `safishamsi/graphify`
- primary language: Python
- license: MIT
- supports code, markdown, PDFs, images
- outputs persistent `graph.json`, `GRAPH_REPORT.md`, `graph.html`, optional `wiki/`, optional `obsidian/`
- supports incremental updates via cache and `--update`
- can run as MCP via `--mcp`
- strong fit for persistent cross-session summarization

Known caveat:
- Graphify is designed first as a Claude Code skill/CLI. We should assume some workflow adaptation will be needed for Hermes usage unless we treat it purely as an external artifact generator.

---

## Top 3 integration ideas

## Idea 1 — Passive project brain (recommended first)

Summary: run Graphify against `D:/projects/racegps`, commit the output under a dedicated project folder, and make Hermes consult the exported wiki/report before broad repo scans.

Why this is strong:
- lowest risk
- no runtime coupling to Hermes internals
- immediately useful for raceGPS re-entry
- preserves a human-auditable artifact in the repo

Suggested layout:
- `D:/projects/racegps/.graphify/graph.json`
- `D:/projects/racegps/.graphify/GRAPH_REPORT.md`
- `D:/projects/racegps/.graphify/wiki/`
- `D:/projects/racegps/.graphify/obsidian/` (optional)
- `D:/projects/racegps/docs/plans/graph-usage.md` (human instructions)

Hermes workflow:
1. On project resume, read `.graphify/GRAPH_REPORT.md`
2. Read one or two wiki pages for the requested subsystem
3. Only then open exact source files/tests for execution

Best use cases:
- "where did we leave off?"
- "what systems touch onboarding?"
- "what depends on the level spec generator?"
- "what changed around menu/save/onboarding?"

Effort: Small
Risk: Low
Payoff: High

Approval outcome if chosen:
- install/validate Graphify locally
- generate first raceGPS graph
- add a short repo-local re-entry workflow doc

---

## Idea 2 — Graph-backed plan mode + milestone navigator

Summary: use Graphify output as input to a raceGPS-specific project map that turns the repo into a milestone knowledge base, not just a code graph.

This would layer a curated navigation surface on top of Graphify:
- milestone nodes: M1 first-drive proof, M2 premium menu, M3 onboarding, etc.
- system nodes: vehicle, menu, onboarding, world loader, installer, CityHub
- artifact nodes: docs, tests, generated JSON, content assets, installer outputs
- blocker nodes: missing `AkronWorld.umap`, missing UE/MSBuild on this machine
- evidence edges: tests, commits, docs, generated outputs, known blockers

Why this is strong:
- best fit for how you actually manage projects: milestone-based, go/no-go, premium execution
- lets Hermes answer planning questions without recomputing context from scratch
- converts "repo memory" into product/program memory

Likely implementation pattern:
- generate Graphify base graph
- add a thin post-processor script that injects curated milestone metadata from:
  - `docs/plans/*.md`
  - key READMEs
  - selected test files
  - optional git metadata
- export a `PROJECT_STATE.md` and/or `MILESTONE_GRAPH.json`

Best use cases:
- "what is Phase A blocked on?"
- "show me every artifact tied to Milestone 1"
- "what still needs real Unreal verification vs repo-side completion?"

Effort: Medium
Risk: Medium
Payoff: Very High

Approval outcome if chosen:
- build Graphify output plus a raceGPS-specific enrichment layer
- produce a milestone navigator artifact in the repo

---

## Idea 3 — Shared multi-project knowledge graph service for Hermes

Summary: create a reusable project-brain pattern across raceGPS, HelixForge, lookBOOK, and PromptPack so Hermes can query a local graph cache before reading repos or depending on session memory.

This would move beyond raceGPS into a local command-center layer:
- one graph per project
- normalized metadata schema across projects
- optional MCP service or local query script
- project-specific wiki exports
- refresh hooks on commit or manual update

Why this is powerful:
- gives you a durable, local-first memory substrate across all active projects
- reduces repeated repo onboarding cost every session
- supports future portfolio-level planning and dependency mapping

Why I would not start here first:
- highest complexity
- requires schema decisions early
- more likely to become infrastructure before proving value on raceGPS

Best use cases:
- "what was the last validated milestone across all projects?"
- "which project already solved X pattern?"
- "what files/docs should Hermes read first for project Y?"

Effort: Large
Risk: Medium-High
Payoff: Strategic / portfolio-level

Approval outcome if chosen:
- define common graph storage layout outside any single repo
- build a small query layer for Hermes-facing re-entry
- then onboard projects one by one

---

## My recommendation

Top recommendation order:
1. Idea 1 now
2. Idea 2 immediately after Idea 1 proves useful
3. Idea 3 only after the raceGPS pattern works cleanly

Reason:
- Idea 1 gets value fast with almost no lock-in
- Idea 2 matches your milestone/go-no-go operating style and is probably the long-term winner for raceGPS specifically
- Idea 3 is the command-center version, but it should be earned after one project proves the pattern

---

## Proposed execution phases if approved

### Phase 1 — Validate Graphify on raceGPS
- install Graphify in this environment
- run it on `D:/projects/racegps`
- inspect output quality on code + docs + plans
- confirm whether it handles the repo size and mixed Unreal/Python/docs structure well

### Phase 2 — Create raceGPS re-entry workflow
- document which Graphify artifacts Hermes should consult first
- define a minimal query checklist for resume / plan mode
- decide what belongs in graph output vs source-of-truth files

### Phase 3 — Optional enrichment
- inject milestones, blockers, and verification evidence as structured overlays
- add a small updater script or commit hook

---

## Approval choices

A. Approve Idea 1 only
B. Approve Idea 1 + pre-design Idea 2
C. Approve Idea 2 directly
D. Approve Idea 3 architecture work

My advice: choose B.
