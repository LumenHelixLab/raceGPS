"""B&E load-only check of regenerated M_SkylineBackdrop. No save, no cook, no Gate 1."""
import unreal

TAG = "[BE-skyline-mat-regen]"
eal = unreal.EditorAssetLibrary

MAT_PATH = "/Game/Materials/M_SkylineBackdrop"
TEX_PATH = "/Game/Textures/T_Cleveland_SkylineNight"

def safe_prop(obj, name):
    try:
        val = obj.get_editor_property(name)
        unreal.log("%s prop %s=%s" % (TAG, name, val))
        return val
    except Exception as ex:
        unreal.log("%s prop %s=<err %s>" % (TAG, name, ex))
        return None

mat_loaded = False
tex_loaded = False

mat_exists = eal.does_asset_exist(MAT_PATH)
mat = eal.load_asset(MAT_PATH) if mat_exists else None
mat_loaded = bool(mat)
unreal.log("%s path=%s exists=%s loaded=%s name=%s" % (
    TAG, MAT_PATH, mat_exists, mat_loaded, mat.get_path_name() if mat else "NONE"))

tex_exists = eal.does_asset_exist(TEX_PATH)
tex = eal.load_asset(TEX_PATH) if tex_exists else None
tex_loaded = bool(tex)
unreal.log("%s path=%s exists=%s loaded=%s name=%s" % (
    TAG, TEX_PATH, tex_exists, tex_loaded, tex.get_path_name() if tex else "NONE"))

is_sky = None
blend_mode = None
shading_model = None
two_sided = None

if mat:
    # Core expected properties
    is_sky = safe_prop(mat, "is_sky")
    blend_mode = safe_prop(mat, "blend_mode")
    shading_model = safe_prop(mat, "shading_model")
    two_sided = safe_prop(mat, "two_sided")
    # Cheap extras
    safe_prop(mat, "fully_rough")
    safe_prop(mat, "use_material_attributes")
    # Fog-related (best-effort; names vary)
    for fog_name in (
        "is_sky",  # already read; harmless duplicate guard skipped below
        "bIsSky",
        "fog_density",
        "disable_depth_test",
        "write_only_alpha",
        "allow_negative_emissive_color",
        "cast_dynamic_shadow_as_masked",
        "opacity_mask_clip_value",
    ):
        if fog_name == "is_sky":
            continue
        safe_prop(mat, fog_name)
    # MaterialEditingLibrary soft probes
    try:
        mel = unreal.MaterialEditingLibrary
        try:
            unreal.log("%s MEL get_material_property=%s" % (TAG, mel.get_material_property(mat, unreal.MaterialProperty.MP_BASE_COLOR) if hasattr(unreal, "MaterialProperty") else "n/a"))
        except Exception as ex:
            unreal.log("%s MEL base_color probe=<err %s>" % (TAG, ex))
    except Exception as ex:
        unreal.log("%s MaterialEditingLibrary unavailable: %s" % (TAG, ex))

# Verdict: PASS only if both load AND is_sky is False
reason_parts = []
if not mat_loaded:
    reason_parts.append("M_SkylineBackdrop did not load")
if not tex_loaded:
    reason_parts.append("T_Cleveland_SkylineNight did not load")
if mat_loaded and is_sky is not False:
    reason_parts.append("is_sky=%s (expected False)" % is_sky)

if not reason_parts:
    unreal.log("B&E_REGEN_CHECK PASS")
    unreal.log("%s summary blend_mode=%s shading_model=%s two_sided=%s is_sky=%s" % (
        TAG, blend_mode, shading_model, two_sided, is_sky))
else:
    unreal.log_error("B&E_REGEN_CHECK FAIL %s" % "; ".join(reason_parts))
    unreal.log("%s summary blend_mode=%s shading_model=%s two_sided=%s is_sky=%s" % (
        TAG, blend_mode, shading_model, two_sided, is_sky))

# Quit editor so Cmd exits cleanly (ExecCmds path does not auto-quit)
try:
    unreal.SystemLibrary.quit_editor()
except Exception:
    try:
        unreal.EditorLevelLibrary.exit_editor()
    except Exception as ex:
        unreal.log_warning("%s quit failed: %s (host may still need QUIT_EDITOR)" % (TAG, ex))
