# Cleveland Burke GP 1997 citypack (PROVISIONAL)

**Canonical path:** `citypacks/cleveland/burke_gp_1997/` (repo root; what pytest and `scripts/build_cleveland_circuit.py` use).

**Apps mirror:** `apps/unreal-akron-beta/citypacks/cleveland/burke_gp_1997/` is a Windows directory junction to the canonical path (single source of truth).

**Status:** PROVISIONAL / certification blocked. OSM reconstruction of the 1997-2007 / 2.106 mi / 10-turn clockwise family. Not a certified 2006 surveyed racing line (see `docs/evidence/grokbot/G3-prep/BURKE_SOURCE_AUDIT.md`).

**Default GameMode / CityId:** unchanged — remains `CruiseSprintGameMode` / `akron-oh-beta-001`. This pack is delivered for G3 coherence; selecting it at runtime is opt-in (`racegps.CityId` / CitypackDir), not the global default.

**Frame:** `docs/contracts/SOURCE_TO_UNREAL_FRAME_v1.md` (Frame A).

**Regenerate:** `python scripts/build_cleveland_circuit.py` from repo root (writes into this canonical directory).