# CARLA-Embedding Agent

Overseer: [World-Gen](../world-gen.md). Week 1: **idle**. Alternate path, not canonical.

## Role

Embed `carla.Osm2Odr` and the CARLA UE5 vehicle/asset pack as a runtime dependency, running beside the Compiler Agent. Output still goes through XODR Validation and the truth gate. The Orchestrator decides which path ships.

## Allowed (when unblocked)

Streaming / batched OSM parsing. Stable `Osm2Odr` API (not the GUI tool) for dense areas. Bridge/tunnel pre-filter or esmini fallback. Spline-normal fix on import. Vehicle assets only after Provenance sign-off.

## Forbidden

Silent replacement of the Python compiler. Skipping XODR Validation or Provenance. Writing into `apps/unreal-akron-beta/Content` without the asset firewall. Treating documented CARLA failure modes as closed.

## Open risks (not resolved)

- OSM import memory overflow above ~50MB
- GUI tool crashes on dense areas
- No bridge / overpass support
- Inverted spline normals on conversion

## Idle-until

Orchestrator explicitly opens this track. Week 1 does not.
