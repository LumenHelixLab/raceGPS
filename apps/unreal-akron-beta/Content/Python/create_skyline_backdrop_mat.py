"""Create M_SkylineBackdrop (run AFTER import_skyline_backdrop.py imported the texture).

/Game/Materials/M_SkylineBackdrop: Unlit, TwoSided, Translucent, Apply Fogging off (NOT bIsSky), texture -> emissive.
"""
import unreal

eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()

tex = eal.load_asset("/Game/Textures/T_Cleveland_SkylineNight.T_Cleveland_SkylineNight")
if not tex:
    unreal.log_error("[skyline-mat] texture missing - run import_skyline_backdrop.py first")
    raise SystemExit(1)

if eal.does_asset_exist("/Game/Materials/M_SkylineBackdrop.M_SkylineBackdrop"):
    eal.delete_asset("/Game/Materials/M_SkylineBackdrop.M_SkylineBackdrop")

mat = at.create_asset("M_SkylineBackdrop", "/Game/Materials", unreal.Material, unreal.MaterialFactoryNew())
mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property("two_sided", True)
try:
    mat.set_editor_property("is_sky", False)  # WE: bIsSky drew the skydome debug overlay + suppressed sky
except Exception as e:
    unreal.log_warning("[skyline-mat] is_sky not set: %s" % e)

ts = mel.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -400, 0)
ts.set_editor_property("parameter_name", "SkylineTexture")
ts.set_editor_property("texture", tex)
mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
mat.set_editor_property("use_translucency_vertex_fog", False)  # "Apply Fogging" off
mat.set_editor_property("apply_cloud_fogging", False)
sc = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -400, 250)
sc.set_editor_property("parameter_name", "BackdropEmissiveScale")
sc.set_editor_property("default_value", 1.0)
mul = mel.create_material_expression(mat, unreal.MaterialExpressionMultiply, -150, 0)
mel.connect_material_expressions(ts, "RGB", mul, "A")
mel.connect_material_expressions(sc, "", mul, "B")
mel.connect_material_property(mul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
one = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -150, 250)
one.set_editor_property("r", 1.0)
mel.connect_material_property(one, "", unreal.MaterialProperty.MP_OPACITY)

mel.recompile_material(mat)
eal.save_asset("/Game/Materials/M_SkylineBackdrop")
unreal.log_warning("[skyline-mat] saved M_SkylineBackdrop")
