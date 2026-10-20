# Wave 1 training index (Unreal PM)

**Freeze:** No unattended editor / PIE / `LaunchClevelandRace` / Gate 1 spam / Tier A clones. Chris owns Track A Sunset. Docs + limited Wave 1 lane work after Chris green light 2026-09-27 — Mode B stills / Mode C / full agent game still need letter unlock via Prototyper.

| Lane | Folder | Pack 01 (primary) | Annotations | Pack QA | Annotations QA |
|------|--------|-------------------|-------------|---------|----------------|
| World Environment | `../world-environment-training/` | `2026-09-26-PACK-01-CLEVELAND-VISUAL-FLOOR-STEAL-MAP.md` | `...-CLEVELAND-VISUAL-FLOOR-ANNOTATIONS.md` | [TRAINING QA](./2026-09-26-WAVE1-TRAINING-QA.md) → **PASS** | [ANNOTATIONS QA](./2026-09-26-WAVE1-ANNOTATIONS-QA.md) → **PASS** |
| Build & Engine | `../build-engine-training/` | `2026-09-26-PACK-01-WIN64-DEV-REBUILD-AND-LOG-FORENSICS.md` | `...-WIN64-DEV-REBUILD-AND-LOG-FORENSICS-ANNOTATIONS.md` | same → **PASS** | same → **PASS** |
| Workshop Web | `../workshop-web-training/` | `2026-09-26-PACK-01-TWO-APP-AND-RGPACK-CONTRACT-MAP.md` (+ routes stub) | `...-TWO-APP-AND-RGPACK-ANNOTATIONS.md` | same → **PASS** | same → **PASS** |

**Overall packs:** FULL SET PASS (2026-09-26).  
**Overall annotations:** FULL SET PASS (2026-09-26).

## Wave 1 unlock gates (post Chris green 2026-09-27)

| Gate | Artifact | QA | Grade | Notes |
|------|----------|----|-------|-------|
| WE photo-skyline stills plan | `../world-environment-training/2026-09-27-PHOTO-SKYLINE-STILLS-PLAN.md` | [STILLS PLAN QA](./2026-09-27-WAVE1-PHOTO-SKYLINE-STILLS-PLAN-QA.md) | **PASS** | EnvActor reuse only; `burke-ez-ribbon/` slot; capture gated Mode B / attended Track A; cook/load → B&E. Tips `5f420f6` + `2d9cf6d`. |
| WW Overpass→rgpack export proof | `../workshop-web-training/2026-09-27-OVERPASS-RGPACK-EXPORT-PROOF.md` | [WW EXPORT+SEMANTIC QA](./2026-09-27-WAVE1-WW-EXPORT-AND-SEMANTIC-QA.md) | **PASS** | Offline fixture + live tiny Burke `validate` PASS; pack hash `sha256:8f8d9e02...`; pytest 6/6; freeze-safe CLI only; citypack→rgpack still post-unlock. Doc sha256 `26157aa2...`. |
| WW semantic compiler (inventory + brief) | `../semantic-compiler/2026-09-27-SEMANTIC-COMPILER-INVENTORY.md` (+ expansion brief) | same QA → **PASS** | **PASS** | Akron KEEP; universal = expansion shell; Cleveland race-base scoreboard; adapter post-unlock. Doc sha256 `8eccc3fd...` / `6452a03c...`. |

| B&E targeted skyline cook recipe | `../build-engine-training/2026-10-05-TARGETED-COOK-RECIPE.md` | [TARGETED COOK RECIPE QA](./2026-10-05-TARGETED-COOK-RECIPE-QA.md) | **CONDITIONAL** | Docs-only recipe PASS (criteria 1-6); cook attempt HOLD — UNVERIFIED `-ini:` reach into Windows platform config dominates; no Launch/Gate1; CruiseSprint untouched; requires Chris+PM green before attended run. |
| WE Mode B photo-skyline stills (Midnight, `9604d0b`) | `../burke-ez-ribbon/stills/` (S1/S2/S3/S3b + manifest + log excerpt + SHA256SUMS) | [MODE B STILLS QA](./2026-10-05-MODE-B-STILLS-QA.md) | **FAIL** (confirmed) | WE self-FAIL honest; D3D12 not NullRHI, no pink, no box fallback path - but black void 58-89%, skyline rendered 180 deg rotated (V+U UV bug in `BuildSkylineBackdrop`), `M_SkylineBackdrop` bIsSky -> SKYDOME debug overlay in every frame, dead-black asphalt/lake. Next lane = WE mat/backdrop source fix, then re-capture; B&E cook not on critical path. |

**Unlock note:** `docs/handoff/2026-09-27-WAVE1-UNLOCK.md` (Documents mirror: `C:\Users\cgp22\Documents\raceGPS-handoff\2026-09-27-WAVE1-UNLOCK.md`).

**Next:** B&E targeted-cook recipe = CONDITIONAL (docs PASS / cook HOLD until Chris+PM green); load PASS still valid; on green: attended targeted cook under editor lock; WE stills hold until Chris Mode B / attended Track A; WW citypack→rgpack adapter = post-unlock only. FAIL-CLOSED: NullRHI / void / pink mat ≠ PASS. WW Overpass→rgpack CLI proof + semantic cite-and-path **gated PASS** 2026-09-27.

**2026-10-05 Mode B stills:** WE Midnight stills graded **FAIL** (confirmed, not overturned) - see [MODE B STILLS QA](./2026-10-05-MODE-B-STILLS-QA.md). Fix lane: WE `BuildSkylineBackdrop` UVs (flip V **and** U) + regenerate `M_SkylineBackdrop` without IsSky + Midnight sky/asphalt/lake floor; then attended re-capture (Chris+PM green).
