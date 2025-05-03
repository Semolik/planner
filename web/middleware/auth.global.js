import { useAuthStore } from "~~/stores/auth";
export default defineNuxtRouteMiddleware(async (to, from) => {
    const authStore = useAuthStore();
    if (!authStore.logined) {
        try {
            await authStore.getUserData();
        } catch (e) {}
    }
});
