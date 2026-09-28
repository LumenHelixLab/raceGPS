export {
  LauncherSettingsSchema,
  LauncherPathsSchema,
  RaceModeSchema,
  LastLaunchSchema,
  parseSettings,
  type LauncherSettings,
  type RaceMode,
} from "./schema.ts";
export { DEFAULT_SETTINGS } from "./defaults.ts";
export { settingsFilePath } from "./paths.ts";
export { loadSettings, saveSettings, resetSettings } from "./io.ts";
