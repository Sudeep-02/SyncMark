import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite"; // Tailwind v4 plugin

export default defineConfig({
  base: "./",
  plugins: [
    react(),
    tailwindcss(), // enables Tailwind v4 build
  ],
  build: {
    outDir: "../dist/popup",
    emptyOutDir: true,
  },
});
