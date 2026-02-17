<template>
    <app-form full-height headline="Вход в личный кабинет" center-mobile>
        <login-form @logined="onLogin" />
    </app-form>
</template>
<script setup>
const onLogin = () => {
    const authStore = useAuthStore();
    const router = useRouter();

    const redirectUrl = authStore.redirectTo || "/";
    authStore.clearRedirectTo();

    router.push(redirectUrl);
};
</script>
