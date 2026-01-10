import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/client";
import type { Filing } from "../types"

export default function Filings() {
  const { ein } = useParams();
  const [filings, setFilings] = useState<Filing[]>([]);


  useEffect(() => {
    api.get(`/filings/${ein}`)
      .then(res => setFilings(res.data))
      .catch(console.error);
  }, [ein]);

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Filings for EIN {ein}</h2>
      <table>
        <thead>
          <tr>
            <th>Year</th>
            <th>Revenue</th>
            <th>Admin Expense</th>
          </tr>
        </thead>
        <tbody>
          {filings.map(f => (
            <tr key={f.ein}>
              <td>{f.tax_year}</td>
              <td>${f.total_revenue?.toLocaleString()}</td>
              <td>${f.admin_expense?.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
