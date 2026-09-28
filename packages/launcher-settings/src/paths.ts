import path from "node:path";

export function settingsFilePath(appDataRoot?: string): string {
  const root = appDataRoot ?? process.env.APPDATA ?? "";
  if (!root) {
    throw new Error("APPDATA unset; pass appDataRoot explicitly");
  }
  return path.join(root, "raceGPS", "settings.json");
}
