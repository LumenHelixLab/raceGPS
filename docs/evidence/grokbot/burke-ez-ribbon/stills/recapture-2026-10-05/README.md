# Burke EZ ribbon: Midnight stills recapture, 2026-10-05 (b205)

**Overall verdict: FAIL (4/4 shots, graded fail-closed).** The backdrop fix works: the photo is upright, not mirrored, and the skydome overlay is gone. Two things still fail: the ground and lake are dead black, and the S2 framing is wrong. Don't use these stills as Gate 1 evidence.

## Provenance
- Commit `9604d0b` (branch `grokbot/cleveland-integration`) plus **uncommitted local edits**:
  - `ClevelandEnvironmentActor.h/.cpp`: skyline arc params, V-upright and U-mirror UVs, emissive MID, lighter midnight water tint.
  - `ClevelandLookDirector.h/.cpp`: night exposure-floor PPV, SkyLuminanceFactor, AutoExposureBias set to 0.
  - `create_skyline_backdrop_mat.py`, `import_skyline_backdrop.py`: is_sky=False, translucent unlit.
  - Untracked scripts: `_we_fix_skyline_mat.py`, `_we_modeb_stills_capture.py`.
  - Asset `Content/Materials/M_SkylineBackdrop.uasset`, regenerated.
- Build: UBT `raceGPSAkronBetaEditor Win64 Development -MaxParallelActions=1 -NoUBA -NoXGE`, editor closed. **Result: Succeeded** (9 actions, 55.3 s).
- Capture: one editor session, 22:53:51 to 22:55:37 ET. Command:
  `UnrealEditor.exe raceGPSAkronBeta.uproject /Game/Maps/Cleveland5_0KmWorld -d3d12 -log -NoSplash -ExecCmds="py _we_fix_skyline_mat.py, py _we_modeb_stills_capture.py"`
  - Env: `RGPS_STILLS_QUIT=1`.
  - Log: `Using Forced RHI: D3D12`, AMD Radeon 880M, SM6.
  - The map was **not** saved. The only package saved was `/Game/Materials/M_SkylineBackdrop`.
- Material regen:
  - Before: is_sky=True, BLEND_OPAQUE.
  - After: **is_sky=False**, BLEND_TRANSLUCENT, MSM_UNLIT, two_sided=True, use_translucency_vertex_fog=False, apply_cloud_fogging=False. saved=True.
- Backdrop cues: `photo skyline backdrop built (radius 2600 m, span 110 deg)`, `backdrop centre=205.0 deg mirrorU=1 emissiveScale=0.45 (V upright)`.
- Exposure cue: `night exposure floor enabled=1 EV100=[-1.00,0.50]`.
- Overlay: no SKYDOME, bIsSky or box-skyline-fallback lines in the log.
- Caveat: this was rendered in the editor world (HighResShot 1920x1080), not in PIE or a packaged build.

## Root-cause lead for black ground and lake (from the log)
The log has three `Failed to find object` lines: `/Game/Materials/M_Water_Blue`, `/Game/Materials/M_NightAsphalt` and `/Game/Materials/M_NightWindow`. The Midnight MIDs for water and asphalt have no parent material, so those surfaces render near-black whatever the exposure. Also missing: the `SM_Hangar*` meshes (expected; fallback in use) and `M_CarPaint_Master_New`, which failed to compile and falls back to the default material.

## Per-shot verdicts
| Shot | File | Verdict | Observed |
|---|---|---|---|
| S1 skyline hero | S1_skyline_hero_b205_midnight_9604d0b.png | **FAIL** | Photo upright and not mirrored: Key Tower (white crown) is left of 200 Public Sq (gold) and Terminal Tower (magenta) is to the right, matching the source photo. No overlay. The sky is a deep blue gradient. The lower 35% of the frame is dead black (98.7% of pixels <4/255), so no asphalt is visible. The only "water" is the reflection inside the photo. Black HISM slabs sit in front of the card. A hard curved top edge on the card shows against the blue sky (lavender haze band). |
| S2 lake/skyline split | S2_lake_skyline_split_b205_midnight_9604d0b.png | **FAIL** | Framing is wrong, as the arc math predicted for 205/110. The skyline appears only as a small card at the far screen-left (x below about 0.2) showing the stadium/bridge end, not the downtown towers. Screen-right shows dark navy runway and black ground, and no visible Lake Erie surface. The sky is fine. |
| S3 car midground | S3_car_midground_b205_midnight_9604d0b.png | **FAIL** | The backdrop is correct (upright, correct order, no overlay). The car is a tiny silhouette at left and not legible. The ground is 100% dead black. |
| S3b car close | S3b_car_close_b205_midnight_9604d0b.png | **FAIL** | The backdrop is correct. The car is only a black outline in front of the card; no paint or lights read. The ground is dead black (97.6% <4/255). |

The night-cruise look is partially there: the sky and skyline read as night, but the scene has no lit asphalt, lake or car.

## Reframe rerun not performed
The single allowed rerun was conditional on *only* the S2 framing being wrong. Black ground and lake also fail (missing materials) in all four shots, so the condition wasn't met, and a bearing change can't fix that. The recommended reframe for when the materials are fixed is arc **120 deg / 60 deg span** with S2 at EZ sample 246 (204 m, 258 m) and yaw -5. Arc math then puts the skyline at screen x [-1,-0.02] (80% of the photo) and the lake at x [0.38,1].

## Known risks
- The translucent card won't appear in Lumen or SSR reflections, and its sorting against other translucency isn't guaranteed.
- Exposure EV range values were tuned blind.
- The left-handed world mirror (Flip-Y import, ticket (a)) is still unresolved and on hold. The U mirror only compensates for it on the card.
- EditorPerformanceSettings isn't exposed to Python, so background throttling could not be disabled.

The original FAIL set in `../` was not touched. Nothing has been committed.
