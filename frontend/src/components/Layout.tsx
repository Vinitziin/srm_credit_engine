import { NavLink, Outlet } from "react-router-dom";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `px-3 py-2 rounded-md text-sm font-medium transition ${
    isActive
      ? "bg-gray-800 text-white"
      : "text-gray-300 hover:bg-gray-800/50 hover:text-white"
  }`;

export function Layout() {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <header className="border-b border-gray-800 bg-gray-900">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-lg font-bold">SRM Credit Engine</h1>
            <p className="text-xs text-gray-500">
              Plataforma de cessão de crédito multimoedas
            </p>
          </div>
          <nav className="flex gap-1">
            <NavLink to="/" className={navLinkClass} end>
              Simulador
            </NavLink>
            <NavLink to="/statements" className={navLinkClass}>
              Extrato
            </NavLink>
            <NavLink to="/cedentes" className={navLinkClass}>
              Cedentes
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
