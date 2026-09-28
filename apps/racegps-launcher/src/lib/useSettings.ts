import { useCallback, useEffect, useState } from "react";
import type { LauncherSettings } from "@racegps/launcher-settings";

export type UseSettingsResult = {
  settings: LauncherSettings | null;
  loading: boolean;
  error: string | null;
  save: (next: LauncherSettings) => Promise<void>;
  reset: () => Promise<LauncherSettings>;
  reload: () => Promise<void>;
};

export function useSettings(): UseSettingsResult {
  const [settings, setSettings] = useState<LauncherSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const next = await window.racegps.getSettings();
      setSettings(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  const save = useCallback(async (next: LauncherSettings) => {
    await window.racegps.saveSettings(next);
    setSettings(next);
  }, []);

  const reset = useCallback(async () => {
    const next = await window.racegps.resetSettings();
    setSettings(next);
    return next;
  }, []);

  return { settings, loading, error, save, reset, reload };
}
