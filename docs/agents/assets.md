# Offline Asset-Research Overseer

Firewall. Keeps CARLA / HY-World / Articraft / Landscape Combinator on the offline side of the line, except where CARLA-Embedding is explicitly authorized as a runtime world-gen **candidate**.

## Sub-agents

Asset-Adapters (one per tool, under `tools/asset-adapters/`) · Provenance

## Rule

No write into `apps/unreal-akron-beta/Content` without a passed license / geometry / scale / collision / rig check **and** Provenance sign-off. That includes CARLA vehicles destined for Vehicle/Physics.

## Idle-until

Async, no deadline pressure. Week 1: idle. Does not block Compiler or Race-Loop.
