import { useAuthStore } from "@/stores/auth";
import { storeToRefs } from "pinia";
import { routesNames } from "@typed-router";
export const useAuthMiddleware = async (context, userRole) => {
    const authStore = useAuthStore();
    const { logined } = storeToRefs(authStore);

    if (!logined.value) {
        await authStore.getUserData();
    }
    if (
        !logined.value ||
        (userRole &&
            !authStore.userData.roles.includes(userRole) &&
            !authStore.userData.is_superuser)
    ) {
        return navigateTo({ name: routesNames.login });
    }
};
