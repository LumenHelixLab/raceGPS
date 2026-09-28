import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import {
  DEFAULT_SETTINGS,
  loadSettings,
  parseSettings,
  resetSettings,
  saveSettings,
  settingsFilePath,
} from "../src/index.ts";

test("parseSettings accepts canonical shape", () => {
  const s = parseSettings(DEFAULT_SETTINGS);
  assert.equal(s.schemaVersion, 1);
  assert.equal(s.raceMode, "package");
  assert.equal(s.firstRunCompleted, false);
  assert.equal(s.paths.devBat.includes("LaunchClevelandRace.bat"), true);
});

test("parseSettings rejects bad raceMode", () => {
  assert.throws(() => parseSettings({ ...DEFAULT_SETTINGS, raceMode: "editor" }));
});

test("settingsFilePath joins AppData/raceGPS/settings.json", () => {
  const p = settingsFilePath("D:\\AppData");
  assert.equal(p, path.join("D:\\AppData", "raceGPS", "settings.json"));
});

test("loadSettings returns defaults when file missing", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rg-settings-"));
  const file = path.join(dir, "settings.json");
  const s = loadSettings(file);
  assert.deepEqual(s, DEFAULT_SETTINGS);
});

test("saveSettings + loadSettings round-trip", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rg-settings-"));
  const file = path.join(dir, "settings.json");
  const next = {
    ...DEFAULT_SETTINGS,
    firstRunCompleted: true,
    raceMode: "dev" as const,
    gpuNote: "RTX",
  };
  saveSettings(file, next);
  assert.deepEqual(loadSettings(file), next);
});

test("resetSettings writes defaults", () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rg-settings-"));
  const file = path.join(dir, "settings.json");
  saveSettings(file, { ...DEFAULT_SETTINGS, firstRunCompleted: true });
  const s = resetSettings(file);
  assert.equal(s.firstRunCompleted, false);
  assert.deepEqual(loadSettings(file), DEFAULT_SETTINGS);
});
