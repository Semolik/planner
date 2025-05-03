import { UserRole } from "@/client";
import { useAuthStore } from "@/stores/auth";
import { storeToRefs } from "pinia";
import { routesNames } from "@typed-router";
export default defineNuxtRouteMiddleware(async (context) => {
    const authStore = useAuthStore();
    const { logined, userData } = storeToRefs(authStore);
    try {
        await authStore.getUserData();
    } catch (e) {}
    if (!logined.value || !authStore.roleEqualOrHigher(UserRole.ADMIN)) {
        return navigateTo({ name: routesNames.login });
    }
});
