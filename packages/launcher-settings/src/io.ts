import fs from "node:fs";
import path from "node:path";
import { DEFAULT_SETTINGS } from "./defaults.ts";
import { parseSettings, type LauncherSettings } from "./schema.ts";

export function loadSettings(filePath: string): LauncherSettings {
  if (!fs.existsSync(filePath)) {
    return structuredClone(DEFAULT_SETTINGS);
  }
  const raw = JSON.parse(fs.readFileSync(filePath, "utf8"));
  return parseSettings(raw);
}

export function saveSettings(filePath: string, settings: LauncherSettings): void {
  const parsed = parseSettings(settings);
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(parsed, null, 2) + "\n", "utf8");
}

export function resetSettings(filePath: string): LauncherSettings {
  const defaults = structuredClone(DEFAULT_SETTINGS);
  saveSettings(filePath, defaults);
  return defaults;
}
