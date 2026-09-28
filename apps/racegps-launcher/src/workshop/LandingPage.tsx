import { usePack } from "./PackContext";

export function LandingPage() {
  const { packDir } = usePack();

  return (
    <section>
      <h1>Workshop</h1>
      <p>
        {packDir
          ? `Pack open: ${packDir}`
          : "No pack open. Start at Pack to choose a local workshop pack."}
      </p>
    </section>
  );
}
