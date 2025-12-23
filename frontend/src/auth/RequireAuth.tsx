import { Navigate } from "react-router-dom";
import { useAppSelector } from "../app/hooks";

type Props = {
  children: React.ReactNode;
};

export default function RequireAuth({ children }: Props) {
  const isAuth = useAppSelector((s) => s.auth.accessToken !== null);
  return isAuth ? <>{children}</> : <Navigate to="/login" replace />;
}
