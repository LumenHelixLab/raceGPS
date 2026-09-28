# Showcase keepers → grokbot (2026-09-27, second commit)

## Already on grokbot tip (no copy needed)
- `ClevelandEnvironmentActor.cpp/.h` photo-skyline — identical to showcase working tree; already committed on `grokbot/cleveland-integration`
- Charger `Door*` / `Lights` / `Glass/*.uasset` — already tracked; hashes match showcase
- `attach_charger_doors.py` — already tracked; hash match
- G2-prep `COORDINATE_CONSUMER_INVENTORY.md` + G3-prep `BURKE_SOURCE_AUDIT.md` — already tracked; hash match

## Newly copied from showcase into this commit
- `Content/Materials/M_SkylineBackdrop.uasset`
- `Content/Textures/T_Cleveland_SkylineNight.uasset`
- `Content/SourceImages/cleveland_skyline_night_jan2025.jpg` + `CREDITS.md`
- `Content/Python/create_skyline_backdrop_mat.py`
- `Content/Python/import_skyline_backdrop.py`

## Skipped (noise / HOLD)
- `Content/Python/_door_probe.py`, `_ground_probe.py`
- `Temp/**`, Cesium sqlite / CesiumSettings
- SPA/html probes
- showcase unpushed docs commit `5de52ac` (left on showcase branch; not cherry-picked here)
