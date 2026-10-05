# Build/PIE Agent

Overseer: [Verification](../verification.md). This agent’s pass/fail **is** the P0 / Section 2.2 gate.

## Role

Dev Editor compile, PIE smoke test, packaged Win64 build.

## Week 1 scope

May smoke the **placeholder** gameplay loop only. Packaged Win64 and real `AkronWorld.umap` stay closed.

## Forbidden

Recording a pass when the UE 5.5 editor is missing. Closing Section 2.2 on C++ tests alone. Engine 5.7.

## Idle-until

Race-Loop and/or Geometry-Import produce an artifact to put through the gate.
