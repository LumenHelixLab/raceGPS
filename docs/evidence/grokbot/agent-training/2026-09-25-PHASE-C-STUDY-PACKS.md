# Phase C — Study-first packs (raceGPS agent training)

**Status:** Phase C **unlocked for study notes**. Docs / README / wiki WebFetch only. **Still no clones, no Marketplace, no Unreal editor, no downloads of repos** until Chris greens installs.  
**Owner:** Unreal PM (synthesis). Specialists may draft read-along annotations into their `*-training/` folders **after** this pack lands — they are **not** required to write yet unless parent asks.  
**Checked:** 2026-09-25 (America/New_York)  
**Constraint weave (every pack):** UE **5.7**; GlobalDefaultGameMode stays **CruiseSprint** (Showcase override only); **Gate 1 HOLD**; no black void / NullRHI evidence; Burke EZ + Cleveland skyline + Lake Erie visual bar; reuse packs, no CARLA rebuild, no greenfield Cleveland; race loop **countdown → racing → finish HUD → R restart**; freeze: no omni editor / PIE / LaunchClevelandRace during training.

**Companions:** [Phase B sources](./2026-09-25-PHASE-B-SOURCES.md) · [Kill list](./2026-09-25-PHASE-B-KILL-LIST.md) · [Outline](./2026-09-25-OUTLINE-FOR-APPROVAL.md)

---

## How to use

1. Read packs in order **01 → 05** (below). Optional VA tip: KinetiForge README patterns after pack 01.
2. Map every lesson to a raceGPS observable (Gate 1 / Burke / vehicle / session). Do not invent scaffolding.
3. Cite URL + date checked when you annotate. Anecdote ≠ API (Reddit leads stay hypotheses).
4. **Observable checks** in each pack are marked **FUTURE** — do not run editor / PIE / LaunchClevelandRace now.
5. When game work reopens, prove lessons with screenshot + log — never NullRHI / black void.

---

## Reading order

| # | Pack | Primary owner | Path |
|---|------|---------------|------|
| 1 | Epic Chaos vehicle setup | **VA** (+ RS skim) | [phase-c/01-epic-chaos-vehicles.md](./phase-c/01-epic-chaos-vehicles.md) |
| 2 | Player Controllers + Enhanced Input | **RS** (+ PM) | [phase-c/02-player-controller-enhanced-input.md](./phase-c/02-player-controller-enhanced-input.md) |
| 3 | CARLA OpenDRIVE + ASAM OpenDRIVE | **CA** (+ ART1 composition from Phase B) | [phase-c/03-opendrive-carla-asam.md](./phase-c/03-opendrive-carla-asam.md) |
| 4 | unreal-simple-racer patterns (README only) | **RS** | [phase-c/04-unreal-simple-racer-patterns.md](./phase-c/04-unreal-simple-racer-patterns.md) |
| 5 | UETrafficGame patterns (README + wiki hub) | **RS** (+ VA) | [phase-c/05-uetrafficgame-patterns.md](./phase-c/05-uetrafficgame-patterns.md) |

**Optional (VA, after 01):** KinetiForge README — https://github.com/myoozy/KinetiForge-Vehicle-System — MIT; made in UE5.3; **patterns only** (input smoothing, LSD lock feel, async-physics discipline). Do **not** replace Chaos Vehicles. No clone until Chris greens.

---

## Suggested ownership split

| Lane | Owns | Notes |
|------|------|-------|
| **Course Architect (CA)** | Pack **03** + Phase B **ART1** (Evenant value thumbnails) for skyline/water still judgment | XODR vocabulary for `cleveland_burke_gp_1997_ez`; wrap/light, don’t rebuild |
| **Vehicle Arcade (VA)** | Pack **01** + optional KinetiForge README | Arcade feel on existing Chaos stack; Midnight Club bar, not iRacing |
| **Race Systems (RS)** | Packs **02**, **04**, **05** | Session ownership, IMC, countdown→finish→R; GameInstance/PC timing authority |
| **Unreal PM** | Cross-cut + evidence mapping | Gate 1 HOLD; CruiseSprint default; kill-list enforcement; synthesis lives here |

Specialists may add short annotations under `course-architect-training/`, `vehicle-arcade-training/`, `race-systems-training/` as **read-along only**. This directory remains the synthesis source of truth.

---

## Kill-list reminder (do not study / clone / buy)

From [2026-09-25-PHASE-B-KILL-LIST.md](./2026-09-25-PHASE-B-KILL-LIST.md):

- **No R-Tune Fab** (paid proprietary)
- **No cracked AVS** / GFX-HUB mirrors
- **No City Sample greenfield** (reuse Burke/Cleveland pipelines)
- **No CHAOS RAT** (`tiagorlampert/CHAOS` — malware name-collision with Chaos physics)
- Also: unpaid Marketplace peeks, Unity/Godot cloners for UE session patterns, Marketplace assets bundled in MIT repos without redistribution rights

---

## Phase C unlock status

| Item | Status |
|------|--------|
| Study notes / WebFetch READMEs | **Unlocked** (this pack) |
| Git clone / Marketplace / Unreal install | **Blocked** until Chris greens |
| omni editor / PIE / LaunchClevelandRace | **Frozen** |
| Gate 1 | **HOLD** |
| Specialist required write-ups | **Not required yet** (optional annotations OK) |

**Next gate:** Chris greens installs and/or Phase D resume game work.

---

## Pack count

**5** study packs + this master index. Zero clones performed for this Phase C write.
