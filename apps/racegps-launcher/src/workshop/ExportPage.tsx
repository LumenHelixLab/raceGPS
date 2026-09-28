import { usePack } from "./PackContext";

export function ExportPage() {
  const { packDir } = usePack();

  return (
    <section>
      <h1>Export</h1>
      <p>
        {packDir
          ? `No export run yet for ${packDir}.`
          : "No pack open. Export is unavailable until a pack is selected."}
      </p>
      <p>Package mode is awaiting build until cook is unlocked.</p>
    </section>
  );
}
