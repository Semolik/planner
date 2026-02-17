import { useAuthStore } from "~~/stores/auth";
import { routesNames } from "@typed-router";
export default defineNuxtRouteMiddleware(async (to, from) => {
    const authStore = useAuthStore();
    if (!authStore.logined) {
        let error = await authStore.getUserData();
        if (error) {
            if (to.name !== "login") {
                authStore.setRedirectTo(to.fullPath);
                return navigateTo({ name: routesNames.login });
            }
        }
    }
});
