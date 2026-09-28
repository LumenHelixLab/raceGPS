import { useCallback, useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import type { LauncherSettings } from "@racegps/launcher-settings";
import { initialRoute } from "./lib/firstRun";
import { PlaceholderHome } from "./pages/PlaceholderHome";
import { SettingsPage } from "./pages/SettingsPage";
import { WizardPage } from "./pages/WizardPage";

export function App() {
  const [settings, setSettings] = useState<LauncherSettings | null>(null);
  const [bootError, setBootError] = useState<string | null>(null);

  useEffect(() => {
    void window.racegps
      .getSettings()
      .then(setSettings)
      .catch((err: unknown) =>
        setBootError(err instanceof Error ? err.message : String(err)),
      );
  }, []);

  const onWizardCompleted = useCallback((next: LauncherSettings) => {
    setSettings(next);
  }, []);

  if (bootError) {
    return (
      <main className="page">
        <h1>raceGPS Launcher</h1>
        <p className="error">Failed to load settings: {bootError}</p>
      </main>
    );
  }

  if (!settings) {
    return (
      <main className="page">
        <p>Loading…</p>
      </main>
    );
  }

  const home = initialRoute(settings);

  return (
    <Routes>
      <Route
        path="/wizard"
        element={
          settings.firstRunCompleted ? (
            <Navigate to="/" replace />
          ) : (
            <WizardPage onCompleted={onWizardCompleted} />
          )
        }
      />
      <Route
        path="/"
        element={
          settings.firstRunCompleted ? (
            <PlaceholderHome />
          ) : (
            <Navigate to="/wizard" replace />
          )
        }
      />
      <Route path="/settings" element={<SettingsPage />} />
      <Route path="*" element={<Navigate to={home} replace />} />
    </Routes>
  );
}
