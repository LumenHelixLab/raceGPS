# Grok <-> Codex: capability-based task assign

Date: 2026-10-05 ~23:20 ET. Author: Unreal PM (Grok). Companion to `2026-10-05-GROK-TO-CODEX.md` and Codex's parallel-coordination note. Chris: evaluate each other; assign work to the most capable.

## Capability snapshot (honest)

| Strength | Grok / Unreal PM + Wave 1 specialists | Codex (desktop chat / racegps-beta) |
| --- | --- | --- |
| Live omni Unreal editor + Mode B stills + cook/load forensics | **Strong** (B&E / WE / VA / CA / RS already queued) | Weak / avoid during our queue |
| Cleveland race-base C++ / Content / evidence gates | **Strong** (day-to-day PM + FAIL-CLOSED QA) | Out of lane unless asked |
| OSM / Overpass / rgpack / Workshop contract | Strong (Workshop Web + pinned compilers) | Do not fork; consume contracts only |
| Earth2Road / SUMO / external world→geometry adapters | Weak (not in-flight) | **Strong** (active eval + specs) |
| Long-form design specs / OSS reuse research | Medium | **Strong** (superpowers specs already landed) |
| Multi-agent room sequencing + gate FAIL-CLOSED | **Strong** | N/A |
| Blind merge / worktree sync across checkouts | Neither — **forbidden** without Chris/PM green | Same |

## Assignments (most capable owns)

### Grok owns (do not hand to Codex)

1. Mode B visual floor to PASS — night-mat restore, 120°/60° recapture, re-gate
2. Omni single-editor queue — B&E → VA body MI → WE → CA
3. Gate 1 Track A coordination (Chris attended Sunset only)
4. Cleveland skyline/asphalt/water Content + related C++
5. Evidence under `docs/evidence/grokbot/` and WAVE1-INDEX gates
6. Protect CruiseSprint GlobalDefault, no unattended Launch spam

### Codex owns (do not hand to Grok)

1. Earth2Road world-v2 → raceGPS geometry adapter eval in `racegps-beta`
2. New adapter module + unit tests/fixtures + contract proposal (versioned geometry artifact with projection/origin metadata)
3. Research vs test evidence stay distinguishable; upstream MIT + map/terrain terms noted
4. Specs already in Codex checkout (`game-direction-reassessment`, `open-source-reuse-review`) — Codex maintains those docs

### Shared / agree-before-merge (neither unilaterally)

1. Any change to `SOURCE_TO_UNREAL_FRAME_v1` or `RGPACK_v1`
2. Loader ownership for a new geometry artifact into Unreal
3. Touching `tools/akron-semantic-compiler` or `universal-city-compiler`
4. Bringing Earth2Road geometry into Cleveland race-base or a shared cook

### Escalate to Chris only when

- Need a shared Unreal editor slot that preempts the Mode B queue
- Want to invent new night water mat (`M_Water_Night`) or Flip-Y world import
- Want to merge Codex adapter into grokbot-cleveland / racegps playable path

## Rationale (one line each)

- **Grok on Cleveland Mode B:** already mid-queue with specialists, FAIL evidence, and omni lock discipline — switching owners mid-flight burns the editor.
- **Codex on Earth2Road adapter:** already scoped in a separate checkout with no editor need; Grok would duplicate research and risk colliding on geometry contracts.
- **Neither on compilers/rgpack forks:** standing KEEP pins; adapter must sit *beside* them, not replace them.

## Sync

Codex: ack or amend via a dated note in `docs/handoff/`. Grok will treat silence as accept of this assign until Mode B re-gate flips.

— Unreal PM
