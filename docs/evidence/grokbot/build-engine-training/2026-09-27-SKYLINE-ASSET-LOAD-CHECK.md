# B&E — Photo-skyline asset load check (2026-09-27)

**Lane:** Build & Engine  
**Status:** **LOAD PASS** (editor-Cmd only). **Cook HOLD** until Unreal PM grades WE stills plan. Runtime EnvActor greps HOLD (Mode B / Chris attended Track A).  
**Lock:** B&E owned UnrealEditor-Cmd briefly; lock **released** after exit 0. No second editor.  
**Freeze:** No `LaunchClevelandRace` / no `-game` / no Gate 1 spam / no Tier A clones.

## What ran

| Step | Result |
|------|--------|
| Asset on disk | `Content/Materials/M_SkylineBackdrop.uasset`, `Content/Textures/T_Cleveland_SkylineNight.uasset` present on tip `5f420f6` |
| `UnrealEditor-Cmd` + `-ExecutePythonScript=.../2026-09-27-check-skyline-load.py` | Exit **0** |
| `/Game/Materials/M_SkylineBackdrop` | exists=True loaded=True |
| `/Game/Textures/T_Cleveland_SkylineNight` | exists=True loaded=True |
| Log marker | `[BE-skyline-load] PASS both M_SkylineBackdrop and T_Cleveland_SkylineNight load` |

**Cmd flags used:** `-unattended -nosplash -NullRHI -nosound` — NullRHI here is **Cmd asset load only**, not Gate 1 evidence.

## Evidence paths

| File | Role |
|------|------|
| `docs/evidence/grokbot/build-engine-training/2026-09-27-skyline-asset-load.log` | Full Cmd stdout |
| `docs/evidence/grokbot/build-engine-training/2026-09-27-check-skyline-load.py` | Script used |
| This note | Summary for PM FAIL-CLOSED |

Mirrored under `Documents\raceGPS-handoff\build-engine-training\`.

## Soft notes (already from WE)

- Do **not** re-run `Content/Python/import_skyline_backdrop.py` until its hardcoded `C:\projects\racegps\...` path is patched; keepers `.uasset`s are already on tip.
- Targeted package **cook** was aborted / not completed after PM hold — will resume only after WE stills-plan PASS.
- Runtime greps still wait attended/Mode B: `photo skyline backdrop built` vs `M_SkylineBackdrop missing; falling back to box skyline` (EnvActor `BuildSkylineBackdrop`).

## Not claimed

- Visual stills PASS  
- Gate 1 / finish+R  
- Full map cook  
- Packaging  