# Overpass → rgpack export proof (CLI)

**Date:** 2026-09-27 ~20:43–20:44 EDT (America/New_York)  
**Lane:** Workshop Web — freeze-safe green-light deliverable  
**Host:** omni · worktree `C:\projects\raceGPS-grokbot-cleveland` · branch `grokbot/cleveland-integration`  
**Contract:** `docs/contracts/RGPACK_v1.md` (ACCEPTED) · package `tools/rgpack/`

## Verdict

| Path | Result |
|------|--------|
| Offline fixture → `validate_pack_dir` | **PASS** |
| Live Overpass tiny Burke bbox → `validate_pack_dir` | **PASS** (optional; network worked) |
| Unreal editor / PIE / LaunchClevelandRace | **Not used** (hard ban) |
| Citypack XODR claimed as rgpack | **No** — adapter still post-unlock |

## What shipped

| Artifact | Role |
|----------|------|
| `tools/rgpack/overpass_export.py` | Overpass JSON → streets/checkpoints/spawn/environment + Manifest |
| `tools/rgpack/__main__.py` | `python -m rgpack export-overpass \| validate` |
| `tools/overpass_to_rgpack.py` | Thin discoverable wrapper (defaults to `export-overpass`) |
| `tests/fixtures/rgpack/overpass_burke_tiny/` | Offline Overpass-*like* JSON (Burke ~41.51/−81.69) |

Siblings cited, not rewritten: `tools/akron-semantic-compiler`, `tools/universal-city-compiler`, `tools/validate-citypack.py`.

## Exact CLI — offline (canonical proof)

```bat
cd /d C:\projects\raceGPS-grokbot-cleveland
set PYTHONPATH=tools
python -m rgpack export-overpass --fixture --out Saved\raceGPS\packs\burke_overpass_proof_v1
```

### Transcript

```
INPUT  offline fixture: C:\projects\raceGPS-grokbot-cleveland\tests\fixtures\rgpack\overpass_burke_tiny\overpass.json
ELEMENTS  14
PACK    C:\projects\raceGPS-grokbot-cleveland\Saved\raceGPS\packs\burke_overpass_proof_v1
packId  burke_overpass_proof_v1
hash    sha256:8f8d9e02c300ff1c1556712c1ebabb99ed80642be8ef9db793a3fbc6659850dc
RESULT  PASS
```

Re-validate:

```bat
python -m rgpack validate Saved\raceGPS\packs\burke_overpass_proof_v1
```

→ same `packId` / `contentHash` / `RESULT  PASS`.

### Output pack

- **Path:** `C:\projects\raceGPS-grokbot-cleveland\Saved\raceGPS\packs\burke_overpass_proof_v1\`
- **Files:** `manifest.json`, `streets.json`, `checkpoints.json`, `spawn.json`, `environment.json`
- **packId:** `burke_overpass_proof_v1`
- **contentHash:** `sha256:8f8d9e02c300ff1c1556712c1ebabb99ed80642be8ef9db793a3fbc6659850dc`
- **Frame A:** `unitsPerMeter=100`, zUp / xEast / yNorth true; origin ≈ 41.5168 / −81.6842
- **certification:** `provisional` (notes state not a citypack XODR adapter; Race must not call Overpass)

## Live Overpass (optional — succeeded)

Tiny Burke Lakefront bbox ~41.51/−81.69. Prefer `--west/--south/--east/--north` (CSV `--bbox=-w,s,e,n` also works; space-separated `--bbox -81…` confuses argparse because of the leading minus).

```bat
set PYTHONPATH=tools
python -m rgpack export-overpass --west -81.695 --south 41.510 --east -81.685 --north 41.520 --out Saved\raceGPS\packs\burke_overpass_live_try --pack-id burke_overpass_live_try --display-name "Burke Live Overpass Try" --timeout 40
```

### transcript

```
INPUT  live Overpass bbox=[-81.695, 41.51, -81.685, 41.52] (tiny; fail-closed on network)
ELEMENTS  488
PACK    C:\projects\raceGPS-grokbot-cleveland\Saved\raceGPS\packs\burke_overpass_live_try
packId  burke_overpass_live_try
hash    sha256:015b37c1cabf4429bb99772a3b52f873c0932cacb11355b558b39a4581f6f118
RESULT  PASS
```

On network/HTTP failure the CLI prints `FAIL  Overpass fetch FAIL-CLOSED: …` and exits non-zero; offline `--fixture` remains the freeze-safe proof.

## Regression

```bat
set PYTHONPATH=tools
python -m pytest tests\test_rgpack_schema.py -q
```

→ `6 passed` (golden `minimal_v1` round-trip intact).

## Honest limits

1. **No Unreal editor / PIE / LaunchClevelandRace** — Python CLI only.
2. **Citypack → rgpack adapter** (Burke/EZ XODR + racing_line) is still **post-unlock**. This proof is Overpass JSON → rgpack, not a rebrand of `citypacks/cleveland/burke_gp_1997`.
3. **Race must not call Overpass** — Workshop writes packs; Race only reads.
4. **Empty Game target compile ≠ export PASS** — evidence is `validate_pack_dir` + hash.
5. **Do not flip `GlobalDefaultGameMode`** — pack override only.
6. Centerline stitch is a simple longest-way + greedy endpoint join — good enough for export contract proof, not a full road-graph race course certifier.
7. Live pack hash is network-volatile (OSM changes); offline fixture hash is the stable citation.

## Mirrors

- Project: `docs/evidence/grokbot/workshop-web-training/2026-09-27-OVERPASS-RGPACK-EXPORT-PROOF.md`
- Documents: `C:\Users\cgp22\Documents\raceGPS-handoff\workshop-web-training\2026-09-27-OVERPASS-RGPACK-EXPORT-PROOF.md`
- Box (when synced): `/workspace/docs/evidence/grokbot/workshop-web-training/` + `/workspace/tools/`
