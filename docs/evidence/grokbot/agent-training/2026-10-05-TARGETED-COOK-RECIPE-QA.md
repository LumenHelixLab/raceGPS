# Wave 1 - B&E targeted-cook recipe QA (Unreal PM)

**Date:** 2026-10-05 (America/New_York)
**Role:** Unreal PM (raceGPS)
**Gate:** Build & Engine targeted skyline cook recipe (`2026-10-05-TARGETED-COOK-RECIPE.md`)
**Status:** **CONDITIONAL** (FAIL-CLOSED)
**Constraint / freeze reminder:** Still NO unattended `LaunchClevelandRace` / Gate 1 spam / Tier A clones / multi-owner editor. NullRHI cook is never Gate 1. Chris owns Track A Sunset. One UnrealEditor owner on omni.

**Source graded:**
`docs/evidence/grokbot/build-engine-training/2026-10-05-TARGETED-COOK-RECIPE.md`
(Documents mirror: `C:\Users\cgp22\Documents\raceGPS-handoff\build-engine-training\2026-10-05-TARGETED-COOK-RECIPE.md`)

**Context skimmed:**
- `2026-09-27-SKYLINE-ASSET-COOK-ABORT.md` (ABORT / KILLED_BY_BE still stands)
- `2026-09-27-SKYLINE-ASSET-LOAD-CHECK.md` (LOAD PASS; not Gate 1)
- Abort "Next" superseded by this recipe's flag set; abort **verdict** not superseded

**Branch / tip cited by recipe:** `grokbot/cleveland-integration` tip `9604d0b`; UE **5.7.4** (`++UE5+Release-5.7-CL-51494982`).

**QA action:** Docs-only grade. **NO Unreal launches. NO cook runs.**

---

## Gate rule (FAIL-CLOSED)

A recipe that claims cook PASS, instructs unattended Launch/Gate 1, edits CruiseSprint / GlobalDefault / `.ini` / `.uproject` / source / assets as a precondition, or buries the 09-27 failure mode → **FAIL**.
Unverified flags that dominate whether a first attended run is safe → **CONDITIONAL** (docs may PASS as recipe; cook attempt = **HOLD** until Chris + Unreal PM green a verified run).
Docs-only honesty with honest UNVERIFIED list + kill watchers → eligible for CONDITIONAL / PASS as documentation.

---

## Checklist grades

| # | Criterion | Grade | Notes |
|---|-----------|-------|-------|
| 1 | Docs-only — does NOT claim a cook PASS or instruct unattended LaunchClevelandRace / Gate 1 | **PASS** | Banner: **DOCS ONLY. NOT RUN. NOT PASS.** Locks table bans unattended Launch / `-game` / Gate 1. Section 3b header: "DO NOT RUN without Unreal PM gate + Chris unlock." Section 6 requires both PM gate + Chris unlock. NullRHI cook explicitly "never Gate 1." |
| 2 | Honest about 09-27 failure: `-CookPackages=` not valid UE 5.7.4 → empty list → full cook; Vulkan SM5 / FTSR; full Windows cook wiped | **PASS** | §2a cites CookCommandlet.cpp (only `-MAP=` / `-PACKAGE=`; no COOKPACKAGES) + CookAllByDefault fallback. §2b cites ini invalidate + wipe of `Saved\Cooked\Windows` (current disk = GlobalShaderCache bins + Metadata only; CookInProgress=true). §2c cites Vulkan SM5 / FTSRRejectShadingCS stall + G4 twin (AutomationTool 25 / HARD_CAP_KILLED). Abort verdict retained. |
| 3 | Proposed flags: `-cooksinglepackage -PACKAGE=` for M_SkylineBackdrop + T_Cleveland_SkylineNight; separate Cooked-targeted; `-ini` overrides for D3D only; 15-min cap; watcher kill on Vulkan / global shader | **PASS** | §3a/3b: `-cooksinglepackage` + `-PACKAGE=/Game/Materials/M_SkylineBackdrop+/Game/Textures/T_Cleveland_SkylineNight`; `-OutputDir=...\Saved\Cooked-targeted\Windows`; four `-ini:Engine:[WindowsTargetSettings]:-...` removals (Vulkan SM5/SM6 + D3D ES31) leaving PCD3D_SM5/SM6; CapMin=15; FailPatterns include SF_VULKAN, Compiling global, FTSRRejectShadingCS, FullDepotSearch, Unable to find package. |
| 4 | Explicit UNVERIFIED items listed (esp whether `-ini:` reaches Windows platform config) | **PASS** | §5 lists eight UNVERIFIED items; #1 is exactly whether `-ini:Engine:` reaches `FConfigCacheIni::ForPlatform("Windows")` / `GetAllTargetedShaderFormats`. Kill criterion 2 (`SF_VULKAN` in log) is the fail-closed backstop. Also lists `_Del` location, material-shader format honour, Success string, `-NoUBA`/`-nop4` omissions, fan-out <=50 judgement, Epic docs currency. |
| 5 | No `.ini` / `.uproject` / source / asset edits required to "use" the recipe as documentation | **PASS** | Locks: "This recipe edits no `.ini`." All config via per-process `-ini:` CLI. Preflight #9 requires empty `git diff` on Config + uproject. Reading/grading the recipe needs zero project edits. Fallback if `-ini:` fails: stop + escalate to PM — do not edit DefaultEngine.ini without Chris. |
| 6 | CruiseSprint / GlobalDefault untouched | **PASS** | Lock row: `GlobalDefaultGameMode=/Script/raceGPSAkronBeta.CruiseSprintGameMode` **Stays.** No GameMapsSettings / GameMode edits in the command line. |
| 7 | READY TO TRY vs DOCS-ONLY HOLD — if unverified flags dominate → CONDITIONAL | **CONDITIONAL** | Docs recipe is freeze-safe and honest. Cook attempt remains **HOLD**: UNVERIFIED #1 (`-ini:` → Windows target-platform config) dominates whether Vulkan is actually stripped; without a verified attended log showing zero `SF_VULKAN` / zero `Compiling global`, a "READY TO TRY" green would overclaim. Section 6 already keeps status DOCS ONLY until PM gate + Chris unlock. |

