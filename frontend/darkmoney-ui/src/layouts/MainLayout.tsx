import { Outlet, NavLink } from "react-router-dom";

export default function MainLayout() {
  return (
    <div>
      <header style={{ padding: "1rem", borderBottom: "1px solid #ddd" }}>
        <h2>Dark Money Project</h2>

        <nav style={{ display: "flex", gap: "1rem" }}>
          <NavLink to="/">Home</NavLink>
          <NavLink to="/donors">Donors</NavLink>
          <NavLink to="/recipients">Recipients</NavLink>
          <NavLink to="/topics">Topics</NavLink>
        </nav>
      </header>

      <main style={{ padding: "1rem" }}>
        <Outlet />
      </main>
    </div>
  );
}
