// pages/Login.tsx
import { useLoginMutation } from "../api/auth.api";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [login, { isLoading }] = useLoginMutation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const submit = async () => {
    await login({ email, password }).unwrap();
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-full max-w-sm bg-white p-6 rounded shadow">
        <h1 className="text-xl font-semibold mb-4">Sign in</h1>

        <input
          className="w-full mb-3 p-2 border rounded"
          placeholder="Email"
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          className="w-full mb-3 p-2 border rounded"
          type="password"
          placeholder="Password"
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          onClick={submit}
          disabled={isLoading}
          className="w-full bg-accent text-white p-2 rounded"
        >
          {isLoading ? "Signing in..." : "Login"}
        </button>
      </div>
    </div>
  );
}
