import { useAppDispatch } from "../app/hooks";
import { logout } from "../auth/authSlice";
import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const handleLogout = () => {
    dispatch(logout());
    navigate("/login");
  };

  return (
    <nav className="flex items-center justify-between px-6 py-3 bg-white border-b">
      <h1 className="font-semibold text-lg">SyncMark</h1>

      <div className="flex gap-4 text-sm">
        <Link to="/">Bookmarks</Link>
        <Link to="/tags">Tags</Link>
        <Link to="/folders">Folders</Link>

        <button onClick={handleLogout} className="text-red-600">
          Logout
        </button>
      </div>
    </nav>
  );
}
