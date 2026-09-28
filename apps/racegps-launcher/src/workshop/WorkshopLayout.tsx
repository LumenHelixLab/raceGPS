import { Link, NavLink, Outlet } from "react-router-dom";
import { PackProvider } from "./PackContext";

export type WorkshopLayoutProps = {
  worktreeRoot: string;
};

export type WorkshopOutletContext = {
  worktreeRoot: string;
};

const links = [
  { label: "Landing", to: "/workshop", end: true },
  { label: "Pack", to: "/workshop/pack", end: false },
  { label: "Compile", to: "/workshop/compile", end: false },
  { label: "Validate", to: "/workshop/validate", end: false },
  { label: "Export", to: "/workshop/export", end: false },
] as const;

export function WorkshopLayout({ worktreeRoot }: WorkshopLayoutProps) {
  return (
    <PackProvider>
      <main className="page">
        <nav aria-label="Workshop steps" className="row">
          {links.map((link) => (
            <NavLink
              className="button-link"
              end={link.end}
              key={link.to}
              to={link.to}
            >
              {link.label}
            </NavLink>
          ))}
          <Link className="button-link" to="/">
            Back to Launcher
          </Link>
        </nav>
        <Outlet context={{ worktreeRoot } satisfies WorkshopOutletContext} />
      </main>
    </PackProvider>
  );
}
