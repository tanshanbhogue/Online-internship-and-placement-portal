
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function isValidEmail(value) {
    return typeof value === "string" && value.length <= 254 && EMAIL_RE.test(value.trim());
}

// Mirrors backend app/core/security.py (UX only; the server is authoritative).
export function passwordProblems(value) {
    const password = value || "";
    const problems = [];
    if (password.length < 8) problems.push("Password must be at least 8 characters");
    if (password.length > 128) problems.push("Password must be at most 128 characters");
    if (!/\p{L}/u.test(password)) problems.push("Password must contain a letter");
    if (!/\p{Nd}/u.test(password)) problems.push("Password must contain a digit");
    if (!/[^\p{L}\p{N}\s]/u.test(password)) problems.push("Password must contain a symbol");
    return problems;
}

export function requiredFields(values, names) {
    const errors = {};
    for (const name of names) {
        const value = values?.[name];
        if (value === undefined || value === null || String(value).trim() === "") {
            errors[name] = "This field is required";
        }
    }
    return errors;
}
