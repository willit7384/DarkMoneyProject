import { useEffect, useState } from "react";
import { fetchTopRecipients } from "../api/recipients";
import type { Recipient } from "../types/recipient";
import { Link } from "react-router-dom";

export default function Recipients() {
  const [recipients, setRecipients] = useState<Recipient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTopRecipients()
      .then(setRecipients)
      .catch(() => setError("Failed to load top recipients. Please try again later."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading top recipients...</p>
      </div>
    );
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="page-container">
      <header className="page-header">
        <h1>Top Recipients</h1>
        <p className="subtitle">
          Organizations receiving the most grant funding
        </p>
      </header>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Recipient Organization</th>
              <th className="numeric">Total Received</th>
              <th className="numeric">Grant Count</th>
            </tr>
          </thead>
          <tbody>
            {recipients.map((recipient) => (
              <tr key={recipient.recipient_name} className="hover-row">
                <td className="name-cell">
                  <Link
                    to={`/recipients/${encodeURIComponent(recipient.recipient_name)}`}
                  >
                    {recipient.recipient_name}
                  </Link>
                </td>
                <td className="numeric">
                  ${recipient.total_grants.toLocaleString("en-US", {
                    minimumFractionDigits: 0,
                  })}
                </td>
                <td className="numeric">{recipient.grant_count.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {recipients.length === 0 && (
          <p className="no-data">No recipient data available at this time.</p>
        )}
      </div>

      <footer className="table-footer">
        Showing top {recipients.length} recipients
      </footer>
    </div>
  );
}