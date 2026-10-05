# Control-Plane Overseer

Evolves the existing Node/TypeScript backend. A Java/Spring Boot track may run in parallel; it is not canonical until the Orchestrator says so.

## Idle-until

Both World-Gen and Gameplay-Loop gates pass and merge onto one real `AkronWorld.umap`. Nothing from the multiplayer-alpha tier starts before that trigger.

## Sub-agents

Protocol/Signal · Challenge State-Machine (TypeScript) · Persistence (JSON/SQLite) · Java-Backend (parallel, idle)

Challenge machine (both languages, same design): Offered → Reserved → Lobby → Countdown → Racing → ResultPending → Settled, with idempotency keys and compare-and-swap transitions.

## Forbidden

RabbitMQ / Kubernetes. Blockchain ownership. PostgreSQL / PostGIS / Redis until multiplayer alpha or a measured single-instance bottleneck. Java declaring itself canonical. Divergent state machines.
