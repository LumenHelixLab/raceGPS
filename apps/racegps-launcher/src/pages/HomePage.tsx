import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import type { PathValidation } from "../lib/pathValidation";

export function HomePage() {
  const navigate = useNavigate();
  const [validation, setValidation] = useState<PathValidation | null>(null);
  const [launchDetail, setLaunchDetail] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      const v = (await window.racegps.validatePaths()) as PathValidation;
      setValidation(v);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function onPlayRace() {
    setBusy(true);
    setLaunchDetail(null);
    setError(null);
    try {
      const result = await window.racegps.launchRace();
      setLaunchDetail(result.detail);
      if (!result.ok) {
        await refresh();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  function onOpenWorkshop() {
    navigate("/workshop");
  }

  const awaitingBuild = validation?.awaitingBuild === true;

  return (
    <main className="page">
      <h1>raceGPS Launcher</h1>
      <p>Easy Test Beta — Cleveland Race home</p>

      {error ? <p className="error">{error}</p> : null}

      <div className="chips" aria-label="Path status">
        {validation?.chips.map((chip) => (
          <span key={chip.id} className={`chip chip-${chip.tone}`}>
            {chip.label}
          </span>
        ))}
        {!validation && !error ? <span className="chip chip-warn">Checking paths…</span> : null}
      </div>

      {awaitingBuild ? (
        <section className="cta-panel" role="status">
          <h2>Package not built yet</h2>
          <p>
            Package mode is awaiting build — use Dev mode or wait for Chris cook
            unlock. See docs/contracts/LAUNCHER_PATH_CONTRACT.md.
          </p>
        </section>
      ) : null}

      <div className="row">
        <button type="button" disabled={busy} onClick={() => void onPlayRace()}>
          Play Race
        </button>
        <button type="button" disabled={busy} onClick={onOpenWorkshop}>
          Open Workshop
        </button>
        <Link className="button-link" to="/settings">
          Settings
        </Link>
        <button type="button" disabled={busy} onClick={() => void refresh()}>
          Refresh status
        </button>
      </div>

      {launchDetail ? (
        <p className={awaitingBuild || launchDetail.toLowerCase().includes("awaiting") ? "error" : "status"}>
          {launchDetail}
        </p>
      ) : null}
    </main>
  );
}
