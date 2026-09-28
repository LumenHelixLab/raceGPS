import { Link } from "react-router-dom";

export function PlaceholderHome() {
  return (
    <main className="page">
      <h1>raceGPS Launcher</h1>
      <p>Scaffold OK. Wizard complete — Home land in Task 4.</p>
      <p>
        <Link to="/settings">Settings</Link>
      </p>
    </main>
  );
}
