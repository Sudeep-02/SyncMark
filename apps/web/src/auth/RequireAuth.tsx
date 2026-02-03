import { Navigate, Outlet } from "react-router-dom";
import { useGetMeQuery } from "../api/auth.api";

export default function RequireAuth() {
  const { isLoading, isError } = useGetMeQuery();

  if (isLoading) return null;

  if (isError) return <Navigate to="/login" replace />;

  return <Outlet />;
}
