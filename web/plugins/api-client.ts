import { OpenAPI } from "@/client";
export default defineNuxtPlugin((nuxtApp) => {
    if (import.meta.server) {
        const cookie = useCookie("fastapiusersauth");
        OpenAPI.HEADERS = {
            Cookie: `fastapiusersauth=${cookie.value}`,
        };
    }

    OpenAPI.BASE =
        process.env.NODE_ENV === "development"
            ? "http://localhost:3000/api"
            : import.meta.server
              ? "http://api:8000"
              : "/api";

    OpenAPI.WITH_CREDENTIALS = true;
});
