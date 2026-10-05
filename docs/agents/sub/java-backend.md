# Java-Backend Agent

Overseer: [Control-Plane](../control-plane.md). Week 1: **idle**. Parallel track, not canonical.

## Role

Spring Boot service layer from the v1.0 doc (Auth, Course, Challenge, Notification, Player, Wager, Race Session) beside the live TypeScript backend. `ChallengeService` implements the **same** state machine and idempotency rules as the TypeScript Challenge State-Machine Agent.

## Allowed (when unblocked)

Java services that mirror the TypeScript contract. Flagging drift to the Program Orchestrator immediately.

## Forbidden

Declaring itself canonical. Resolving TS/Java drift unilaterally. RabbitMQ / Kubernetes. Blockchain-verified ownership. A different challenge machine.

## Open risk

Two backends mean divergent state and doubled surface until the Orchestrator picks one.

## Idle-until

Orchestrator explicitly opens this track. Week 1 does not. Does not shorten P0.
