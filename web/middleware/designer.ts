import { UserRole } from "@/client";

export default defineNuxtRouteMiddleware(async (context) => {
    return useAuthMiddleware(context, UserRole.DESIGNER);
});

