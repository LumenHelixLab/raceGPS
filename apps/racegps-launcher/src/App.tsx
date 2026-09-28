import { useCallback, useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import type { LauncherSettings } from "@racegps/launcher-settings";
import { initialRoute } from "./lib/firstRun";
import { HomePage } from "./pages/HomePage";
import { SettingsPage } from "./pages/SettingsPage";
import { WizardPage } from "./pages/WizardPage";
import { CompilePage } from "./workshop/CompilePage";
import { ExportPage } from "./workshop/ExportPage";
import { LandingPage } from "./workshop/LandingPage";
import { PackPage } from "./workshop/PackPage";
import { ValidatePage } from "./workshop/ValidatePage";
import { WorkshopLayout } from "./workshop/WorkshopLayout";

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
        <p>Loading.</p>
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
            <HomePage />
          ) : (
            <Navigate to="/wizard" replace />
          )
        }
      />
      <Route path="/settings" element={<SettingsPage />} />
      <Route
        path="/workshop"
        element={<WorkshopLayout worktreeRoot={settings.paths.worktreeRoot} />}
      >
        <Route index element={<LandingPage />} />
        <Route path="pack" element={<PackPage />} />
        <Route path="compile" element={<CompilePage />} />
        <Route path="validate" element={<ValidatePage />} />
        <Route path="export" element={<ExportPage />} />
      </Route>
      <Route path="*" element={<Navigate to={home} replace />} />
    </Routes>
  );
}
