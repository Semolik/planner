import { OpenAPI } from "@/client";
export default defineNuxtPlugin(() => {
    // Always run in client-only mode; configure API base for SPA served by nginx
    const isDev = import.meta.env.DEV;
    OpenAPI.BASE = isDev ? "http://localhost:8000" : "/api";
    OpenAPI.WITH_CREDENTIALS = true;
});
