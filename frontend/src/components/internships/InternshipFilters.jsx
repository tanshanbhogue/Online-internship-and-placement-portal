import { useEffect, useRef, useState } from "react";

const EMPTY = { q: "", location: "", domain: "", min_stipend: "", max_duration_months: "", open_only: false };

// Only non-empty values leave this component.
export function cleanFilters(form) {
  const out = {};
  if (form.q && form.q.trim()) out.q = form.q.trim();
  if (form.location && form.location.trim()) out.location = form.location.trim();
  if (form.domain && form.domain.trim()) out.domain = form.domain.trim();
  if (form.min_stipend !== "" && form.min_stipend !== undefined) out.min_stipend = Number(form.min_stipend);
  if (form.max_duration_months !== "" && form.max_duration_months !== undefined) out.max_duration_months = Number(form.max_duration_months);
  if (form.open_only) out.open_only = true;
  return out;
}

export default function InternshipFilters({ values = {}, onChange }) {
  const [form, setForm] = useState({ ...EMPTY, ...values });
  const valuesKey = JSON.stringify(cleanFilters({ ...EMPTY, ...values }));
  const lastEmitted = useRef(valuesKey);

  // Follow changes made from outside (e.g. the page's "Reset filters" button or browser back).
  useEffect(() => {
    if (valuesKey !== JSON.stringify(cleanFilters(form))) setForm({ ...EMPTY, ...values });
    lastEmitted.current = valuesKey;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [valuesKey]);

  // Debounce (~300 ms) so typing does not fire a request per keystroke.
  useEffect(() => {
    const cleaned = cleanFilters(form);
    const key = JSON.stringify(cleaned);
    if (key === lastEmitted.current) return undefined;
    const timer = setTimeout(() => {
      lastEmitted.current = key;
      onChange(cleaned);
    }, 300);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form]);

  const set = (name) => (event) => setForm((f) => ({ ...f, [name]: event.target.value }));

  return (
    <form className="filters card" onSubmit={(e) => e.preventDefault()} aria-label="Filter internships">
      <div className="field">
        <label htmlFor="f-q">Search</label>
        <input id="f-q" type="search" placeholder="Title or company" value={form.q} onChange={set("q")} />
      </div>
      <div className="field">
        <label htmlFor="f-location">Location</label>
        <input id="f-location" type="text" list="f-location-list" placeholder="e.g. Bengaluru" value={form.location} onChange={set("location")} />
        <datalist id="f-location-list">
          <option value="Remote" /><option value="Bengaluru" /><option value="Pune" />
        </datalist>
      </div>
      <div className="field">
        <label htmlFor="f-domain">Domain</label>
        <input id="f-domain" type="text" list="f-domain-list" placeholder="e.g. Backend" value={form.domain} onChange={set("domain")} />
        <datalist id="f-domain-list">
          <option value="Backend" /><option value="Frontend" /><option value="Data Analytics" /><option value="QA" /><option value="DevOps" />
        </datalist>
      </div>
      <div className="field">
        <label htmlFor="f-stipend">Minimum stipend (Rs / month)</label>
        <input id="f-stipend" type="number" min="0" step="1000" value={form.min_stipend} onChange={set("min_stipend")} />
      </div>
      <div className="field">
        <label htmlFor="f-duration">Maximum duration (months)</label>
        <input id="f-duration" type="number" min="1" value={form.max_duration_months} onChange={set("max_duration_months")} />
      </div>
      <div className="field" style={{ justifyContent: "flex-end" }}>
        <label className="check">
          <input type="checkbox" checked={form.open_only} onChange={(e) => setForm((f) => ({ ...f, open_only: e.target.checked }))} />
          Open listings only
        </label>
        <button type="button" className="btn btn-secondary btn-small" onClick={() => { setForm({ ...EMPTY }); lastEmitted.current = "{}"; onChange({}); }}>
          Reset
        </button>
      </div>
    </form>
  );
}
