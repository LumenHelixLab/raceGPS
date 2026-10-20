# B&E — Photo-skyline targeted cook ABORT (2026-09-27)

**Lane:** Build & Engine  
**Status:** **COOK ABORT / KILLED** — not PASS. Load-only PASS unchanged.  
**Authority:** Unreal PM recommend kill (Wave 1 room); B&E executed.  
**Lock:** UnrealEditor-Cmd killed; editor lock **free**.

## What happened

| Step | Result |
|------|--------|
| Intent | Targeted Windows cook of /Game/Materials/M_SkylineBackdrop + /Game/Textures/T_Cleveland_SkylineNight |
| Actual | Ini invalidate → **FULL COOK** despite -CookPackages + -legacyiterative |
| Stall | Global shader compile FTSRRejectShadingCS (Vulkan SM5); log last write ~2026-09-27 20:48:08 ET |
| Exit | **KILLED_BY_BE** (no clean cook Succeeded) |
| Prior twin | G4 packaged-solo Development: SCW fail / FTSR jobs → AutomationTool 25 / HARD_CAP_KILLED |

## Last log lines (verbatim)

```
[2026.09.28-00.47.37:034][  0]LogShaderCompilers: Display: Job FTSRRejectShadingCS(permutation 59, format SF_VULKAN_SM5) compile time exceeded threshold (78.805s)
[2026.09.28-00.47.37:057][  0]LogShaderCompilers: Display: Job FTSRRejectShadingCS(permutation 50, format SF_VULKAN_SM5) compile time exceeded threshold (116.206s)
[2026.09.28-00.48.04:719][  0]LogShaderCompilers: Display: Job FTSRRejectShadingCS(permutation 51, format SF_VULKAN_SM5) compile time exceeded threshold (68.599s)
[2026.09.28-00.48.04:745][  0]LogShaderCompilers: Display: Job FTSRRejectShadingCS(permutation 58, format SF_VULKAN_SM5) compile time exceeded threshold (154.536s)
[2026.09.28-00.48.05:350][  0]LogShaderCompilers: Display: Job FTSRRejectShadingCS(permutation 107, format SF_VULKAN_SM5) compile time exceeded threshold (63.006s)
[2026.09.28-00.48.05:377][  0]LogShaderCompilers: Display: Job FTSRRejectShadingCS(permutation 114, format SF_VULKAN_SM5) compile time exceeded threshold (159.750s)
[2026.09.28-00.48.08:887][  0]LogShaderCompilers: Display: Job FTSRRejectShadingCS(permutation 99, format SF_VULKAN_SM5) compile time exceeded threshold (56.190s)
[2026.09.28-00.48.08:908][  0]LogShaderCompilers: Display: Job FTSRRejectShadingCS(permutation 112, format SF_VULKAN_SM5) compile time exceeded threshold (171.156s)
```

## Evidence paths

| File | Role |
|------|------|
| `2026-09-27-skyline-asset-cook.log` | Cook stdout (aborted) |
| `2026-09-27-skyline-asset-cook.meta.txt` | Start/PID/KILL |
| `2026-09-27-SKYLINE-ASSET-LOAD-CHECK.md` | **LOAD PASS** (still valid) |
| This note | Abort honesty for PM FAIL-CLOSED |

## Not claimed

- Skyline package cook PASS  
- Full Windows cook PASS  
- Visual stills / Gate 1  

## Next (when Chris / PM green a cook retry)

Prefer a recipe that does **not** force global shader rebuild for two packages, or defer cook until Mode B packaging is actually needed. LaunchCleveland / attended Track A remains the playable path — no unattended Launch / Gate 1.