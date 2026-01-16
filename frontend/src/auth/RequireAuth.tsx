import { Navigate, Outlet } from "react-router-dom";
import { useGetMeQuery } from "../api/auth.api";

export default function RequireAuth() {
  const { data: user, isLoading, isError } = useGetMeQuery();

  if (isLoading) return null;

  if (isError || !user) return <Navigate to="/login" replace />;

  return <Outlet />;
}
