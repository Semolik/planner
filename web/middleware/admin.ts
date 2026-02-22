import { useAuthStore } from "@/stores/auth";
import { storeToRefs } from "pinia";
import { routesNames } from "@typed-router";

export default defineNuxtRouteMiddleware(async (context) => {
    const authStore = useAuthStore();
    const { logined, userData } = storeToRefs(authStore);
    try {
        await authStore.getUserData();
    } catch (e) {}
    if (!logined.value || !userData.value?.is_superuser) {
        return navigateTo({ name: routesNames.login });
    }
});

