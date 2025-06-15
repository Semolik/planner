<script setup>
import { useAuthStore } from "~/stores/auth";
import { AuthService } from "~/client";
const authStore = useAuthStore();
const codeVerifier = localStorage.getItem("core_verifier");
localStorage.removeItem("core_verifier");
const { $toast } = useNuxtApp();
if (codeVerifier) {
    const query = new URLSearchParams(window.location.search);
    await AuthService.vkCallbackAuthVkCallbackPost({
        code_verifier: codeVerifier,
        ...Object.fromEntries(query.entries()),
    })
        .then(async (response) => {
            await authStore.getUserData();
        })
        .catch((error) => {
            console.error("Ошибка авторизации:", error);
            $toast.error(HandleOpenApiError(error).message);
        })
        .finally(() => {
            const router = useRouter();
            router.push("/");
        });
}
</script>
<template></template>
