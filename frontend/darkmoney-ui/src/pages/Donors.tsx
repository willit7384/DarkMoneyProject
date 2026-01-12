import { useEffect, useState } from "react";
import { fetchTopDonors } from "../api/donors";
import type { Donor } from "../types/donor";
import { Link } from "react-router-dom";

export default function Donors() {
  const [donors, setDonors] = useState<Donor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTopDonors()
      .then(setDonors)
      .catch(() => setError("Failed to load donors"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading donors…</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h2>Top Donors</h2>

      <table>
        <thead>
          <tr>
            <th>Donor</th>
            <th>Total Given</th>
            <th># Transactions</th>
          </tr>
        </thead>
        <tbody>
          {donors.map((d) => (
            <tr key={d.donor_name}>
              <td>
                <Link to={`/donors/${encodeURIComponent(d.donor_name)}`}>
                  {d.donor_name}
                </Link>
              </td>
              <td>${d.total_grants.toLocaleString()}</td>
              <td>{d.grant_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
