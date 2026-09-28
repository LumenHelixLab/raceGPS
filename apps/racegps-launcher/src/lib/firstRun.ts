import type { LauncherSettings } from "@racegps/launcher-settings";

export function initialRoute(settings: LauncherSettings): "/wizard" | "/" {
  return settings.firstRunCompleted ? "/" : "/wizard";
}
