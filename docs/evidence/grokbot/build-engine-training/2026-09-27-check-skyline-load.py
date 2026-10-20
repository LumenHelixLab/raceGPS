"""B&E freeze-safe skyline asset load check. No LaunchClevelandRace / no -game."""
import unreal

eal = unreal.EditorAssetLibrary
checks = [
    "/Game/Materials/M_SkylineBackdrop",
    "/Game/Textures/T_Cleveland_SkylineNight",
]
ok = True
for p in checks:
    exists = eal.does_asset_exist(p)
    loaded = eal.load_asset(p) if exists else None
    name = loaded.get_path_name() if loaded else "NONE"
    unreal.log("[BE-skyline-load] path=%s exists=%s loaded=%s name=%s" % (p, exists, bool(loaded), name))
    if not exists or not loaded:
        ok = False
        unreal.log_error("[BE-skyline-load] FAIL %s" % p)

# Soft note: import script still hardcodes old racegps path — do not reimport.
import_script = "/Game/Python/import_skyline_backdrop"
unreal.log("[BE-skyline-load] note: do not run import_skyline_backdrop.py until PROJ path patched (hardcodes C:\\projects\\racegps\\...)")

if ok:
    unreal.log("[BE-skyline-load] PASS both M_SkylineBackdrop and T_Cleveland_SkylineNight load")
else:
    unreal.log_error("[BE-skyline-load] FAIL one or more assets did not load")
    raise SystemExit(1)