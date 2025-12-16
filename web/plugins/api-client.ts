import { OpenAPI } from "@/client";
export default defineNuxtPlugin(() => {
    const isDev = import.meta.env.DEV;
    OpenAPI.BASE = isDev ? "http://localhost:8000" : "/api";
    OpenAPI.WITH_CREDENTIALS = true;
});
