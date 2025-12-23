// src/router.tsx
import { createBrowserRouter } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Tags from "./pages/Tags";
import Folders from "./pages/Folders";
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
    element: (
      <RequireAuth>
        <AppLayout />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <Dashboard /> },
      { path: "tags", element: <Tags /> },
      { path: "folders", element: <Folders /> },
    ],
  },
]);
