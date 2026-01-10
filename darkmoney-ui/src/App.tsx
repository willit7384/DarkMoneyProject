import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Organizations from "./pages/Organizations";
import Filings from "./pages/Filings";
import Grants from "./pages/Grants";

export default function App() {
  return (
    <BrowserRouter>
      <nav style={{ padding: "1rem", borderBottom: "1px solid #ccc" }}>
        <Link to="/">Organizations</Link> |{" "}
        <Link to="/grants">Grants</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Organizations />} />
        <Route path="/filings/:ein" element={<Filings />} />
        <Route path="/grants" element={<Grants />} />
      </Routes>
    </BrowserRouter>
  );
}
