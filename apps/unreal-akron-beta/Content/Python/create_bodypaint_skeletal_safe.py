"""Create skeletal-safe body paint master + optional MI for Dodge Charger.

/Game/Materials/M_BodyPaint_SkeletalSafe
  Opaque, Default Lit, UsedWithSkeletalMesh=true (and UsedWithStaticMesh)
  Vector param BaseColor default dark asphalt (0.12, 0.13, 0.15)
  Scalar Metallic ~0.6, Roughness ~0.28

/Game/Materials/MI_ChargerBody_SkeletalSafe
  Instance of the master (Hellcat-ish orange default; runtime tints via MID)

Pattern matches create_skyline_backdrop_mat.py (AssetTools + MaterialEditingLibrary).
Do NOT touch M_CarPaint_Master_New / Triplanar / WE night mats.
"""
import unreal

eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
at = unreal.AssetToolsHelpers.get_asset_tools()

MASTER_DIR = "/Game/Materials"
MASTER_NAME = "M_BodyPaint_SkeletalSafe"
MASTER_PATH = f"{MASTER_DIR}/{MASTER_NAME}"
MI_NAME = "MI_ChargerBody_SkeletalSafe"
MI_PATH = f"{MASTER_DIR}/{MI_NAME}"

TAG = "[VA body-mi]"


def _set_usage(mat):
    """Mark usable on skeletal + static meshes (illegal-on-skel was BasicShapeMaterial failure)."""
    for prop, val in (
        ("used_with_skeletal_mesh", True),
        ("used_with_static_mesh", True),
        ("used_with_morph_targets", True),
    ):
        try:
            mat.set_editor_property(prop, val)
        except Exception as exc:  # noqa: BLE001
            unreal.log_warning(f"{TAG} could not set {prop}: {exc}")


def create_master():
    if eal.does_asset_exist(MASTER_PATH):
        unreal.log_warning(f"{TAG} deleting existing {MASTER_PATH}")
        eal.delete_asset(MASTER_PATH)

    mat = at.create_asset(MASTER_NAME, MASTER_DIR, unreal.Material, unreal.MaterialFactoryNew())
    if not mat:
        unreal.log_error(f"{TAG} FAILED to create master material")
        raise SystemExit(1)

    mat.set_editor_property("material_domain", unreal.MaterialDomain.MD_SURFACE)
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
    mat.set_editor_property("two_sided", False)
    _set_usage(mat)

    # BaseColor vector param (dark asphalt default)
    base = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -400, 0)
    base.set_editor_property("parameter_name", "BaseColor")
    base.set_editor_property("default_value", unreal.LinearColor(0.12, 0.13, 0.15, 1.0))
    mel.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)

    # Metallic
    metal = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -400, 200)
    metal.set_editor_property("parameter_name", "Metallic")
    metal.set_editor_property("default_value", 0.6)
    mel.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)

    # Roughness
    rough = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -400, 350)
    rough.set_editor_property("parameter_name", "Roughness")
    rough.set_editor_property("default_value", 0.28)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)

    mel.recompile_material(mat)
    _set_usage(mat)  # usage flags sometimes need post-recompile
    saved = eal.save_asset(MASTER_PATH, only_if_is_dirty=False)
    skel = bool(mat.get_editor_property("used_with_skeletal_mesh"))
    unreal.log_warning(
        f"{TAG} master saved={saved} UsedWithSkeletalMesh={skel} path={MASTER_PATH}"
    )
    if not skel:
        unreal.log_error(f"{TAG} ABORT: UsedWithSkeletalMesh still false after save")
        raise SystemExit(2)
    return mat


def create_mi(master):
    if eal.does_asset_exist(MI_PATH):
        unreal.log_warning(f"{TAG} deleting existing {MI_PATH}")
        eal.delete_asset(MI_PATH)

    factory = unreal.MaterialInstanceConstantFactoryNew()
    mi = at.create_asset(MI_NAME, MASTER_DIR, unreal.MaterialInstanceConstant, factory)
    if not mi:
        unreal.log_error(f"{TAG} FAILED to create MI")
        raise SystemExit(3)

    mel.set_material_instance_parent(mi, master)
    # Hellcat-ish orange optional default; runtime MID tints override anyway
    mel.set_material_instance_vector_parameter_value(
        mi, "BaseColor", unreal.LinearColor(1.0, 0.42, 0.08, 1.0)
    )
    mel.set_material_instance_scalar_parameter_value(mi, "Metallic", 0.78)
    mel.set_material_instance_scalar_parameter_value(mi, "Roughness", 0.18)
    saved = eal.save_asset(MI_PATH, only_if_is_dirty=False)
    unreal.log_warning(f"{TAG} MI saved={saved} path={MI_PATH} parent={MASTER_NAME}")
    return mi


def main():
    unreal.log_warning(f"{TAG} creating skeletal-safe body paint assets")
    master = create_master()
    create_mi(master)
    unreal.log_warning(f"{TAG} DONE — M_BodyPaint_SkeletalSafe + MI_ChargerBody_SkeletalSafe")


main()
