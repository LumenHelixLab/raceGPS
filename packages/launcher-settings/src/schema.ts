import { z } from "zod";

export const RaceModeSchema = z.enum(["package", "dev"]);
export type RaceMode = z.infer<typeof RaceModeSchema>;

export const LauncherPathsSchema = z.object({
  worktreeRoot: z.string().min(1),
  devBat: z.string().min(1),
  packageExe: z.string().min(1),
  workshopPython: z.string().min(1),
  uproject: z.string().min(1),
  logDir: z.string().min(1),
});

export const LastLaunchSchema = z.object({
  target: z.enum(["race", "workshop"]).nullable(),
  at: z.string().nullable(),
  ok: z.boolean().nullable(),
});

export const LauncherSettingsSchema = z.object({
  schemaVersion: z.literal(1),
  raceMode: RaceModeSchema,
  paths: LauncherPathsSchema,
  gpuNote: z.string(),
  firstRunCompleted: z.boolean(),
  lastLaunch: LastLaunchSchema,
});

export type LauncherSettings = z.infer<typeof LauncherSettingsSchema>;

export function parseSettings(data: unknown): LauncherSettings {
  return LauncherSettingsSchema.parse(data);
}
