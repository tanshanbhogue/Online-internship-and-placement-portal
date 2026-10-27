

import { useState } from "react";
import { Link } from "react-router-dom";

import { registerStudent } from "../../api/registerApi.js";
import { isValidEmail, passwordProblems, requiredFields } from "../../utils/validators.js";

function FieldError({ id, message }) {
    return message ? (
        <p id={id} className="field-error" role="alert">
            {message}
        </p>
    ) : null;
}

export default function RegisterForm({ onSuccess, initialValues = {} }) {
    const [values, setValues] = useState({ name: "", email: "", password: "", college: "", batch: "", ...initialValues });
    const [errors, setErrors] = useState({});
    const [formError, setFormError] = useState("");
    const [submitting, setSubmitting] = useState(false);

    const set = (name) => (event) => setValues((v) => ({ ...v, [name]: event.target.value }));
    const hints = values.password ? passwordProblems(values.password) : [];

    function validate() {
        const found = requiredFields(values, ["name", "email", "password"]);
        if (!found.email && !isValidEmail(values.email)) found.email = "Enter a valid email address";
        if (!found.password) {
            const problems = passwordProblems(values.password);
            if (problems.length) found.password = problems[0];
        }
        return found;
    }

    async function handleSubmit(event) {
        event.preventDefault();
        setFormError("");
        const found = validate();
        setErrors(found);
        if (Object.keys(found).length) return;

        setSubmitting(true);
        try {
            const user = await registerStudent(values);
            setValues((v) => ({ ...v, password: "" })); // never keep the password around
            onSuccess?.(user);
        } catch (err) {
            if (err.code === "duplicate_email") {
                setErrors({ email: "Email already exists" });
            } else if (err.status === 422 && err.fields && Object.keys(err.fields).length) {
                const mapped = {};
                for (const [field, messages] of Object.entries(err.fields)) mapped[field] = messages[0];
                setErrors(mapped);
            } else {
                setFormError(err.message || "Something went wrong");
            }
        } finally {
            setSubmitting(false);
        }
    }

    return (
        <form onSubmit={handleSubmit} noValidate>
            {formError && <p className="field-error" role="alert">{formError}</p>}

            <div className="field">
                <label htmlFor="reg-name">Name</label>
                <input id="reg-name" type="text" autoComplete="name" maxLength={100} value={values.name} onChange={set("name")}
                    aria-invalid={!!errors.name} aria-describedby={errors.name ? "reg-name-err" : undefined} />
                <FieldError id="reg-name-err" message={errors.name} />
            </div>

            <div className="field">
                <label htmlFor="reg-email">Email</label>
                <input id="reg-email" type="email" autoComplete="email" maxLength={254} value={values.email} onChange={set("email")}
                    aria-invalid={!!errors.email} aria-describedby={errors.email ? "reg-email-err" : undefined} />
                <FieldError id="reg-email-err" message={errors.email} />
                {errors.email === "Email already exists" && (
                    <p className="small">
                        Already registered? <Link to="/login">Log in instead</Link>
                    </p>
                )}
            </div>

            <div className="field">
                <label htmlFor="reg-password">Password</label>
                <input id="reg-password" type="password" autoComplete="new-password" maxLength={128} value={values.password}
                    onChange={set("password")} aria-invalid={!!errors.password}
                    aria-describedby={`reg-password-hint${errors.password ? " reg-password-err" : ""}`} />
                <FieldError id="reg-password-err" message={errors.password} />
                <div id="reg-password-hint" className="hint" aria-live="polite">
                    {values.password && hints.length === 0
                        ? "Password looks good"
                        : hints.length > 0
                            ? `Still needed: ${hints.map((h) => h.replace("Password must ", "")).join("; ")}`
                            : "At least 8 characters with a letter, a digit and a symbol"}
                </div>
            </div>

            <div className="field">
                <label htmlFor="reg-college">College (optional)</label>
                <input id="reg-college" type="text" maxLength={100} value={values.college} onChange={set("college")}
                    aria-invalid={!!errors.college} />
                <FieldError message={errors.college} />
            </div>

            <div className="field">
                <label htmlFor="reg-batch">Batch (optional)</label>
                <input id="reg-batch" type="text" maxLength={20} placeholder="e.g. 2026" value={values.batch} onChange={set("batch")}
                    aria-invalid={!!errors.batch} />
                <FieldError message={errors.batch} />
            </div>

            <button className="btn" type="submit" disabled={submitting}>
                {submitting ? "Creating account..." : "Create account"}
            </button>
        </form>
    );
}