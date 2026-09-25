"""Attach CARLA DodgeCharger2024 door static meshes to BP_DodgeCharger2024.

Run:
  UnrealEditor-Cmd.exe <uproject> -ExecutePythonScript=<this file> -unattended -NullRHI
"""
import unreal

BP_PATH = "/Game/Vehicles/DodgeCharger2024/BP_DodgeCharger2024"
DOOR_MESHES = {
    "Door_FL": "/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/SM_DodgeCharger2024_DoorFL.SM_DodgeCharger2024_DoorFL",
    "Door_FR": "/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/SM_DodgeCharger2024_DoorFR.SM_DodgeCharger2024_DoorFR",
    "Door_RL": "/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/SM_DodgeCharger2024_DoorRL.SM_DodgeCharger2024_DoorRL",
    "Door_RR": "/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/SM_DodgeCharger2024_DoorRR.SM_DodgeCharger2024_DoorRR",
}
# Alternate bone name spellings seen in CARLA phys assets
BONE_ALIASES = {
    "Door_FL": ["Door_FL", "door_fl", "DoorFL", "Door_Front_Left", "door_front_left"],
    "Door_FR": ["Door_FR", "door_fr", "DoorFR", "Door_Front_Right", "door_front_right"],
    "Door_RL": ["Door_RL", "door_rl", "DoorRL", "Door_Back_Left", "door_rear_left", "Door_Rear_Left"],
    "Door_RR": ["Door_RR", "door_rr", "DoorRR", "Door_Back_Right", "door_rear_right", "Door_Rear_Right"],
}

def log(msg):
    unreal.log_warning("[attach_charger_doors] " + msg)

def find_bone(skel_mesh, aliases):
    if not skel_mesh:
        return None
    names = [str(n) for n in skel_mesh.get_editor_property("skeleton").get_editor_property("bone_tree")] if False else None
    # Prefer socket/bone query via skeletal mesh component API later; list ref skeleton bones:
    try:
        skel = skel_mesh.skeleton
        # UE5 python: get_bone_names via reference skeleton
        ref = skel.get_reference_skeleton() if hasattr(skel, "get_reference_skeleton") else None
    except Exception:
        ref = None
    # Fallback: try each alias with exists check on mesh
    for a in aliases:
        # skeletal_mesh.find_bone_index if available
        try:
            idx = skel_mesh.get_bone_index(unreal.Name(a)) if hasattr(skel_mesh, "get_bone_index") else -1
            if idx is not None and int(idx) >= 0:
                return a
        except Exception:
            pass
    return aliases[0]  # still attempt attach; engine will warn