---

## Overall

| Gate | Grade |
|------|-------|
| B&E targeted-cook recipe (2026-10-05) as **documentation** | **PASS** (criteria 1–6) |
| First attended cook attempt readiness | **HOLD** |
| **Combined Unreal PM grade** | **CONDITIONAL** |

Docs PASS as a fail-closed recipe. Cook attempt HOLD until Chris + Unreal PM green a verified attended run with this exact flag set and the 15-minute watcher. Do not treat this QA as cook PASS or as an unlock to launch Unreal.

### Gaps (1-line)

- **UNVERIFIED #1 dominates:** whether `-ini:Engine:[WindowsTargetSettings]:-Vulkan...` reaches the Windows *platform* config branch is unproven — kill-on-`SF_VULKAN` is the only backstop until a green attended log.
- **Fan-out threshold judgement:** `Packages Cooked: <= 50` is not measured; hard-dep count for `M_SkylineBackdrop` unknown until first run.
- **No cook evidence yet:** recipe correctly claims NOT RUN; this QA does not authorize a run.

### Next action

- **HOLD cook** until Unreal PM posts an attended-run gate **and** Chris unlocks B&E for UnrealEditor-Cmd on omni (WE lock released first).
- **On green:** one attended run only; 15-min cap; kill on Vulkan / global-shader / default-sandbox touch; land `<date>-skyline-targeted-cook.{log,meta.txt}` + PASS/FAIL note; never overwrite 09-27 abort files; never claim Gate 1 from NullRHI cook.
- **If `-ini:` fails (SF_VULKAN appears):** stop, escalate to PM — do **not** edit `DefaultEngine.ini` without Chris.
- **WE / WW / Track A:** unchanged freeze; stills still Mode B / attended Track A; no unattended LaunchClevelandRace.

---

## Not claimed by this QA

- Targeted cook PASS
- Full Windows cook PASS
- Packaging / stills / Gate 1
- Authorization to start UnrealEditor-Cmd

---

## Paths written / mirrored

**Project**
- `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\agent-training\2026-10-05-TARGETED-COOK-RECIPE-QA.md`
- `C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\agent-training\WAVE1-INDEX.md` (row added)

**Documents mirror**
- `C:\Users\cgp22\Documents\raceGPS-handoff\agent-training\2026-10-05-TARGETED-COOK-RECIPE-QA.md`
- `C:\Users\cgp22\Documents\raceGPS-handoff\agent-training\WAVE1-INDEX.md` (row added)
