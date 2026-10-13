import { Analytics } from "@vercel/analytics/react";
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import ErrorBoundary from "./ErrorBoundary";
import { installTranslationGuard } from "./translationGuard";
import "@fontsource-variable/dm-sans";
import "./styles.css";

if (typeof Node !== "undefined") installTranslationGuard(Node.prototype);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
    {import.meta.env.VITE_VERCEL_ANALYTICS === "true" && <Analytics />}
  </React.StrictMode>,
);
