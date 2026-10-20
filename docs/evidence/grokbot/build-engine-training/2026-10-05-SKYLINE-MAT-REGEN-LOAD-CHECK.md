# B&E - Skyline material regen load check (2026-10-05)

**Lane:** Build & Engine  
**Status:** **B&E_REGEN_CHECK PASS** (editor-Cmd only).  
**Lock:** B&E owned single UnrealEditor-Cmd briefly; lock held by B&E for this attended-style load-only check.  
**Note:** load-only, NullRHI Cmd — not Gate 1, not visual PASS

## What ran

| Field | Value |
|------|--------|
| Command | `"C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\raceGPSAkronBeta.uproject -unattended -nosplash -NullRHI -nosound -stdout -FullStdOutLogOutput -abslog=C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\build-engine-training\2026-10-05-skyline-mat-regen-load.log "-ExecCmds=py C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\build-engine-training\2026-10-05-check-skyline-mat-regen.py,QUIT_EDITOR"` |
| PID | 7012 |
| Start (ET) | 2026-10-05 23:32:26 ET |
| End (ET) | 2026-10-05 23:33:16 ET |
| Exit code | 0 |
| Elapsed | ~50 s |
| Flags | `-unattended -nosplash -NullRHI -nosound -stdout -FullStdOutLogOutput` + `-ExecCmds=py <script>,QUIT_EDITOR` + `-abslog=` |

## Asset on disk (M_SkylineBackdrop.uasset)

| Field | Value |
|------|--------|
| Path | `apps/unreal-akron-beta/Content/Materials/M_SkylineBackdrop.uasset` |
| SHA256 | `990F1696FD8D0051385FA4A8F06B505476D2F8740518C47E249DF93FA9B2D550` |
| mtime | 2026-10-05 22:54:23 ET |
| Size | 16863 bytes |

## Grep'd property / verdict lines

```
[2026.10.06-03.32.48:058][  0]Cmd: py C:\projects\raceGPS-grokbot-cleveland\docs\evidence\grokbot\build-engine-training\2026-10-05-check-skyline-mat-regen.py
[2026.10.06-03.32.48:199][  0]LogPython: [BE-skyline-mat-regen] path=/Game/Materials/M_SkylineBackdrop exists=True loaded=True name=/Game/Materials/M_SkylineBackdrop.M_SkylineBackdrop
[2026.10.06-03.32.48:199][  0]LogPython: [BE-skyline-mat-regen] path=/Game/Textures/T_Cleveland_SkylineNight exists=True loaded=True name=/Game/Textures/T_Cleveland_SkylineNight.T_Cleveland_SkylineNight
[2026.10.06-03.32.48:200][  0]LogPython: [BE-skyline-mat-regen] prop is_sky=False
[2026.10.06-03.32.48:200][  0]LogPython: [BE-skyline-mat-regen] prop blend_mode=<BlendMode.BLEND_TRANSLUCENT: 2>
[2026.10.06-03.32.48:200][  0]LogPython: [BE-skyline-mat-regen] prop shading_model=<MaterialShadingModel.MSM_UNLIT: 0>
[2026.10.06-03.32.48:200][  0]LogPython: [BE-skyline-mat-regen] prop two_sided=True
[2026.10.06-03.32.48:200][  0]LogPython: [BE-skyline-mat-regen] prop fully_rough=False
[2026.10.06-03.32.48:200][  0]LogPython: [BE-skyline-mat-regen] prop use_material_attributes=False
[2026.10.06-03.32.48:201][  0]LogPython: [BE-skyline-mat-regen] prop bIsSky=False
[2026.10.06-03.32.48:201][  0]LogPython: [BE-skyline-mat-regen] prop fog_density=<err Material: Failed to find property 'fog_density' for attribute 'fog_density' on 'Material'>
[2026.10.06-03.32.48:201][  0]LogPython: [BE-skyline-mat-regen] prop disable_depth_test=False
[2026.10.06-03.32.48:201][  0]LogPython: [BE-skyline-mat-regen] prop write_only_alpha=False
[2026.10.06-03.32.48:201][  0]LogPython: [BE-skyline-mat-regen] prop allow_negative_emissive_color=False
[2026.10.06-03.32.48:201][  0]LogPython: [BE-skyline-mat-regen] prop cast_dynamic_shadow_as_masked=False
[2026.10.06-03.32.48:201][  1]LogPython: [BE-skyline-mat-regen] prop opacity_mask_clip_value=0.33329999446868896
[2026.10.06-03.32.48:201][  1]LogPython: [BE-skyline-mat-regen] MEL base_color probe=<err type object 'MaterialEditingLibrary' has no attribute 'get_material_property'>
[2026.10.06-03.32.48:201][  1]LogPython: B&E_REGEN_CHECK PASS
[2026.10.06-03.32.48:202][  1]LogPython: [BE-skyline-mat-regen] summary blend_mode=<BlendMode.BLEND_TRANSLUCENT: 2> shading_model=<MaterialShadingModel.MSM_UNLIT: 0> two_sided=True is_sky=False
[2026.10.06-03.32.48:202][  1]Cmd: QUIT_EDITOR
[2026.10.06-03.32.48:202][  1]Cmd: QUIT_EDITOR
```

## Verdict interpretation

- Both `/Game/Materials/M_SkylineBackdrop` and `/Game/Textures/T_Cleveland_SkylineNight` loaded.
- `is_sky=False` (required for PASS).
- Observed: translucent (`BLEND_TRANSLUCENT`), unlit (`MSM_UNLIT`), `two_sided=True` — matches expected regen state.
- `fully_rough=False`, `use_material_attributes=False`; no `fog_density` property on Material (try/except).

## Evidence paths

| File | Role |
|------|------|
| `docs/evidence/grokbot/build-engine-training/2026-10-05-skyline-mat-regen-load.log` | Full Cmd abslog |
| `docs/evidence/grokbot/build-engine-training/2026-10-05-check-skyline-mat-regen.py` | Script used |
| This note | Summary |

Mirrored under `Documents\raceGPS-handoff\build-engine-training\`.

## Not claimed

- Visual stills PASS  
- Gate 1 / finish+R  
- Cook / RunUAT / PIE / `-game` / LaunchClevelandRace  
- Package save (none performed)

## Process hygiene

- Pre-launch: no UnrealEditor / UnrealEditor-Cmd / ShaderCompileWorker / AutomationTool.
- Exactly one UnrealEditor-Cmd (PID 7012) for the successful attempt.
- Post-exit: no Unreal processes remain.
- Earlier failed quoting attempts (PID 21592, 38844) were killed under the 15-minute hard cap / after script-path parse failure; they did not produce a PASS log. Attempt 3 is the authoritative run.
