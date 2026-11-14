import { useState } from "react";

const blank = { title: "", company: "", description: "", eligibility: "", location: "", domain: "", stipend: "", duration: "", deadline: "", status: "active" };

function fromListing(l) {
    if (!l) return blank;
    return {
        title: l.title, company: l.company, description: l.description, eligibility: l.eligibility || "", location: l.location || "",
        domain: l.domain || "", stipend: l.stipend_per_month ?? "", duration: l.duration_months ?? "", deadline: l.deadline, status: l.status,
    };
}

function Err({ message }) {
    return message ? <p className="field-error" role="alert">{message}</p> : null;
}

/** onSubmit(payload) must return a promise; an ApiError's `fields` are mapped back onto the inputs. */
export default function InternshipForm({ initial, onSubmit, onCancel }) {
    const [s, setS] = useState(() => fromListing(initial));
    const [errors, setErrors] = useState({});
    const [formError, setFormError] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const set = (name) => (e) => setS((v) => ({ ...v, [name]: e.target.value }));

    function validate() {
        const found = {};
        if (!s.title.trim()) found.title = "This field is required";
        if (!s.company.trim()) found.company = "This field is required";
        if (!s.description.trim()) found.description = "This field is required";
        if (!s.deadline) found.deadline = "Choose a deadline";
        return found;
    }

    async function handleSubmit(event) {
        event.preventDefault();
        setFormError("");
        const found = validate();
        setErrors(found);
        if (Object.keys(found).length) return;
        const payload = {
            title: s.title, company: s.company, description: s.description, eligibility: s.eligibility, location: s.location, domain: s.domain,
            stipend_per_month: s.stipend === "" ? null : Number(s.stipend),
            duration_months: s.duration === "" ? null : Number(s.duration),
            deadline: s.deadline, status: s.status,
        };
        setSubmitting(true);
        try {
            await onSubmit(payload);
        } catch (err) {
            if (err.status === 422 && err.fields && Object.keys(err.fields).length) {
                const mapped = {};
                for (const [field, messages] of Object.entries(err.fields)) mapped[field] = messages[0];
                setErrors({ ...mapped, stipend: mapped.stipend_per_month, duration: mapped.duration_months });
            } else {
                setFormError(err.message || "Something went wrong");
            }
        } finally {
            setSubmitting(false);
        }
    }

    const input = (id, label, name, props = {}) => (
        <div className="field" style={{ flex: 1 }}>
            <label htmlFor={`if-${id}`}>{label}</label>
            <input id={`if-${id}`} value={s[name]} onChange={set(name)} aria-invalid={!!errors[name]} {...props} />
            <Err message={errors[name]} />
        </div>
    );

    return (
        <form className="card" onSubmit={handleSubmit} noValidate aria-label={initial ? "Edit internship" : "New internship"}>
            <h2>{initial ? "Edit internship" : "Add internship"}</h2>
            {formError && <Err message={formError} />}
            <div className="row">{input("title", "Title", "title", { maxLength: 150 })}{input("company", "Company", "company", { maxLength: 100 })}</div>
            <div className="field">
                <label htmlFor="if-description">Description</label>
                <textarea id="if-description" value={s.description} onChange={set("description")} maxLength={5000} aria-invalid={!!errors.description} />
                <Err message={errors.description} />
            </div>
            <div className="field">
                <label htmlFor="if-eligibility">Eligibility (optional)</label>
                <textarea id="if-eligibility" value={s.eligibility} onChange={set("eligibility")} maxLength={2000} />
                <Err message={errors.eligibility} />
            </div>
            <div className="row">{input("location", "Location", "location", { maxLength: 100 })}{input("domain", "Domain", "domain", { maxLength: 60 })}</div>
            <div className="row">
                {input("stipend", "Stipend per month", "stipend", { type: "number", min: 0 })}
                {input("duration", "Duration (months)", "duration", { type: "number", min: 1, max: 36 })}
                {input("deadline", "Application deadline", "deadline", { type: "date" })}
            </div>
            <div className="field">
                <label htmlFor="if-status">Status</label>
                <select id="if-status" value={s.status} onChange={set("status")}>
                    <option value="active">Active (visible to students)</option>
                    <option value="draft">Draft (hidden)</option>
                    <option value="inactive">Inactive (hidden)</option>
                </select>
            </div>
            <div className="row">
                <button type="submit" className="btn" disabled={submitting}>{submitting ? "Saving..." : "Save internship"}</button>
                <button type="button" className="btn btn-secondary" onClick={onCancel}>Cancel</button>
            </div>
        </form>
    );
}