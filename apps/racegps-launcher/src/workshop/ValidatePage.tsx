import { useState } from "react";
import { usePack } from "./PackContext";

function buildValidateArgv(packDir: string): string[] {
  return ["-m", "rgpack", "validate", packDir];
}

export function ValidatePage() {
  const { packDir } = usePack();
  const [running, setRunning] = useState(false);
  const [stdout, setStdout] = useState("");
  const [stderr, setStderr] = useState("");
  const [logPath, setLogPath] = useState("");
  const [code, setCode] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onValidate() {
    if (!packDir?.trim()) {
      setError("No pack open. Open a pack on Pack, or export one on Compile first.");
      return;
    }
    setRunning(true);
    setError(null);
    setStdout("");
    setStderr("");
    setLogPath("");
    setCode(null);
    try {
      const result = await window.racegps.runWorkshopCli(buildValidateArgv(packDir));
      setStdout(result.stdout);
      setStderr(result.stderr);
      setLogPath(result.logPath);
      setCode(result.code);
      if (!result.stderr && !result.stdout) {
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

  const verdict =
    code === null
      ? null
      : /\bRESULT\s+PASS\b/i.test(stdout)
        ? "PASS"
        : /\bRESULT\s+FAIL\b/i.test(stdout)
          ? "FAIL"
          : code === 0
            ? "PASS"
            : "FAIL";

  return (
    <section>
      <h1>Validate</h1>
      <p>
        {packDir
          ? `Validate pack: ${packDir}`
          : "No pack open. Validation is unavailable until a pack is selected."}
      </p>
      <div className="row">
        <button
          type="button"
          disabled={running || !packDir}
          onClick={() => void onValidate()}
        >
          {running ? "Validating…" : "Validate pack"}
        </button>
      </div>
      {error ? <p className="error">{error}</p> : null}
      {verdict ? (
        <p>
          RESULT <strong>{verdict}</strong> (exit {code})
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
    </section>
  );
}
