import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({
  plugins: [react()],
  define: {
    "import.meta.env.VITE_VERCEL_ANALYTICS": JSON.stringify(
      process.env.VERCEL === "1" ? "true" : "false",
    ),
  },
});
