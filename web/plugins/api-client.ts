import { OpenAPI } from "@/client";
export default defineNuxtPlugin((nuxtApp) => {
    const runtimeConfig = useRuntimeConfig();
    if (import.meta.server) {
        const cookie = useCookie("fastapiusersauth");
        OpenAPI.HEADERS = {
            Cookie: `fastapiusersauth=${cookie.value}`,
        };
    }

    if (process.env.NODE_ENV === "development") {
        OpenAPI.BASE = "http://localhost:8000";
    } else {
        if (import.meta.server) {
            OpenAPI.BASE = "http://api:8000";
        } else {
            OpenAPI.BASE = `https://${runtimeConfig.public.apiBaseUrl}`;
        }
    }

    OpenAPI.WITH_CREDENTIALS = true;
});
