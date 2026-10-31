// Contract: <AnalyticsFilterBar filters onChange /> source (all / practice / mock) and date range.
import "../../styles/analytics.css";

export const DEFAULT_FILTERS = { source: "all", dateFrom: "", dateTo: "" };

export default function AnalyticsFilterBar({ filters, onChange }) {
  const set = (key) => (e) => onChange({ ...filters, [key]: e.target.value });
  const invalid = filters.dateFrom && filters.dateTo && filters.dateFrom > filters.dateTo;
  return (
    <form className="filters analytics-filters" onSubmit={(e) => e.preventDefault()} aria-label="Analytics filters">
      <div className="field">
        <label htmlFor="a-source">Attempts</label>
        <select id="a-source" value={filters.source} onChange={set("source")}>
          <option value="all">Practice and mock tests</option>
          <option value="practice">Practice only</option>
          <option value="mock">Mock tests only</option>
        </select>
      </div>
      <div className="field">
        <label htmlFor="a-from">From</label>
        <input id="a-from" type="date" value={filters.dateFrom} max={filters.dateTo || undefined} onChange={set("dateFrom")} />
      </div>
      <div className="field">
        <label htmlFor="a-to">To</label>
        <input id="a-to" type="date" value={filters.dateTo} min={filters.dateFrom || undefined} onChange={set("dateTo")} aria-invalid={invalid ? "true" : undefined} />
        {invalid && <p className="field-error">The end date must not be before the start date.</p>}
      </div>
      <div className="field analytics-reset">
        <button type="button" className="btn btn-secondary btn-small" onClick={() => onChange(DEFAULT_FILTERS)}>Reset filters</button>
      </div>
    </form>
  );
}
