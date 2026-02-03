import { RouterProvider } from "react-router-dom";
import { router } from "./Router";
import { Toaster } from "@/components/ui/sonner";
import "./App.css";
function App() {
  return (
    <>
      <RouterProvider router={router} />
      <Toaster />
    </>
  );
}

export default App;
