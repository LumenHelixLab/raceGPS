# Research brief: Electron + Vite launcher scaffold (electron-vite)

**Date:** 2026-09-28 (America/New_York)  
**Author:** Unreal PM (idle research) / Grok Bot Task 2  
**Lane impacted:** Launcher

## Question

Which Electron+Vite toolchain should raceGPS use for `apps/racegps-launcher` so we get a typed React renderer, a Node main process, and a secure preload bridge for `@racegps/launcher-settings` without inventing a second web shell?

## Sources (with dates)

| Source | URL | Accessed | Notes |
|--------|-----|----------|-------|
| electron-vite Getting Started | https://electron-vite.org/guide/ | 2026-09-28 | CLI `dev`/`build`/`preview`; `main` → `./out/main/index.js`; Node 20.19+/22.12+; Vite 5+ |
| electron-vite Config | https://electron-vite.org/config/ | 2026-09-28 | `defineConfig` with `main` / `preload` / `renderer` |
| electron-vite Dependency Handling | https://electron-vite.org/guide/dependency-handling | 2026-09-28 | v5+: `build.externalizeDeps`; pre-v5: `externalizeDepsPlugin` |
| electron-vite Migration (v4→v5) | https://electron-vite.org/guide/migration | 2026-09-28 | `externalizeDepsPlugin` deprecated in v5 |
| electron-vite Vite 6 support issue | https://github.com/alex8088/electron-vite/issues/673 | 2026-09-28 | `electron-vite@2.3.0` peers `vite@^4 \|\| ^5` only; Vite 6 needs ≥3.0.0 |
| npm `electron-vite` peers | https://www.npmjs.com/package/electron-vite | 2026-09-28 | 3.1.0: vite ^4\|\|^5\|\|^6; 4.0.1/5.0.0: vite ^5\|\|^6\|\|^7; latest published 5.0.0 (6.x still beta) |
| create-electron React-TS template | https://electron-vite.org/guide/ (Scaffolding) | 2026-09-28 | `npm create @quick-start/electron@latest -- --template react-ts` |

## Findings

- Task brief pins `electron-vite@^2.3.0` + `vite@^6.0.6`, but **2.3.0 cannot resolve Vite 6 peers** (npm ERESOLVE); Vite 6 support landed in **electron-vite 3.0.0**.
- Brief config uses `externalizeDepsPlugin()`, which remains available through **3.x/4.x** and is **deprecated (replaced by `build.externalizeDeps`) in 5.0**.
- Official layout defaults to `src/main|preload|renderer`; brief’s `electron/main.ts` + `electron/preload.ts` + root `index.html` is valid via custom `build.rollupOptions.input`.
- Preload must keep `contextIsolation: true` / `nodeIntegration: false`; expose only `window.racegps.*` via `contextBridge`.
- Workspace package `@racegps/launcher-settings` exports **TypeScript sources** (`./src/index.ts`). If externalized, Electron cannot load `.ts` at runtime — **exclude it from externalize** so Vite bundles it into main.
- `@racegps/ui-kit` is CSS-only (`main: tokens.css`, no `exports`); prefer relative `@import` if package subpath fails.
- Tauri rejected unless Electron install is blocked (constraint / brief alternative only).

## Recommend / Reject

**Recommend:** `electron-vite@^3.1.0` with brief’s `externalizeDepsPlugin` config (Vite 6 compatible; plugin still present), React 19 + `react-router-dom` 7, Electron ^33, settings IPC wired to `settingsFilePath(app.getPath('appData'))`. Exclude `@racegps/launcher-settings` from externalize.  
**Reject:** Strict `electron-vite@^2.3.0` with Vite 6 (peer conflict); Tauri (not needed); Electron main loading TS workspace package unbundled.  
**Why:** Unblocks Task 2 scaffold with installable deps and a working AppData settings contract while staying closest to the brief’s API shape.
