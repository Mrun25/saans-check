import { useEffect, useState } from "react";
import { getHotspots } from "../api";

export default function Dashboard() {
  const [hotspots, setHotspots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getHotspots()
      .then(setHotspots)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="dashboard">
      <header className="dash-header">
        <h1>Saans Check — Camp Prioritization</h1>
        <p className="dash-sub">
          Sites ranked by elevated-pattern rate. This is aggregate data only — no individual
          worker results, audio, or identifying information are included anywhere in this view.
        </p>
      </header>

      {loading && <p className="dash-loading">Loading...</p>}
      {error && <p className="dash-error">Error: {error}</p>}

      {!loading && !error && hotspots.length === 0 && (
        <p className="dash-empty">
          No site aggregates yet. Aggregates appear here once a site has at least 5 submissions
          and the rollup job has run.
        </p>
      )}

      {!loading && !error && hotspots.length > 0 && (
        <table className="hotspot-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Site</th>
              <th>District</th>
              <th>Submissions</th>
              <th>Elevated rate</th>
              <th>Avg years exposure</th>
              <th>Never wear mask</th>
              <th>No dust control</th>
            </tr>
          </thead>
          <tbody>
            {hotspots.map((h, i) => (
              <tr key={h.site_id} className={i === 0 ? "top-priority" : ""}>
                <td>{i + 1}</td>
                <td>{h.site_code}</td>
                <td>{h.district}</td>
                <td>{h.total_submissions}</td>
                <td>
                  <span className="rate-pill">{h.elevated_rate_pct}%</span>
                </td>
                <td>{h.avg_years_exposure ?? "—"}</td>
                <td>{h.pct_never_mask != null ? `${h.pct_never_mask}%` : "—"}</td>
                <td>{h.pct_no_dust_suppression != null ? `${h.pct_no_dust_suppression}%` : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <footer className="dash-footnote">
        <strong>Reminder:</strong> "elevated rate" reflects the Stage-1 proxy classifier (trained
        on public TB/COVID datasets), not a silicosis-validated model. Use this to prioritize
        which sites get the next X-ray/spirometry camp sooner — not as a diagnosis of any
        individual or site.
      </footer>

      <style>{`
        .dashboard {
          font-family: var(--font-display, system-ui, sans-serif);
          max-width: 1000px;
          margin: 0 auto;
          padding: 32px 24px 60px;
          color: var(--ink, #2a1d15);
        }
        .dash-header h1 {
          font-size: 1.6rem;
          margin: 0 0 6px;
          color: var(--sandstone-800, #5e3320);
        }
        .dash-sub {
          color: var(--sandstone-600, #9c5a34);
          font-size: 0.95rem;
          max-width: 640px;
          line-height: 1.5;
        }
        .dash-loading, .dash-empty {
          color: var(--sandstone-600, #9c5a34);
          margin-top: 24px;
        }
        .dash-error { color: #b3502f; margin-top: 24px; }
        .hotspot-table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 28px;
          font-size: 0.95rem;
        }
        .hotspot-table th {
          text-align: left;
          padding: 10px 12px;
          background: var(--sandstone-100, #f3e3cc);
          color: var(--sandstone-800, #5e3320);
          border-bottom: 2px solid var(--sandstone-200, #e6c79b);
        }
        .hotspot-table td {
          padding: 12px;
          border-bottom: 1px solid var(--sandstone-100, #f3e3cc);
        }
        .top-priority { background: rgba(179, 80, 47, 0.06); }
        .rate-pill {
          background: var(--sandstone-200, #e6c79b);
          color: var(--terracotta-dark, #8a3a21);
          padding: 4px 10px;
          border-radius: 999px;
          font-weight: 700;
          font-size: 0.88rem;
        }
        .dash-footnote {
          margin-top: 36px;
          font-size: 0.85rem;
          color: var(--sandstone-600, #9c5a34);
          border-top: 1px solid var(--sandstone-200, #e6c79b);
          padding-top: 16px;
          line-height: 1.5;
        }
      `}</style>
    </div>
  );
}
