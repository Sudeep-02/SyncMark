import { createBrowserRouter } from "react-router-dom";
import Login from "./pages/login/Login";
import Register from "./pages/signup/Register";
import Dashboard from "./pages/dashboard/page";
import Tags from "./components/dashboard/Tags";
import Folders from "./components/dashboard/Folders";
import RequireAuth from "./auth/RequireAuth";
import AppLayout from "./layouts/AppLayout";

export const router = createBrowserRouter([
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/register",
    element: <Register />,
  },
  {
    path: "/",
    element: <RequireAuth />,

    children: [
      { index: true, element: <Dashboard /> },
      { path: "tags", element: <Tags /> },
      { path: "folders", element: <Folders /> },
    ],
  },
]);
