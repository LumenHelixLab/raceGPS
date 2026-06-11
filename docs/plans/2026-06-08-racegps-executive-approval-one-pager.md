# raceGPS Executive Approval One-Pager

## Decision Request
Approve the raceGPS Akron Beta roadmap as a first-playable vertical slice program, with Milestone 1 as the hard go/no-go gate.

## What raceGPS is
raceGPS is a local-first street-racing game concept built on real-world city data. The current proof city is Akron. The core fantasy is simple:
- real roads
- clean onboarding
- route-based night driving
- selectable vehicle identity + handling style
- eventual social/community loop through routes, replays, leaderboards, and city sharing

## What already exists
The repo already contains credible product infrastructure:
- Unreal gameplay client
- citypack/compiler pipeline
- route/checkpoint support
- onboarding and preflight systems
- garage with vehicle class + handling mode split
- replay / ghost / leaderboard / traffic systems
- CityHub backend direction for sharing and community features

## What is not yet proven
The repo is not yet fully proven as a product because the core first-drive experience still depends on one editor-truth step:
- real `Content/Maps/AkronWorld.umap`
- successful menu -> spawn -> drive -> checkpoint -> tutorial PIE flow

## Why this matters now
The project is past the point where more architecture alone creates confidence.
The next stage must answer one question clearly:
Can a first-time user get into Akron and have a working, readable, premium-feeling first drive?

## Current assessment
- Concept credibility: High
- Architectural breadth: High
- First-playable proof: Incomplete
- Risk concentration: Mostly isolated to Unreal world assembly + first-drive execution

## Recommended roadmap
10 milestones are proposed, but they are not equal.

### Hard gate
1. Akron First-Drive Proof

### Product credibility layer
2. Main Menu Premium Pass
3. First-Run Onboarding Completion Flow
4. Vehicle Identity Pass
5. Route Readability Pass
6. Basic World Polish Pass

### Retention / expansion layer
7. Race Result / Feedback Loop
8. Replay / Ghost Slice
9. CityHub Integration Slice

### Final decision layer
10. Go / No-Go Vertical Slice Review

## Recommended approval structure
Approve the roadmap in 4 phases:
- Phase A: Milestones 1–3
- Phase B: Milestones 4–6
- Phase C: Milestones 7–9
- Phase D: Milestone 10

## Executive recommendation
Approve the roadmap, but enforce this rule:
- if Milestone 1 fails, pause the roadmap and re-evaluate
- if Milestone 1 succeeds, proceed immediately into polish and onboarding quality

## Approval statement
Approve raceGPS Akron Beta as a first-playable vertical slice initiative, with Milestone 1 serving as the primary viability gate and Milestones 2–3 as the immediate productization follow-through.
