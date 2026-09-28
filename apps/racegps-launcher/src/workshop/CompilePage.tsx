import { useOutletContext } from "react-router-dom";
import { useState } from "react";
import { usePack } from "./PackContext";
import { suggestedPackPath } from "./PackPage";
import type { WorkshopOutletContext } from "./WorkshopLayout";

function buildExportArgv(outDir: string, packId: string): string[] {
  return [
    "-m",
    "rgpack",
    "export-overpass",
    "--fixture",
    "-o",
    outDir,
    "--pack-id",
    packId,
  ];
}

export function CompilePage() {
  const { packDir, setPackDir } = usePack();
  const { worktreeRoot } = useOutletContext<WorkshopOutletContext>();
  const defaultOut = suggestedPackPath(worktreeRoot);
  const [running, setRunning] = useState(false);
  const [stdout, setStdout] = useState("");
  const [stderr, setStderr] = useState("");
  const [logPath, setLogPath] = useState("");
  const [code, setCode] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onExportFixture() {
    setRunning(true);
    setError(null);
    setStdout("");
    setStderr("");
    setLogPath("");
    setCode(null);
    const outDir = packDir?.trim() || defaultOut;
    const packId = outDir.split(/[\\/]/).filter(Boolean).pop() || "burke_overpass_proof_v1";
    const argv = buildExportArgv(outDir, packId);
    try {
      const result = await window.racegps.runWorkshopCli(argv);
      setStdout(result.stdout);
      setStderr(result.stderr);
      setLogPath(result.logPath);
      setCode(result.code);
      const pass =
        result.code === 0 && /\bRESULT\s+PASS\b/i.test(result.stdout);
      if (pass) {
        setPackDir(outDir);
      } else if (!result.stderr && !result.stdout) {
        setError(
          `CLI silent fail (code ${result.code}). Check log: ${result.logPath || "(none)"}`,
        );
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setRunning(false);
    }
  }

  return (
    <section>
      <h1>Compile</h1>
      <p>
        Offline Burke fixture → rgpack (no Unreal, no live Overpass). Output:{" "}
        <code>{packDir?.trim() || defaultOut}</code>
      </p>
      <div className="row">
        <button type="button" disabled={running} onClick={() => void onExportFixture()}>
          {running ? "Exporting…" : "Export Burke offline fixture → rgpack"}
        </button>
      </div>
      {error ? <p className="error">{error}</p> : null}
      {code !== null ? (
        <p>
          Exit code: {code}
          {/\bRESULT\s+PASS\b/i.test(stdout)
            ? " — RESULT PASS"
            : /\bRESULT\s+FAIL\b/i.test(stdout)
              ? " — RESULT FAIL"
              : code === 0
                ? ""
                : " — FAIL"}
        </p>
      ) : null}
      {logPath ? (
        <p>
          Log: <code>{logPath}</code>
        </p>
      ) : null}
      {stdout ? (
        <pre aria-label="CLI stdout">{stdout}</pre>
      ) : null}
      {stderr ? (
        <pre aria-label="CLI stderr" className="error">
          {stderr}
        </pre>
      ) : null}
      {!running && code === null && !error ? (
        <p>
          {packDir
            ? `Pack open: ${packDir}. Re-export will overwrite that directory.`
            : "No pack open yet — export will create the suggested path and set it as the open pack on PASS."}
        </p>
      ) : null}
    </section>
  );
}
