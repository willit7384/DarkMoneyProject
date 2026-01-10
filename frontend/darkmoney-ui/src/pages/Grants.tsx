import { useEffect, useState } from "react";
import api from "../api/client";
import type { Grant } from "../types"

export default function Grants() {
  const [grants, setGrants] = useState<Grant[]>([]);

  useEffect(() => {
    api.get("/grants?min_amount=10000")
      .then(res => setGrants(res.data))
      .catch(console.error);
  }, []);

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Grant Network</h2>
      <table>
        <thead>
          <tr>
            <th>Source</th>
            <th>Target</th>
            <th>Amount</th>
            <th>Year</th>
          </tr>
        </thead>
        <tbody>
          {grants.map((g, i) => (
            <tr key={i}>
              <td>{g.source_org}</td>
              <td>{g.target_org}</td>
              <td>${g.amount.toLocaleString()}</td>
              <td>{g.tax_year}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
