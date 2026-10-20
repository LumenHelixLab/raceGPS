# Burke EZ Mode B photo-skyline stills: Midnight, run 2026-10-05 (FAIL)

**Verdict: FAIL, all 4 shots.** Not Gate 1 evidence. Nothing was git added or committed.

- Commit: `9604d0b` (branch `grokbot/cleveland-integration`, worktree `C:\projects\raceGPS-grokbot-cleveland`)
- Plan: `docs/evidence/grokbot/world-environment-training/2026-09-27-PHOTO-SKYLINE-STILLS-PLAN.md`
- Tool: `apps/unreal-akron-beta/Content/Python/_we_modeb_stills_capture.py` (local helper, untracked)
- Captured: 2026-10-05 22:29 ET (America/New_York). Single UnrealEditor, PID 51808, exited on its own at 22:29:51 ET. The map was **not** saved (no SavePackage in log; umap mtime still 2026-09-07).
- RHI: `LogRHI: Using Forced RHI: D3D12`, SM6, AMD Radeon(TM) 880M. Not NullRHI, not Vulkan. No FTSRRejectShadingCS stall; `Shaders left to compile 0`.

## Command used (run 2)

```
set RGPS_STILLS_QUIT=1
"C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\Win64\UnrealEditor.exe" "C:\projects\raceGPS-grokbot-cleveland\apps\unreal-akron-beta\raceGPSAkronBeta.uproject" /Game/Maps/Cleveland5_0KmWorld -d3d12 -log -NoSplash -ExecCmds="py C:/projects/raceGPS-grokbot-cleveland/apps/unreal-akron-beta/Content/Python/_we_modeb_stills_capture.py"
```

Run 1 used `-ExecutePythonScript=` instead. The editor issued `QUIT_EDITOR` about 2 s after the script armed, so no shots were taken. In UE 5.7, `-ExecutePythonScript` quits the GUI editor once the script returns. Use `-ExecCmds="py ..."` instead.

## Log cues

- PASS cue present: `raceGPS Cleveland env: photo skyline backdrop built (radius 2600 m, span 110 deg)`
- FAIL cues (`M_SkylineBackdrop missing` / `falling back to box skyline`): absent
- `look FINAL [Midnight]: hour=22.00 sunI=2.40 sunPitch=-46.0 sunYaw=35.0 skyI=2.20`
- Errors: only the existing `LogClass: StructProperty ... not initialized properly` lines (AkronXodrImporter.h, StreetFurnitureSpawner.h). None come from this capture.
- See `capture_log_excerpt_midnight_9604d0b.txt`.

## Per-shot verdict

| Shot | Verdict | What the still actually shows |
|---|---|---|
| S1 skyline hero (compass 205, FOV 55, eye 4 m) | **FAIL** | The photo panorama renders and fills the horizon band, but it is **upside down**: towers hang from the top and the lake reflection band sits above them. It is overexposed (washed lavender). The upper sky is pure black void. The ground is dead black, with black unlit box silhouettes (hangars and buildings) on the horizon. An engine debug overlay is tiled across the frame: "YOUR SCENE CONTAINS A SKYDOME MESH WITH A SKY MATERIAL BUT IT DOES NOT COVER THAT PART OF THE SCREEN". |
| S2 lake + skyline split (NE corner, 30 m, compass 255, FOV 100) | **FAIL** | About 70% of the frame is black. The inverted skyline card covers only the **right** third. Lake Erie can't be seen (the left is black). Same debug-text overlay. Framing is wrong: skyline is on the right, not the left (see world handedness below). |
| S3 car midground (Showcase intro framing, FOV 66) | **FAIL** | The car is a clean black silhouette on the left-third midground against the bright inverted card, which reads well as a silhouette. But it has the same upside-down skyline, black sky and ground, black box silhouettes, and debug overlay. |
| S3b car close (extra) | **FAIL** | The car roof and greenhouse silhouette sits at bottom centre. Same defects as S3. |

None of the four meets the Midnight Club night-cruise bar. The render is not black-only: mean luma is 70 / 18 / 57 / 63. The backdrop is not pink, and there is no box-skyline fallback, but the frames fail on void, inverted art and overlay.

## Root causes observed (for WE / B&E)

1. **Inverted backdrop UVs.** `BuildSkylineBackdrop()` puts V=0 on the bottom vertex and V=1 on the top. Texture V=0 is the top of the image, so the panorama is vertically flipped. Swapping the V values would fix it. That is a source change, not done here.
2. **`M_SkylineBackdrop` has `bIsSky`.** A non-full-screen arc using a sky material makes the engine print the "SKYDOME MESH ... DOES NOT COVER" overlay into every frame, in non-shipping builds and in -game too. It likely also suppresses the normal sky behind it. Use unlit, two-sided, and fog-disabled settings without IsSky.
3. **Black void and black ground/lake.** The Midnight look gives a black sky above the 600 m card. Asphalt, lake (`Water_Surface` MID) and the HISM boxes render black. Exposure is driven by the bright emissive card.
4. **World handedness.** UE is left-handed. With Frame A (X=east, Y=north), screen-right while facing +X is +Y (north), so the world renders **mirror-imaged** relative to real compass. Looking toward real SSW, the lake is on the left. In UE frames a real-geography "skyline left + lake right" split can't be had; the plan's left/right expectation needs re-stating. Related: `ClevelandSoloGameMode` sets UE yaw = compass-90.

## Caveat

Editor-world render: the EnvActor, LookDirector and car were spawned transient into the editor level through Python. There was no GameMode, no BeginPlay and no PIE. Auto-exposure, Lumen and lighting can differ from `-game`/runtime, but defects 1, 2 and 4 are geometry/material facts and will reproduce at runtime.

## Files

See `SHA256SUMS.txt`. Mirror: `%USERPROFILE%\Documents\raceGPS-handoff\burke-ez-ribbon\stills\`.
