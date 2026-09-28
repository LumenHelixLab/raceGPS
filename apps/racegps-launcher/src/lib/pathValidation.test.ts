import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { DEFAULT_SETTINGS } from "@racegps/launcher-settings";
import { validateLauncherPaths } from "./pathValidation.ts";

test("marks missing package exe as awaiting build", () => {
  const missing = path.join(os.tmpdir(), "no-such-raceGPSRace.exe");
  const r = validateLauncherPaths(
    {
      ...DEFAULT_SETTINGS,
      raceMode: "package",
      paths: { ...DEFAULT_SETTINGS.paths, packageExe: missing },
    },
    fs.existsSync,
  );
  assert.equal(r.packageExeOk, false);
  assert.equal(r.awaitingBuild, true);
});

test("dev bat ok when exists", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rg-bat-"));
  const bat = path.join(dir, "LaunchClevelandRace.bat");
  fs.writeFileSync(bat, "@echo off\n");
  const r = validateLauncherPaths(
    {
      ...DEFAULT_SETTINGS,
      raceMode: "dev",
      paths: { ...DEFAULT_SETTINGS.paths, devBat: bat },
    },
    fs.existsSync,
  );
  assert.equal(r.devBatOk, true);
});

test("awaitingBuild false in dev mode even if package exe missing", () => {
  const missing = path.join(os.tmpdir(), "no-such-raceGPSRace.exe");
  const r = validateLauncherPaths(
    {
      ...DEFAULT_SETTINGS,
      raceMode: "dev",
      paths: { ...DEFAULT_SETTINGS.paths, packageExe: missing },
    },
    fs.existsSync,
  );
  assert.equal(r.packageExeOk, false);
  assert.equal(r.awaitingBuild, false);
});

test("chips include package awaiting build warn when exe missing", () => {
  const missing = path.join(os.tmpdir(), "no-such-raceGPSRace.exe");
  const r = validateLauncherPaths(
    {
      ...DEFAULT_SETTINGS,
      raceMode: "package",
      paths: { ...DEFAULT_SETTINGS.paths, packageExe: missing },
    },
    () => false,
  );
  const pkg = r.chips.find((c) => c.id === "package");
  assert.ok(pkg);
  assert.equal(pkg.tone, "warn");
  assert.match(pkg.label, /awaiting build/i);
});
