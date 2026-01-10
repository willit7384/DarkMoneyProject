import { useEffect, useState } from "react";
import api from "../api/client";
import { Link } from "react-router-dom";
import type { Organization } from "../types"

export default function Organizations() {
  const [orgs, setOrgs] = useState<Organization[]>([]);

  useEffect(() => {
    api.get("/organizations?limit=100")
      .then(res => setOrgs(res.data))
      .catch(console.error);
  }, []);

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Organizations</h2>
      <ul>
        {orgs.map(org => (
          <li key={org.ein}>
            <Link to={`/filings/${org.ein}`}>
              {org.name} ({org.state})
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
