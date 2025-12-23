import { useState } from "react";
import { useRegisterMutation } from "../api/auth.api";
import { useNavigate, Link } from "react-router-dom";

export default function Register() {
  const [register, { isLoading, error }] = useRegisterMutation();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [clientError, setClientError] = useState<string | null>(null);

  const submit = async () => {
    setClientError(null);

    if (password !== confirmPassword) {
      setClientError("Passwords do not match");
      return;
    }

    try {
      await register({ email, password }).unwrap();
      navigate("/login");
    } catch {
      // handled by RTK Query error
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-full max-w-sm bg-white p-6 rounded shadow">
        <h1 className="text-xl font-semibold mb-4">Create account</h1>

        <input
          className="w-full mb-3 p-2 border rounded"
          placeholder="Email"
          type="email"
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          className="w-full mb-3 p-2 border rounded"
          placeholder="Password"
          type="password"
          onChange={(e) => setPassword(e.target.value)}
        />

        <input
          className="w-full mb-3 p-2 border rounded"
          placeholder="Confirm Password"
          type="password"
          onChange={(e) => setConfirmPassword(e.target.value)}
        />

        {clientError && (
          <p className="text-red-500 text-sm mb-2">{clientError}</p>
        )}

        {error && (
          <p className="text-red-500 text-sm mb-2">Unable to create account</p>
        )}

        <button
          onClick={submit}
          disabled={isLoading}
          className="w-full bg-accent text-white p-2 rounded"
        >
          {isLoading ? "Creating..." : "Sign up"}
        </button>

        <p className="text-sm mt-3 text-center">
          Already have an account?{" "}
          <Link to="/login" className="text-accent">
            Login
          </Link>
        </p>
      </div>
    </div>
  );
}
