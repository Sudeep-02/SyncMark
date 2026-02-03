import { useEffect, useState } from "react";

export function useAuthStatus() {
  const [loading, setLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function checkAuth() {
      try {
        const res = await fetch("https://localhost:8000/auth/me", {
          credentials: "include",
        });

        if (!cancelled) {
          setIsLoggedIn(res.ok);
        }
      } catch {
        if (!cancelled) {
          setIsLoggedIn(false);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    checkAuth();

    return () => {
      cancelled = true;
    };
  }, []);

  return { loading, isLoggedIn };
}
