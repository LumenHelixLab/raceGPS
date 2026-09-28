import path from "node:path";
import test from "node:test";
import assert from "node:assert/strict";
import { settingsFilePath } from "@racegps/launcher-settings";

test("settingsFilePath matches AppData/raceGPS/settings.json contract", () => {
  const p = settingsFilePath("C:\\Users\\test\\AppData\\Roaming");
  assert.equal(p, path.join("C:\\Users\\test\\AppData\\Roaming", "raceGPS", "settings.json"));
});
