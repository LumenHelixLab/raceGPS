"""_we_fix_skyline_mat.py -- LOCAL HELPER (untracked; do NOT git add).

Regenerates the node graph + flags of /Game/Materials/M_SkylineBackdrop IN PLACE
(same asset, references kept) and saves ONLY that asset:
  * is_sky = False   (bIsSky made the renderer treat the arc as a skydome: tiled
                      "SKYDOME MESH ... DOES NOT COVER" debug overlay + sky-atmosphere
                      pixels left black). Note: per UE docs bIsSky only removed aerial
                      perspective; height fog was never disabled by it.
  * fog kept off another way: blend_mode = BLEND_TRANSLUCENT with
    use_translucency_vertex_fog = False ("Apply Fogging" off) + apply_cloud_fogging = False,
    Opacity = 1.0 constant.
  * shading_model = MSM_UNLIT, two_sided = True
  * Emissive = SkylineTexture(T_Cleveland_SkylineNight).RGB * BackdropEmissiveScale (scalar, default 1)
    -> AClevelandEnvironmentActor::SkylineBackdropEmissiveScale drives it through a MID.
Fail-closed: aborts (no save) if the material or texture cannot be loaded.
Run inside UnrealEditor:  -ExecCmds="py <abs path>/_we_fix_skyline_mat.py"
"""
import unreal

TAG = "[WE skyline-mat]"
MAT_PATH = "/Game/Materials/M_SkylineBackdrop"
TEX_PATH = "/Game/Textures/T_Cleveland_SkylineNight"
eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary


def main():
    mat = eal.load_asset(MAT_PATH)
    tex = eal.load_asset(TEX_PATH)
    if not isinstance(mat, unreal.Material) or not tex:
        unreal.log_error(f"{TAG} ABORT: mat={mat} tex={tex}; nothing saved")
        return False
    before = {k: str(mat.get_editor_property(k)) for k in
              ("is_sky", "blend_mode", "shading_model", "two_sided", "use_translucency_vertex_fog")}
    unreal.log_warning(f"{TAG} before: {before}")

    mat.set_editor_property("material_domain", unreal.MaterialDomain.MD_SURFACE)
    mat.set_editor_property("is_sky", False)
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property("two_sided", True)
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    mat.set_editor_property("use_translucency_vertex_fog", False)  # "Apply Fogging" off
    mat.set_editor_property("apply_cloud_fogging", False)

    mel.delete_all_material_expressions(mat)
    ts = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -600, 0)
    ts.set_editor_property("parameter_name", "SkylineTexture")
    ts.set_editor_property("texture", tex)
    sc = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -600, 260)
    sc.set_editor_property("parameter_name", "BackdropEmissiveScale")
    sc.set_editor_property("default_value", 1.0)
    mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -300, 0)
    ok = mel.connect_material_expressions(ts, "RGB", mul, "A")
    ok &= mel.connect_material_expressions(sc, "", mul, "B")
    ok &= mel.connect_material_property(mul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    one = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 260)
    one.set_editor_property("r", 1.0)
    ok &= mel.connect_material_property(one, "", unreal.MaterialProperty.MP_OPACITY)
    if not ok:
        unreal.log_error(f"{TAG} ABORT: graph connect failed; nothing saved")
        return False

    mel.recompile_material(mat)
    after = {k: str(mat.get_editor_property(k)) for k in
             ("is_sky", "blend_mode", "shading_model", "two_sided", "use_translucency_vertex_fog",
              "apply_cloud_fogging")}
    if mat.get_editor_property("is_sky"):
        unreal.log_error(f"{TAG} ABORT: is_sky still true; nothing saved")
        return False
    saved = eal.save_asset(MAT_PATH, only_if_is_dirty=False)
    unreal.log_warning(f"{TAG} after: {after} saved={saved} (ONLY {MAT_PATH})")
    return saved


main()
