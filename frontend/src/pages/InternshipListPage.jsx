

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { listInternships } from "../api/internshipApi.js";
import StatusMessage from "../components/common/StatusMessage.jsx";
import InternshipCard from "../components/internships/InternshipCard.jsx";
import InternshipFilters from "../components/internships/InternshipFilters.jsx";

const PAGE_SIZE = 12;

// Filters and the page number live in the URL so back/forward and shared links keep working.
function filtersFromParams(params) {
  const f = {};
  for (const key of ["q", "location", "domain"]) if (params.get(key)) f[key] = params.get(key);
  for (const key of ["min_stipend", "max_duration_months"]) if (params.get(key)) f[key] = Number(params.get(key));
  if (params.get("open_only") === "true") f.open_only = true;
  return f;
}

export default function InternshipListPage() {
  const [params, setParams] = useSearchParams();
  const filters = useMemo(() => filtersFromParams(params), [params]);
  const page = Math.max(1, Number(params.get("page")) || 1);
  const [state, setState] = useState({ loading: true, error: "", data: null });

  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: "" }));
    listInternships({ ...filters, page, page_size: PAGE_SIZE })
      .then((data) => !cancelled && setState({ loading: false, error: "", data }))
      .catch((err) => !cancelled && setState({ loading: false, error: err.message || "Something went wrong", data: null }));
    return () => {
      cancelled = true;
    };
  }, [filters, page]);

  function applyFilters(next) {
    const p = new URLSearchParams();
    Object.entries(next).forEach(([k, v]) => p.set(k, String(v)));
    setParams(p); // changing a filter returns to page 1
  }

  function goToPage(n) {
    const p = new URLSearchParams(params);
    p.set("page", String(n));
    setParams(p);
  }

  const hasFilters = Object.keys(filters).length > 0;
  const { loading, error, data } = state;
  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;

  return (
    <div>
      <h1>Internships</h1>
      <InternshipFilters values={filters} onChange={applyFilters} />

      {loading && <StatusMessage kind="loading" message="Loading internships..." />}
      {error && <StatusMessage kind="error" message={error} />}

      {data && data.items.length === 0 && !loading && (
        hasFilters ? (
          <StatusMessage kind="empty" message="No matching internships found">
            <button type="button" className="btn btn-secondary btn-small" onClick={() => applyFilters({})}>Reset filters</button>
          </StatusMessage>
        ) : (
          <StatusMessage kind="empty" message="No internships currently available." />
        )
      )}

      {data && data.items.length > 0 && (
        <>
          <p className="muted small" aria-live="polite">{data.total} {data.total === 1 ? "listing" : "listings"}</p>
          <div className="grid">
            {data.items.map((item) => <InternshipCard key={item.id} internship={item} />)}
          </div>
          {totalPages > 1 && (
            <nav className="row spread" style={{ marginTop: "1rem" }} aria-label="Pagination">
              <button type="button" className="btn btn-secondary" disabled={page <= 1} onClick={() => goToPage(page - 1)}>Previous</button>
              <span>Page {page} of {totalPages}</span>
              <button type="button" className="btn btn-secondary" disabled={page >= totalPages} onClick={() => goToPage(page + 1)}>Next</button>
            </nav>
          )}
        </>
      )}
    </div>
  );
}
