# raceGPS consolidation — 2026-10-19

**Authority:** Chris approved ("go", 2026-10-19 ~23:46 ET): combine all parallel work, remove no features.
**Result:** one line of development on `master`; single working folder `C:\projects\racegps`.

## Merged into master

| Source | What it brought |
|---|---|
| `grokbot/cleveland-integration` (+ saved WIP commit `4e60ff2`) | easy-test-beta launcher, rgpack/Workshop, skeletal-safe car paint, name-protection + F2P notes, Mode B skyline/material fixes, night materials, Overpass→rgpack exporter, October handoffs + evidence |
| `integration/reconciled` | Sept showcase race loop (full lap verified 9/9), V15/V16 night visuals, M2 real-roads pipeline (ribbon specs/bake/validator), 20-milestone plan, Track B viewport diagnostics (TEMP) |
| `feature/cleveland-showcase-demo` | sprint_status 20-milestone dashboard (M2 marked blocked:ue-bake-ram) |
| `origin/codex/two-car-contact-slice` | two-car first-release scope + fair contact policy |
| `origin/feature/akron-pin` | CityPack v2 steel-thread exporter (Akron/UCC) |
| `origin/showcase/cleveland-intro-2026-10-18` | cinematic intro prompts, garage signs, wordmark concepts |
| `archive/omni-pause-handoff-2026-09-29` | pause handoff docs |
| Danu snapshot (`archive/danu-full-sync-snapshot`) | **only** `docs/contracts/CITYPACK_V2.md` + manifest schema (needed by CityPack v2 tests). Rest is July-era code older than master; kept under the tag, not merged. |
| `racegps` folder loose files | newer pause/unlock banners, `unreal-game-dev-HANDOFF.md` |

## Owner decisions applied

- **Midnight lighting:** September V15 night toolbox is the default. October WE recapture (exposure clamp + navy sky) is kept behind `AClevelandLookDirector::bUseOctoberNightExposure` (default `false`) for side-by-side comparison in the editor.
- **Launch preset:** Sunset (Midnight visuals failed Mode B stills on 2026-10-05).

## Nothing lost — where the old state lives

- Every pre-merge branch tip: tags `pre-merge-2026-10-19/*`
- Every loose/uncommitted file from the `racegps` folder: branch `backup/racegps-folder-loose-files-2026-10-19`
- Danu snapshot: tag `archive/danu-full-sync-snapshot`

## Verified here (portable, Linux)

- Python: full pytest suite green (Python 3.12).
- Node: typecheck green; workspace tests green except one launcher test that asserts a Windows path separator (only passes on Windows; unchanged by this merge).

## NOT verified — next gates (Windows, omni)

1. **UE 5.7 compile** of merged C++ — last attempt (2026-09-25) died of host RAM exhaustion. Close other apps; build with low parallelism (e.g. `-MaxParallelActions=2`).
2. **Gate 1 lap (Track A, attended):** `LaunchClevelandRace.bat Sunset`, drive to finish HUD, press R. Watch for the ViewportClosed ~2 s after Racing (Track B diagnostics are compiled in to catch it).
3. Only after 1+2 pass: package installer and launch.
