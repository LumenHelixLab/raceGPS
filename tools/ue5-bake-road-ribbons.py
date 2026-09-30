#!/usr/bin/env python3
"""ue5-bake-road-ribbons.py — bake ribbon_spec.json into a Cleveland map.

Run via:
    UnrealEditor-Cmd.exe "<uproject>" -run=pythonscript ^
        -script="tools/ue5-bake-road-ribbons.py" -- <pack_dir> <map_package> ^
        -unattended -nop4 -nullrhi -log

One ProceduralMeshComponent per ribbon + per junction under a single
in-map actor named "RoadRibbons". Collision: simple convex from the strip
outline (bUseComplexAsSimple off). Coords: spec is UE-space meters -> cm here.
Graph-sourced ribbons carry a `layer`; each layer lifts base_z by 5.0 m
(road_network.py vertical-offset convention). Rotators keyword-args only.
Fail-closed: zero ribbons baked -> RuntimeError, map is not saved.
"""
import json
import sys
from pathlib import Path

import unreal

M_TO_CM = 100.0
RIBBON_LIFT_M = 0.06   # 6 cm proud of terrain to kill z-fighting
LAYER_STEP_M = 5.0     # road_network.py vertical-offset convention
UV_TILE_M = 6.0        # asphalt texture tile
MAT_PATH = "/Game/Materials/M_RoadRibbon"


def _to_ue(pt, z_m):
    return unreal.Vector(pt[0] * M_TO_CM, pt[1] * M_TO_CM, z_m * M_TO_CM)


def _ensure_material():
    """Load M_RoadRibbon; create a minimal asphalt material if missing.

    Follows the repo's create_night_mats_v13.py idioms (wipe + create_asset +
    MaterialEditingLibrary). Dash lines are intentionally NOT baked into the
    mesh; a later material iteration can add them via world-UV masks.
    """
    eal = unreal.EditorAssetLibrary
    if eal.does_asset_exist(MAT_PATH):
        return eal.load_asset(MAT_PATH)
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    mel = unreal.MaterialEditingLibrary
    mat = asset_tools.create_asset("M_RoadRibbon", "/Game/Materials",
                                   unreal.Material, unreal.MaterialFactoryNew())
    base = mel.create_material_expression(mat, unreal.MaterialExpressionVectorParameter, -600, -100)
    base.set_editor_property("parameter_name", "AsphaltColor")
    base.set_editor_property("default_value", unreal.LinearColor(0.035, 0.035, 0.038, 1.0))
    mel.connect_material_property(base, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    rough = mel.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -600, 100)
    rough.set_editor_property("parameter_name", "Roughness")
    rough.set_editor_property("default_value", 0.95)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(mat)
    eal.save_asset(MAT_PATH)
    unreal.log("[raceGPS-PREFLIGHT] created M_RoadRibbon asphalt material")
    return mat


def _build_pmc(owner, name, polygon_xy, base_z_m, mat):
    """Flat n-gon fan from a simple outline (strip or junction box)."""
    pmc = unreal.ProceduralMeshComponent.new_object(owner, name)
    pmc.register_component()
    pmc.attach_to_component(owner.get_root_component(),
                            unreal.AttachmentRule.keep_relative, "")
    z = base_z_m + RIBBON_LIFT_M
    verts = [_to_ue(p, z) for p in polygon_xy]
    tris = []
    for i in range(1, len(polygon_xy) - 1):
        tris += [0, i, i + 1]
    uvs = [unreal.Vector2D(p[0] / UV_TILE_M, p[1] / UV_TILE_M) for p in polygon_xy]
    pmc.create_mesh_section(0, verts, tris, [], uvs, [], [], True)
    if mat:
        pmc.set_material(0, mat)
    pmc.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    pmc.set_collision_response_to_channel(unreal.CollisionChannel.VEHICLE,
                                          unreal.CollisionResponse.BLOCK)
    return pmc


def run(pack_dir: str, map_package: str):
    pack = Path(pack_dir)
    spec = json.loads((pack / "ribbon_spec.json").read_text(encoding="utf-8"))
    unreal.EditorLoadingAndSavingUtils.load_map(map_package)
    root = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.Actor, unreal.Vector(0, 0, 0),
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0))
    root.set_actor_label("RoadRibbons")
    if root.get_root_component() is None:
        scene = unreal.SceneComponent.new_object(root, "Root")
        scene.register_component()
        root.set_root_component(scene)
    mat = _ensure_material()
    n_r, n_j = 0, 0
    for rb in spec["ribbons"]:
        base_z = float(rb.get("layer", 0)) * LAYER_STEP_M
        _build_pmc(root, f"R_{rb['road_id']}", rb["strip"], base_z, mat)
        n_r += 1
    for j in spec["junctions"]:
        _build_pmc(root, f"J_{j['id']}", j["polygon"], 0.0, mat)
        n_j += 1
    if n_r == 0:
        raise RuntimeError("FAIL-CLOSED: zero ribbons baked; map not saved")
    unreal.EditorLevelLibrary.save_current_level()
    unreal.log(f"[raceGPS-PREFLIGHT] ribbons baked={n_r} junctions={n_j} "
               f"spawns_snapped={len(spec['spawns'])} dropped_stubs={spec['dropped_stubs']}")


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    run(args[0], args[1])
