
import { Link, useNavigate } from "react-router-dom";

import RegisterForm from "../components/auth/RegisterForm.jsx";

export default function RegisterPage() {
    const navigate = useNavigate();
    return (
        <div className="page-narrow card">
            <h1>Create your account</h1>
            <RegisterForm onSuccess={() => navigate("/login", { state: { registered: true } })} />
            <p className="small" style={{ marginTop: "1rem" }}>
                Already have an account? <Link to="/login">Log in</Link>
            </p>
        </div>
    );
}
