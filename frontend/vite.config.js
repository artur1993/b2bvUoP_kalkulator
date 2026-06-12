import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5001",
        changeOrigin: true,
        secure: false,
      },
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./setupTests.js"],
    globals: true,
    coverage: {
      exclude: ["src/main.jsx"],
    },
    environmentOptions: {
      jsdom: {
        resources: "usable",
      },
    },
    threads: false,
  },
});