def main():
    # Verify door meshes load
    for key, path in DOOR_MESHES.items():
        m = unreal.EditorAssetLibrary.load_asset(path.split(".")[0])
        if not m:
            log("MISSING mesh %s at %s" % (key, path))
            return False
        log("OK mesh %s -> %s" % (key, m.get_name()))

    bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
    if not bp:
        log("MISSING BP %s" % BP_PATH)
        return False

    # Use SubobjectDataSubsystem / BlueprintEditorLibrary where available
    try:
        subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    except Exception as e:
        log("No SubobjectDataSubsystem: %s — will try legacy SCSeditor" % e)
        subsystem = None

    # Load generated class / skeletal mesh from CDO
    gen = bp.generated_class if hasattr(bp, "generated_class") else None
    if not gen:
        # Blueprint asset
        try:
            gen = unreal.EditorAssetLibrary.load_blueprint_class(BP_PATH)
        except Exception:
            gen = None
    cdo = unreal.get_default_object(gen) if gen else None
    skel_comp = None
    skel_mesh = None
    if cdo:
        try:
            skel_comp = cdo.get_editor_property("mesh") or cdo.get_component_by_class(unreal.SkeletalMeshComponent)
        except Exception:
            try:
                skel_comp = cdo.get_component_by_class(unreal.SkeletalMeshComponent)
            except Exception as e:
                log("CDO mesh lookup failed: %s" % e)
        if skel_comp:
            try:
                skel_mesh = skel_comp.skeletal_mesh
            except Exception:
                skel_mesh = None
    log("BP loaded gen=%s skel_mesh=%s" % (bool(gen), skel_mesh.get_name() if skel_mesh else None))

    # List bones containing door
    if skel_mesh and hasattr(skel_mesh, "get_all_morph_target_names"):
        pass
    # Dump bone names via animation library if possible
    bone_dump = []
    try:
        # unreal.AnimationLibrary or skeletal mesh editor
        import re
        # Phys asset probe path
        phys = unreal.EditorAssetLibrary.load_asset("/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/Phys_DodgeCharger2024")
        if phys:
            for s in phys.skeletal_body_setups:
                n = str(s.bone_name)
                if "door" in n.lower():
                    bone_dump.append(n)
                    log("phys door bone=%s" % n)
    except Exception as e:
        log("phys probe: %s" % e)

    # Prefer SimpleConstructionScript add via AssetTools — UE 5.4+ Subobject API
    attached = 0
    if subsystem is not None:
        try:
            handles = subsystem.k2_gather_subobject_data_for_blueprint(bp)
            # Find Mesh component handle
            mesh_handle = None
            existing = []
            for h in handles:
                data = subsystem.k2_find_subobject_data_from_handle(h) if hasattr(subsystem, "k2_find_subobject_data_from_handle") else None
                # alternate API
                try:
                    name = str(unreal.SubobjectDataBlueprintFunctionLibrary.get_variable_name(h))
                except Exception:
                    try:
                        name = str(h)
                    except Exception:
                        name = "?"
                existing.append(name)
                if name in ("Mesh", "VehicleMesh", "SkeletalMeshComponent0"):
                    mesh_handle = h
            log("subobjects: %s" % ", ".join(existing[:40]))
            for door_key, mesh_path in DOOR_MESHES.items():
                comp_name = "SM_" + door_key
                # skip if already present
                if any(comp_name == n or door_key in n for n in existing):
                    log("already have %s" % comp_name)
                    attached += 1
                    continue
                parent = mesh_handle if mesh_handle is not None else (handles[0] if handles else None)
                if parent is None:
                    log("no parent handle for %s" % door_key)
                    continue
                params = unreal.AddNewSubobjectParams()
                params.parent_handle = parent
                params.new_class = unreal.StaticMeshComponent
                params.blueprint_context = bp
                new_handle, fail_reason = subsystem.add_new_subobject(params)
                if fail_reason and str(fail_reason) not in ("", "None"):
                    log("add %s fail: %s" % (door_key, fail_reason))
                    continue
                subsystem.rename_subobject(new_handle, unreal.Text(comp_name))
                # Attach to bone
                bone = find_bone(skel_mesh, BONE_ALIASES[door_key])
                if bone_dump:
                    # pick best match from phys dump
                    for b in bone_dump:
                        bl = b.lower().replace(" ", "")
                        if door_key[-2:].lower() in bl or door_key.replace("_", "").lower() in bl:
                            bone = b
                            break
                try:
                    unreal.SubobjectDataBlueprintFunctionLibrary.set_attachment(new_handle, parent, unreal.Name(bone or "root"))
                except Exception as e:
                    log("attach API: %s — trying socket name only" % e)
                # Set static mesh on the template component
                try:
                    obj = unreal.SubobjectDataBlueprintFunctionLibrary.get_object_for_blueprint(new_handle, bp)
                    sm = unreal.EditorAssetLibrary.load_asset(mesh_path.split(".")[0])
                    if obj and sm:
                        obj.set_editor_property("static_mesh", sm)
                        obj.set_editor_property("collision_enabled", unreal.CollisionEnabled.NO_COLLISION)
                        attached += 1
                        log("attached %s bone=%s mesh=%s" % (comp_name, bone, sm.get_name()))
                except Exception as e:
                    log("set mesh failed %s: %s" % (door_key, e))
            unreal.EditorAssetLibrary.save_loaded_asset(bp)
            log("saved BP attached=%d" % attached)
            return attached >= 4
        except Exception as e:
            log("Subobject path failed: %s" % e)

    log("FALLBACK: write attach recipe only — open BP and add 4 StaticMeshComponents manually")
    recipe = "docs/superpowers/investigations/2026-09-24-charger-door-attach-recipe.md"
    return False

if __name__ == "__main__":
    ok = main()
    log("RESULT ok=%s" % ok)
