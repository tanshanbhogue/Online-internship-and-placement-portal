// Contract: route /analytics (student).
//   * Fetches fresh numbers on every visit and whenever the tab becomes visible again (no stale dashboard).
//   * No attempts yet -> "Complete a test or practice session to see your analytics" , never a broken chart.
//   * Extra sections are AUTO-DISCOVERED: any file src/components/analytics/panels/*.panel.jsx whose default export is
//     { id, order, title, Component } is rendered between the summary and the recent attempts, and receives
//     { filters, refreshKey }. Story #27 adds its trend and strengths panels this way, so this file never changes.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getAnalyticsSummary } from "../api/analyticsApi.js";
import AnalyticsFilterBar, { DEFAULT_FILTERS } from "../components/analytics/AnalyticsFilterBar.jsx";
import PanelBoundary from "../components/analytics/PanelBoundary.jsx";
import RecentAttempts from "../components/analytics/RecentAttempts.jsx";
import SummaryCards from "../components/analytics/SummaryCards.jsx";
import StatusMessage from "../components/common/StatusMessage.jsx";
import "../styles/analytics.css";

const panelModules = import.meta.glob("../components/analytics/panels/*.panel.jsx", { eager: true });
const panels = Object.values(panelModules)
  .map((m) => m.default)
  .filter((p) => p && p.Component)
  .sort((a, b) => (a.order ?? 100) - (b.order ?? 100));

export default function AnalyticsDashboardPage() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [refreshKey, setRefreshKey] = useState(0);
  const [state, setState] = useState({ loading: true, error: "", summary: null });

  useEffect(() => {
    const onVisible = () => document.visibilityState === "visible" && setRefreshKey((k) => k + 1);
    document.addEventListener("visibilitychange", onVisible);
    return () => document.removeEventListener("visibilitychange", onVisible);
  }, []);

  const rangeInvalid = Boolean(filters.dateFrom && filters.dateTo && filters.dateFrom > filters.dateTo);

  useEffect(() => {
    if (rangeInvalid) return undefined;
    let cancelled = false;
    getAnalyticsSummary(filters)
      .then((summary) => !cancelled && setState({ loading: false, error: "", summary }))
      .catch((err) => !cancelled && setState({ loading: false, error: err.message || "Something went wrong", summary: null }));
    return () => {
      cancelled = true;
    };
  }, [filters, refreshKey, rangeInvalid]);

  const { loading, error, summary } = state;
  const filtered = filters.source !== "all" || filters.dateFrom || filters.dateTo;

  return (
    <div className="analytics-page">
      <h1>My Analytics</h1>
      <AnalyticsFilterBar filters={filters} onChange={setFilters} />
      {loading && <StatusMessage kind="loading" message="Loading your analytics..." />}
      {error && <StatusMessage kind="error" message={error} />}

      {summary && !summary.has_data && (
        <StatusMessage kind="empty" message={filtered ? "No attempts match these filters" : "Complete a test or practice session to see your analytics"}>
          <span className="row" style={{ justifyContent: "center", marginTop: "0.5rem" }}>
            <Link to="/practice">Start practising</Link>
            <Link to="/mock-tests">Take a mock test</Link>
          </span>
        </StatusMessage>
      )}

      {summary && summary.has_data && (
        <>
          <SummaryCards summary={summary} />
          {panels.map((panel) => (
            <PanelBoundary key={panel.id} title={panel.title}>
              <panel.Component filters={filters} refreshKey={refreshKey} />
            </PanelBoundary>
          ))}
          <RecentAttempts filters={filters} refreshKey={refreshKey} />
        </>
      )}
    </div>
  );
}
