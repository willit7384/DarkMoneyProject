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
      .catch(() => setError("Failed to load top donors. Please try again later."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading top donors...</p>
      </div>
    );
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="page-container">
      <header className="page-header">
        <h1>Top Donors</h1>
        <p className="subtitle">
          Organizations giving the most in grants (based on available 990 data)
        </p>
      </header>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Donor Organization</th>
              <th className="numeric">Total # of Grants</th>
              <th className="numeric">Total $ Given</th>
            </tr>
          </thead>
          <tbody>
            {donors.map((donor) => (
              <tr key={donor.donor_name} className="hover-row">
                <td className="name-cell">
                  <Link to={`/donors/${encodeURIComponent(donor.donor_name)}`}>
                    {donor.donor_name}
                  </Link>
                </td>
                <td className="numeric">
                  {donor.total_grants.toLocaleString("en-US", {
                    minimumFractionDigits: 0,
                  })}
                </td>
                <td className="numeric">${donor.grant_count.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {donors.length === 0 && (
          <p className="no-data">No donor data available at this time.</p>
        )}
      </div>

      <footer className="table-footer">
        Showing top {donors.length} donors
      </footer>
    </div>
  );
}